from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

from Models.model import model
from Schema.log_analyzer_schema import LogAnalysis


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_ANALYZER_PROMPT_PATH = (
    PROJECT_ROOT
    / "Prompts"
    / "logAnalyserPrompt.txt"
)


# ============================================================
# LOAD PROMPT
# ============================================================

def load_log_analyzer_prompt() -> str:
    """
    Load the Log Analyzer system prompt.
    """

    if not LOG_ANALYZER_PROMPT_PATH.is_file():
        raise FileNotFoundError(
            "Log Analyzer prompt file was not found: "
            f"{LOG_ANALYZER_PROMPT_PATH}"
        )

    prompt = LOG_ANALYZER_PROMPT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    if not prompt:
        raise ValueError(
            "Log Analyzer prompt file is empty: "
            f"{LOG_ANALYZER_PROMPT_PATH}"
        )

    return prompt


# ============================================================
# BUILD LOG ANALYZER AGENT
# ============================================================

def build_log_analyzer_agent() -> Any:
    """
    Build the Log Analyzer Agent.

    The Log Analyzer:
    - Receives exact log evidence from the Supervisor.
    - Does not search files.
    - Does not call external tools.
    - Does not perform remediation.
    - Returns structured LogAnalysis output.
    """

    prompt = load_log_analyzer_prompt()

    log_analyzer = create_agent(
        model=model,

        # LogAnalyzer intentionally has no tools.
        # Evidence must come from the Supervisor.
        tools=[],

        system_prompt=prompt,

        # Force structured output matching
        # Schema/log_analyzer_schema.py
        response_format=ToolStrategy(
            LogAnalysis
        ),
    )

    return log_analyzer