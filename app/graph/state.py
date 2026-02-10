"""
State definitions for the refactored SheetAgent LangGraph workflow.

This module defines the GraphState that flows through the 2-node architecture:
1. semantic_mapping: LLM identifies column mappings and currency
2. report_generator: Deterministic Python generates the A/R aging report
"""

from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from app.dataset.dataloader import SheetProblem


class GraphState(TypedDict):
    """
    Simplified state representation for the refactored LangGraph workflow.

    This state flows linearly through the semantic_mapping and report_generator
    nodes, eliminating the need for iterative planner loops.

    Attributes:
        problem: The sheet problem containing workbook path and instructions.
        output_dir: Directory where the final analysis file will be saved.
        reporting_date: The date to use for maturity calculations (format: YYYY-MM-DD).
        messages: Chat history for LangSmith tracing (auto-accumulated via add_messages).
        column_map: Mapping of semantic keys to actual Excel column names.
                   Populated by semantic_mapping node.
        currency_symbol: The currency symbol detected from the file (e.g., '€', '$').
                        Populated by semantic_mapping node.
    """

    # Input configuration
    problem: SheetProblem
    output_dir: Path
    reporting_date: str

    # Dynamic state (populated by semantic_mapping node)
    column_map: dict[str, str] | None
    currency_symbol: str | None

    # Message history for tracing (accumulated automatically)
    messages: Annotated[list[BaseMessage], add_messages]
