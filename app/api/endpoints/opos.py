import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.services.analysis_service import run_analysis

router = APIRouter()
PROMPT = """
Analyze an Accounts Receivable (A/R) open posts list containing unpaid invoices and credit notes.

## Overview
This endpoint generates a comprehensive aging report from your A/R data, automatically identifying
German column names and calculating maturity clusters for financial analysis.

## What the System Does

The analysis follows a deterministic 2-step process:

1. **Semantic Column Mapping**: Automatically identifies and maps German column names to their semantic
   meaning (e.g., "Betrag in Hauswährung" → amount, "Nettofälligkeit" → due date, "Währung" → currency).

2. **Report Generation**: Performs deterministic calculations to generate a comprehensive aging report
   including:
   - Identification of cumulative rows (summary/subtotal rows containing keywords like "Debitor" or matching running sums)
   - Classification of invoice rows (positive amounts) and credit rows (negative amounts)
   - Maturity calculations based on due date vs. reporting date
   - Clustering into age brackets: Not mature, 1-30 days, 31-60 days, >60 days
   - Sum totals and percentage breakdowns for both invoices and credits
   - Row number references for audit trails

## Output Format

The generated Excel file includes:
- **Original Sheet**: Your source data (unchanged)
- **Analysis Sheet**: Summary report with:
  - Total sum of invoice amounts
  - Total sum of credit amounts
  - Invoice aging breakdown by maturity cluster (amounts and percentages)
  - Credit aging breakdown by maturity cluster (amounts and percentages)
  - Lists of cumulative, invoice, and credit row numbers
- **Processed Sheet** (hidden): Intermediate calculations with row classifications

## Supported File Formats
- Excel files (.xlsx, .xls) with German or English column headers
- Currency detection for EUR (€), USD ($), GBP (£), CHF (Fr), JPY (¥)

## Notes
- The system uses deterministic business rules for accurate, reproducible results
- All monetary values are formatted with the appropriate currency symbol
- The reporting date defaults to 2025-06-10 for testing purposes
"""


class AnalysisRequest(BaseModel):
    """Request model for the analysis endpoint."""

    workbook_source: str = Field(
        "https://storage.googleapis.com/kritis-documents/Opos-test.xlsx",
        description="The URL or local file path of the workbook to analyze",
    )

    @field_validator("workbook_source")
    @classmethod
    def validate_workbook_source(cls, v: str) -> str:
        """Validate that the workbook source is either a valid URL or an existing local file path."""
        if not v:
            raise ValueError("Workbook source cannot be empty")

        # Check if it's a URL
        parsed = urlparse(v)
        if parsed.scheme in ("http", "https"):
            return v

        # Check if it's a local file path
        file_path = Path(v)
        if file_path.exists() and file_path.is_file():
            # Check if it's an Excel file
            if file_path.suffix.lower() not in [".xlsx", ".xls"]:
                raise ValueError("Local file must be an Excel file (.xlsx or .xls)")
            return str(file_path.resolve())

        raise ValueError(
            "Workbook source must be either a valid URL (http/https) or an existing local Excel file path"
        )

    @property
    def is_url(self) -> bool:
        """Check if the workbook source is a URL."""
        parsed = urlparse(self.workbook_source)
        return parsed.scheme in ("http", "https")

    @property
    def is_local_file(self) -> bool:
        """Check if the workbook source is a local file."""
        return not self.is_url


class AnalysisResponse(BaseModel):
    """Response model for the analysis endpoint."""

    analysis_file_url: str


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_workbook(request: AnalysisRequest):
    """
    Analyzes an Accounts Receivable (A/R) workbook and generates an aging report.

    This endpoint processes Excel files containing open posts lists (unpaid invoices
    and credits) using a deterministic 2-node architecture:

    1. **Semantic Mapping**: LLM identifies German column names and currency
    2. **Report Generation**: Deterministic Python calculates aging metrics

    The process includes:
    - Loading the workbook from URL or local file path
    - Automatically mapping German accounting columns to semantic keys
    - Identifying cumulative, invoice, and credit rows using business rules
    - Calculating maturity clusters (Not mature, 1-30, 31-60, >60 days)
    - Generating a formatted Analysis sheet with totals and percentages
    - In non-local environments, uploading the result to Google Cloud Storage

    All file operations are performed in secure temporary directories.

    Args:
        request: The analysis request containing:
            - workbook_source: URL or local file path to the Excel file

    Returns:
        AnalysisResponse containing:
        - In local environments: Success message with the local file path
        - In non-local environments: Public URL to the file in Google Cloud Storage

    Raises:
        HTTPException: If an error occurs during analysis (e.g., invalid file format,
                      missing columns, processing errors).

    Example:
        ```python
        response = await analyze_workbook(AnalysisRequest(
            workbook_source="https://example.com/opos.xlsx"
        ))
        # Returns: {"analysis_file_url": "https://storage.googleapis.com/..."}
        ```
    """
    try:
        result_url = run_analysis(
            workbook_source=request.workbook_source,
            is_local_file=request.is_local_file,
            reporting_date=datetime.now().strftime(
                "%Y-%m-%d"
            ),  # If unused, reporting date defaults to 2025-06-10 for testing purposes
        )
        return {"analysis_file_url": result_url}
    except Exception as e:
        logging.exception("Error during analysis")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}") from e
