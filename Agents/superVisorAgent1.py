from pathlib import Path
from typing import Any

from deepagents.backends import StateBackend
from deepagents.middleware.subagents import SubAgentMiddleware

from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

from Models.model import model

from Tools.search import create_search_tool
from Tools.Jarvis import ask_jarvis
from Tools.evaluation import evaluate_faithfulness

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
    Load the Supervisor Agent system prompt from:

    Prompts/supervisorPrompt.txt
    """

    if not SUPERVISOR_PROMPT_PATH.is_file():
        raise FileNotFoundError(
            "Supervisor prompt file was not found: "
            f"{SUPERVISOR_PROMPT_PATH}"
        )

    prompt = SUPERVISOR_PROMPT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    if not prompt:
        raise ValueError(
            "Supervisor prompt file is empty: "
            f"{SUPERVISOR_PROMPT_PATH}"
        )

    return prompt


# ============================================================
# BUILD SUPERVISOR AGENT
# ============================================================

def build_supervisor_agent() -> Any:
    """
    Build and return the Supervisor Agent.

    The Supervisor can:

    - Track work using TodoListMiddleware
    - Discover logs using glob
    - Search logs using grep
    - Read bounded evidence using read_file
    - Delegate evidence analysis to LogAnalyzer
    - Ask Jarvis for sanitized troubleshooting guidance
    - Evaluate LogAnalyzer output using RAGAS Faithfulness
    """

    # --------------------------------------------------------
    # LOAD PROMPT
    # --------------------------------------------------------

    supervisor_prompt = load_supervisor_prompt()

    # --------------------------------------------------------
    # FILESYSTEM SEARCH MIDDLEWARE
    # --------------------------------------------------------

    filesystem_middleware = create_search_tool()

    # --------------------------------------------------------
    # LOG ANALYZER SUBAGENT
    # --------------------------------------------------------

    log_analyzer_agent = build_log_analyzer_agent()

    # --------------------------------------------------------
    # SUBAGENT MIDDLEWARE
    # --------------------------------------------------------

    subagent_middleware = SubAgentMiddleware(
        backend=StateBackend(),
        subagents=[
            {
                "name": "log-analyzer",
                "description": (
                    "Analyze exact numbered log excerpts and "
                    "return structured, evidence-grounded findings. "
                    "Use this subagent only after relevant log "
                    "evidence has been collected."
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
        tools=[
            ask_jarvis,
            evaluate_faithfulness,
        ],
        system_prompt=supervisor_prompt,
        middleware=[
            TodoListMiddleware(),
            filesystem_middleware,
            subagent_middleware,
        ],
    )

    return supervisor