"""
Semantic schema for structured LLM output.

This module defines the Pydantic model that enforces structured output
from the semantic_mapping node, ensuring the LLM provides all required
column mappings and currency information.
"""

from pydantic import BaseModel, Field


class SemanticSchema(BaseModel):
    """
    Structured output schema for semantic column mapping.

    This schema is used by the LLM to map German column names to their
    semantic English keys and identify the currency symbol.
    """

    amount_local_currency: str = Field(
        description="The exact column name that contains the amount in local currency (e.g., 'Betrag in Hauswährung')"
    )
    due_date: str = Field(
        description="The exact column name that contains the net due date (e.g., 'Nettofälligkeit')"
    )
    assignment: str = Field(
        description="The exact column name that contains the assignment/reference field (e.g., 'Zuordnung')"
    )
    posting_date: str = Field(
        description="The exact column name that contains the posting/booking date (e.g., 'Buchungsdatum')"
    )
    document_type: str = Field(
        description="The exact column name that contains the document type (e.g., 'Belegart')"
    )
    currency_column: str = Field(
        description="The exact column name that contains the currency code (e.g., 'Währung')"
    )
    currency_symbol: str = Field(
        description="The currency symbol derived from the currency code (e.g., '€' for EUR, '$' for USD, '£' for GBP)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "amount_local_currency": "Betrag in Hauswährung",
                "due_date": "Nettofälligkeit",
                "assignment": "Zuordnung",
                "posting_date": "Buchungsdatum",
                "document_type": "Belegart",
                "currency_column": "Währung",
                "currency_symbol": "€",
            }
        }
