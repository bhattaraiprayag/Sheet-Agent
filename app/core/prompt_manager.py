"""
Prompt manager module for SheetAgent.

This module provides a centralized class for managing prompt templates for the semantic_mapping node. It defines the system prompt that guides the LLM to identify column mappings and currency symbols.
"""

import os

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage


class PromptManager:
    """
    A class that centralizes the management of prompt templates for the semantic mapping task.

    This simplified version focuses solely on the semantic mapping task, which is the only point where the LLM is used in the refactored architecture.
    """

    # System prompt for semantic column mapping
    SEMANTIC_MAPPING_SYSTEM_PROMPT = """
You are an expert at analyzing Excel spreadsheets and identifying column structures.

Your task is to examine the column headers of a German accounts receivable (A/R) spreadsheet and map them to semantic English keys. You must also identify the currency being used.

## Required Column Mappings

You must identify the following columns by their exact names in the spreadsheet:

1. **amount_local_currency**: The column containing monetary amounts in local currency
   - Common German names: "Betrag in Hauswährung", "Betrag in Belegwährung", "Betrag"

2. **due_date**: The column containing the net due date for payments
   - Common German names: "Nettofälligkeit", "Fälligkeitsdatum", "Fälligkeit"

3. **assignment**: The column containing assignment or reference information
   - Common German names: "Zuordnung", "Referenz", "Zuordn."

4. **posting_date**: The column containing the posting or booking date
   - Common German names: "Buchungsdatum", "Belegdatum", "Datum"

5. **document_type**: The column containing the document type classification
   - Common German names: "Belegart", "Dokumenttyp", "Art"

6. **currency_column**: The column containing the currency code
   - Common German names: "Währung", "Wahrung", "Currency", "Wäh."

## Currency Symbol Detection

Based on the currency code found in the spreadsheet (e.g., EUR, USD, GBP), you must provide the corresponding currency symbol:
- EUR → €
- USD → $
- GBP → £
- CHF → Fr
- JPY → ¥

## Instructions

1. Carefully examine the column headers provided
2. Match each semantic key to its exact column name in the spreadsheet
3. Identify the currency code from sample data
4. Return a structured response with all mappings and the currency symbol

## Important Notes

- Column names may have slight variations in spacing or abbreviations
- If a column name is ambiguous, choose the most likely match based on common accounting practices
- The column names you provide must match EXACTLY as they appear in the spreadsheet (case-sensitive)
- If you cannot find a required column, make your best guess based on semantic similarity
"""

    SEMANTIC_MAPPING_USER_PROMPT = """
Please analyze this Excel spreadsheet and provide the column mappings and currency information.

## Column Headers:
{column_headers}

## Sample Row (to identify currency):
{sample_row}

Return your response as a structured JSON with the following fields:
- amount_local_currency: exact column name
- due_date: exact column name
- assignment: exact column name
- posting_date: exact column name
- document_type: exact column name
- currency_column: exact column name
- currency_symbol: the symbol (€, $, £, etc.)
"""

    def __init__(self):
        """
        Initialize the PromptManager.
        """
        self.prompt_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompt"
        )

    def get_semantic_mapping_prompt(
        self, column_headers: list[str], sample_row: dict[str, any]
    ) -> list[BaseMessage]:
        """
        Create the prompt messages for the semantic mapping task.

        Args:
            column_headers: List of column header names from the Excel file.
            sample_row: A dictionary representing a sample data row (to detect currency).

        Returns:
            A list of BaseMessage objects for the LLM.
        """
        # Format the column headers as a numbered list
        headers_str = "\n".join([f"{i + 1}. {header}" for i, header in enumerate(column_headers)])

        # Format the sample row as key-value pairs
        sample_str = "\n".join([f"- {key}: {value}" for key, value in sample_row.items()])

        user_content = self.SEMANTIC_MAPPING_USER_PROMPT.format(
            column_headers=headers_str, sample_row=sample_str
        )

        return [
            SystemMessage(content=self.SEMANTIC_MAPPING_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
