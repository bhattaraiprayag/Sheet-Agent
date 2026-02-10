"""
Refactored LangGraph implementation for SheetAgent.

This module implements a deterministic 2-node architecture:
1. semantic_mapping: LLM identifies column mappings and currency
2. report_generator: Pure Python generates the A/R aging report

This replaces the previous non-deterministic planner loop with a linear, testable, and cost-efficient flow.
"""

import logging
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langsmith import traceable

from app.core.prompt_manager import PromptManager
from app.core.report_generator import create_ar_report
from app.dataset.dataloader import SheetProblem
from app.graph.state import GraphState
from app.utils.semantic_schema import SemanticSchema

logger = logging.getLogger(__name__)


@traceable(name="Semantic Mapping Node", run_type="chain")
def semantic_mapping_node(state: GraphState) -> dict[str, Any]:
    """
    Node 1: Semantic column mapping using LLM with structured output.

    This node leverages the LLM's semantic understanding capability to:
    1. Read the Excel column headers
    2. Map German column names to English semantic keys
    3. Detect the currency code and convert it to a symbol

    The LLM is constrained to return structured output matching the
    SemanticSchema, ensuring consistency.

    Args:
        state: Current graph state containing the problem and workbook path.

    Returns:
        Updated state with column_map and currency_symbol populated.
    """
    logger.info("Executing semantic_mapping_node")

    problem = state["problem"]
    workbook_path = problem.workbook_path

    try:
        # Read the Excel file to extract headers and sample data
        df = pd.read_excel(workbook_path)
        column_headers = df.columns.tolist()
        sample_row = df.iloc[0].to_dict() if len(df) > 0 else {}

        logger.info(f"Loaded {len(column_headers)} columns from Excel file")
        logger.debug(f"Column headers: {column_headers}")

        # Initialize the prompt manager
        prompt_manager = PromptManager()
        messages = prompt_manager.get_semantic_mapping_prompt(
            column_headers=column_headers, sample_row=sample_row
        )

        # Initialize the LLM with structured output
        from app.core.config import get_settings

        settings = get_settings()

        llm = ChatOpenAI(
            model="gpt-4o-mini",  # Fast and cost-efficient for structured extraction
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            temperature=0.0,  # Deterministic output
            timeout=60,
        )

        # Bind structured output schema
        structured_llm = llm.with_structured_output(SemanticSchema)

        # Call the LLM
        logger.info("Calling LLM for semantic column mapping")
        response: SemanticSchema = structured_llm.invoke(messages)

        # Extract the mapping from the structured response
        column_map = {
            "amount_local_currency": response.amount_local_currency,
            "due_date": response.due_date,
            "assignment": response.assignment,
            "posting_date": response.posting_date,
            "document_type": response.document_type,
            "currency_column": response.currency_column,
        }
        currency_symbol = response.currency_symbol

        logger.info(f"Successfully mapped columns: {column_map}")
        logger.info(f"Detected currency symbol: {currency_symbol}")

        # Create message log for tracing
        ai_message = AIMessage(
            content=f"Successfully mapped columns:\n{column_map}\n\nCurrency: {currency_symbol}"
        )

        return {
            "column_map": column_map,
            "currency_symbol": currency_symbol,
            "messages": [*state.get("messages", []), ai_message],
        }

    except Exception as e:
        logger.error("Error in semantic_mapping_node: %s", e)
        raise RuntimeError(f"Semantic mapping failed: {e}") from e


