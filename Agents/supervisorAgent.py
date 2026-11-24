from pathlib import Path
from typing import Any

from deepagents.backends import StateBackend
from deepagents.middleware.subagents import SubAgentMiddleware

from langchain.agents import create_agent

from Models.model import model

from Tools.search import create_search_tool
from Tools.Jarvis import ask_jarvis

from Agents.logAnalyserAgent import build_log_analyzer_agent


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SUPERVISOR_PROMPT_PATH = (
    PROJECT_ROOT
    / "Prompts"
    / "supervisorPrompt.txt"
)


# ============================================================
# LOAD SUPERVISOR PROMPT
# ============================================================

def load_supervisor_prompt() -> str:
    """
    Load the Supervisor Agent system prompt.
    """

    if not SUPERVISOR_PROMPT_PATH.is_file():
        raise FileNotFoundError(
            f"Supervisor prompt file not found: "
            f"{SUPERVISOR_PROMPT_PATH}"
        )

    prompt = SUPERVISOR_PROMPT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    if not prompt:
        raise ValueError(
            f"Supervisor prompt file is empty: "
            f"{SUPERVISOR_PROMPT_PATH}"
        )

    return prompt


# ============================================================
# BUILD SUPERVISOR AGENT
# ============================================================

def build_supervisor_agent() -> Any:
    """
    Build the Supervisor Agent.

    Supervisor can:
    - Discover log files using glob
    - Search logs using grep
    - Read bounded evidence using read_file
    - Delegate analysis to LogAnalyzer
    - Ask Jarvis for sanitized troubleshooting and resolution guidance
    """

    # --------------------------------------------------------
    # LOAD SUPERVISOR PROMPT
    # --------------------------------------------------------

    supervisor_prompt = load_supervisor_prompt()

    # --------------------------------------------------------
    # FILESYSTEM MIDDLEWARE
    # --------------------------------------------------------

    filesystem_middleware = create_search_tool()

    # --------------------------------------------------------
    # BUILD LOG ANALYZER
    # --------------------------------------------------------

    log_analyzer_agent = build_log_analyzer_agent()

    # --------------------------------------------------------
    # LOG ANALYZER SUBAGENT
    # --------------------------------------------------------

    subagent_middleware = SubAgentMiddleware(
        backend=StateBackend(),
        subagents=[
            {
                "name": "log-analyzer",
                "description": (
                    "Analyze collected log evidence and return "
                    "structured evidence-grounded findings."
                ),
                "runnable": log_analyzer_agent,
            }
        ],
    )

    # --------------------------------------------------------
    # CREATE SUPERVISOR
    # --------------------------------------------------------

    supervisor = create_agent(
        model=model,

        # Direct Supervisor tools
        tools=[
            ask_jarvis,
        ],

        system_prompt=supervisor_prompt,

        middleware=[
            filesystem_middleware,
            subagent_middleware,
        ],
    )

    return supervisor