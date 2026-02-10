"""
Analysis service for the refactored SheetAgent.

This module provides the main entry point for running A/R aging report analysis.
It has been simplified to work with the new 2-node deterministic architecture,
removing the need for sandbox and iterative planning loops.
"""

import logging
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from app.core.config import get_settings
from app.dataset.dataloader import load_problem
from app.graph.graph import SheetAgentGraph
from app.utils.gcs import upload_to_gcs

logger = logging.getLogger(__name__)


def run_analysis(
    workbook_source: str,
    is_local_file: bool = False,
    reporting_date: str | None = None,
) -> str:
    """
    Runs the A/R aging report analysis on the given workbook.

    This function orchestrates the entire analysis workflow using the refactored
    2-node architecture:
    1. semantic_mapping: LLM identifies column mappings and currency
    2. report_generator: Deterministic Python generates the report

    All file operations are executed within a secure temporary directory to prevent
    unauthorized file system access. The analysis process loads the workbook from
    either a URL or local file path, processes it, and generates an analysis file.

    In local environment, returns a success message with the local file path.
    In development and production environments, uploads the output file to
    Google Cloud Storage and returns the public URL.

    Args:
        workbook_source: The URL or local file path to the workbook file.
        is_local_file: Whether the workbook_source is a local file path.
        reporting_date: Optional reporting date for maturity calculations (YYYY-MM-DD).
                       Defaults to "2025-06-10" for testing if not provided.

    Returns:
        In local environment: A success message with the local file path.
        In non-local environments: The public URL of the uploaded analysis file in Google Cloud Storage.

    Raises:
        ValueError: If GCS_BUCKET_NAME environment variable is not set in non-local environments.
        Exception: For any errors during file processing or GCS upload.
    """
    source_type = "local file" if is_local_file else "URL"
    logger.info(f"Starting analysis for workbook from {source_type}: {workbook_source}")

    # Default to testing date if not provided
    if not reporting_date:
        reporting_date = "2025-06-10"
        logger.info(f"Using test reporting date: {reporting_date}")
    else:
        logger.info(f"Using reporting date: {reporting_date}")

    try:
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str).resolve()
            output_dir = temp_dir / "output"
            db_path = temp_dir / "db_path"

            # Ensure directories exist
            output_dir.mkdir(exist_ok=True)
            db_path.mkdir(exist_ok=True)

            logger.info(
                f"Created temporary directories: output_dir={output_dir}, db_path={db_path}"
            )

            unique_id = uuid.uuid4()
            local_workbook_path = output_dir / f"{unique_id}_workbook.xlsx"

            logger.info(f"Generated unique ID: {unique_id}")

            # Load the problem (downloads file if URL, copies if local)
            logger.info("Loading problem from workbook")
            problem = load_problem(
                workbook_path=local_workbook_path,
                db_path=db_path,
                workbook_source=workbook_source,
                is_local_file=is_local_file,
            )

            # Create the session output directory
            session_output_dir = output_dir / str(unique_id)
            session_output_dir.mkdir(exist_ok=True)
            logger.info(f"Created session output directory: {session_output_dir}")

            # Create and run the SheetAgentGraph with the new 2-node architecture
            logger.info("Creating SheetAgentGraph")
            agent_graph = SheetAgentGraph(
                problem=problem,
                output_dir=session_output_dir,
                reporting_date=reporting_date,
            )

            # Run the graph
            logger.info("Running SheetAgentGraph")
            agent_graph.run()
            logger.info("SheetAgentGraph execution completed")

            # The output file is saved as "workbook_new.xlsx" in the session's output directory
            output_file_path = session_output_dir / "workbook_new.xlsx"
            logger.info(f"Output file path: {output_file_path}")

            # Check if we're in local environment
            settings = get_settings()
            if settings.APP_ENVIRONMENT == "local":
                # In local environment, save to a persistent directory that can be mounted in Docker
                persistent_output_dir = (
                    Path("/app/sandbox/output")
                    if Path("/app/sandbox").exists()
                    else Path("./output")
                )
                persistent_output_dir.mkdir(parents=True, exist_ok=True)

                # Create a final output file path with timestamp for uniqueness
                final_output_path = (
                    persistent_output_dir
                    / f"{unique_id}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )

                # Copy the generated file to the persistent location
                if output_file_path.exists():
                    shutil.copy2(output_file_path, final_output_path)
                    logger.info(f"Analysis file saved to: {final_output_path}")
                    return f"Successfully generated analysis file to: {final_output_path}"
                else:
                    logger.error(f"Output file not found at: {output_file_path}")
                    raise FileNotFoundError(f"Output file not generated at: {output_file_path}")
            else:
                # Non-local environment: upload to GCS
                bucket_name = settings.GCS_BUCKET_NAME
                if not bucket_name:
                    logger.error("GCS_BUCKET_NAME environment variable is not set")
                    raise ValueError(
                        "GCS_BUCKET_NAME environment variable is not set but required in non-local environment"
                    )

                # Generate a unique name for the file in GCS
                destination_blob_name = f"analysis/{unique_id}_analysis.xlsx"

                # Upload the file to GCS and get the public URL
                logger.info(f"Uploading output file to GCS bucket: {bucket_name}")
                gcs_url = upload_to_gcs(output_file_path, bucket_name, destination_blob_name)
                logger.info(f"File uploaded successfully to GCS: {gcs_url}")
                return gcs_url
    except Exception as e:
        logger.exception(f"Error during analysis: {str(e)}")
        raise