@traceable(name="Report Generator Node", run_type="chain")
def report_generator_node(state: GraphState) -> dict[str, Any]:
    """
    Node 2: Deterministic A/R Aging report generation.

    This node uses pure Python logic to:
    1. Identify cumulative rows using business rules
    2. Classify invoice and credit rows
    3. Calculate maturity clusters
    4. Generate the Analysis sheet with proper formatting

    No LLM calls are made in this node, ensuring deterministic,
    cost-efficient and testable output.

    Args:
        state: Current graph state with column_map and currency_symbol populated.

    Returns:
        Updated state with completion message.
    """
    logger.info("Executing report_generator_node")

    problem = state["problem"]
    output_dir = state["output_dir"]
    reporting_date = state["reporting_date"]
    column_map = state["column_map"]
    currency_symbol = state["currency_symbol"]

    if not column_map or not currency_symbol:
        raise ValueError("column_map and currency_symbol must be set by semantic_mapping_node")

    try:
        # Copy the input file to the output directory
        input_path = problem.workbook_path
        output_path = output_dir / "workbook_new.xlsx"

        logger.info(f"Copying input file to output: {input_path} -> {output_path}")
        shutil.copy(input_path, output_path)

        # Generate the A/R aging report
        logger.info("Generating A/R aging report")
        create_ar_report(
            input_path=input_path,
            output_path=output_path,
            reporting_date=reporting_date,
            column_map=column_map,
            currency_symbol=currency_symbol,
            hide_processed_sheet=True,  # Hide the detailed processed sheet
        )

        logger.info(f"Successfully generated report at: {output_path}")

        # Create completion message for tracing
        completion_message = AIMessage(
            content=f"Successfully generated A/R aging report with currency {currency_symbol}"
        )

        return {"messages": [*state.get("messages", []), completion_message]}

    except Exception as e:
        logger.error("Error in report_generator_node: %s", e)
        raise RuntimeError(f"Report generation failed: {e}") from e


def build_graph() -> StateGraph:
    """
    Builds and returns the StateGraph for the refactored
    2-node architecture.

    The graph flow is linear and deterministic:
    START → semantic_mapping → report_generator → END

    Returns:
        The compiled StateGraph.
    """
    graph = StateGraph(GraphState)

    # Add the two nodes
    graph.add_node("semantic_mapping", semantic_mapping_node)
    graph.add_node("report_generator", report_generator_node)

    # Define linear flow
    graph.set_entry_point("semantic_mapping")
    graph.add_edge("semantic_mapping", "report_generator")
    graph.add_edge("report_generator", END)

    return graph.compile()


def create_initial_state(
    problem: SheetProblem,
    output_dir: Path,
    reporting_date: str,
) -> GraphState:
    """
    Creates the initial state for the graph execution.

    Args:
        problem: The sheet problem to analyze.
        output_dir: The directory where output files will be saved.
        reporting_date: The date to use for maturity calculations (format: YYYY-MM-DD).

    Returns:
        The initial state for the graph execution.
    """
    initial_message = HumanMessage(
        content=f"Analyzing accounts receivable file: {problem.workbook_path}\n"
        f"Reporting date: {reporting_date}"
    )

    return {
        "problem": problem,
        "output_dir": output_dir,
        "reporting_date": reporting_date,
        "column_map": None,
        "currency_symbol": None,
        "messages": [initial_message],
    }


class SheetAgentGraph:
    """
    A simplified wrapper class for the refactored StateGraph.

    This class provides a clean interface for the analysis service to execute
    the 2-node deterministic workflow. It integrates with LangSmith for
    tracing both the LLM call and the pure Python processing.
    """

    def __init__(
        self,
        problem: SheetProblem,
        output_dir: Path,
        reporting_date: str = "2025-06-10",  # Default for testing
    ):
        """
        Initializes the SheetAgentGraph.

        Args:
            problem: The sheet problem to analyze.
            output_dir: The directory where output files will be saved.
            reporting_date: The date to use for maturity calculations.
                           Defaults to 2025-06-10 for testing purposes.
        """
        self.problem = problem
        self.output_dir = output_dir
        self.reporting_date = reporting_date

        # Build the graph
        self.graph = build_graph()
        logger.info("SheetAgentGraph initialized with 2-node architecture")

    @traceable(name="SheetAgent", run_type="chain")
    def run(self) -> dict[str, Any]:
        """
        Runs the graph with the initial state.

        This method is traced with LangSmith to provide monitoring and debugging
        capabilities for the entire workflow.

        Returns:
            The final state after graph execution.
        """
        logger.info("Starting SheetAgentGraph execution")

        # Create the initial state
        logger.info("Creating initial state")
        initial_state = create_initial_state(
            problem=self.problem, output_dir=self.output_dir, reporting_date=self.reporting_date
        )

        # Run the graph
        logger.info("Invoking graph")
        final_state = self.graph.invoke(initial_state)
        logger.info("Graph execution completed successfully")

        return final_state
