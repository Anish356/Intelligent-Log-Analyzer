from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents.middleware.summarization import SummarizationMiddleware

from langchain.agents.structured_output import ToolStrategy

from Models.model import model
from Tools.Jarvis import ask_jarvis
from Tools.evaluation import evaluate_faithfulness
from Agents.logAnalyserAgent import build_log_analyzer_agent
from Schema.supervisor_schema import SupervisorEvidenceBrief


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SUPERVISOR_PROMPT_PATH = (
    PROJECT_ROOT
    / "Prompts"
    / "supervisorPrompt.txt"
)

SKILLS_DIRECTORY = (
    PROJECT_ROOT
    / "Skills"
)

LOG_INCIDENT_SKILL_PATH = (
    SKILLS_DIRECTORY
    / "supervisor-log-investigator"
)


# ============================================================
# VALIDATE PROJECT FILES
# ============================================================

def validate_project_files() -> None:
    """
    Validate the Supervisor prompt and Skill files.
    """

    if not SUPERVISOR_PROMPT_PATH.is_file():
        raise FileNotFoundError(
            "Supervisor prompt file not found: "
            f"{SUPERVISOR_PROMPT_PATH}"
        )

    if not LOG_INCIDENT_SKILL_PATH.is_dir():
        raise FileNotFoundError(
            "Log investigation Skill directory not found: "
            f"{LOG_INCIDENT_SKILL_PATH}"
        )

    skill_file = LOG_INCIDENT_SKILL_PATH / "SKILL.md"

    if not skill_file.is_file():
        raise FileNotFoundError(
            f"SKILL.md not found: {skill_file}"
        )


# ============================================================
# LOAD SUPERVISOR PROMPT
# ============================================================

def load_supervisor_prompt() -> str:
    """
    Load the Supervisor Agent system prompt.
    """

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
    Build the Supervisor Agent.

    The Supervisor can:
    - Load the log-incident-investigation Skill
    - Discover log files
    - Search logs using dynamically generated grep patterns
    - Read bounded evidence
    - Summarize growing conversation context
    - Delegate evidence analysis to LogAnalyzer
    - Ask Jarvis for technical knowledge
    - Evaluate answer faithfulness
    - Return SupervisorEvidenceBrief
    """

    # --------------------------------------------------------
    # VALIDATE FILES
    # --------------------------------------------------------

    validate_project_files()


    # --------------------------------------------------------
    # LOAD SUPERVISOR PROMPT
    # --------------------------------------------------------

    supervisor_prompt = load_supervisor_prompt()


    # --------------------------------------------------------
    # FILESYSTEM BACKEND
    # --------------------------------------------------------
    #
    # PROJECT_ROOT becomes the root exposed to the Deep Agent.
    #
    # For example:
    #
    # Physical path:
    # C:\...\Best_Practice\Skills\log-incident-investigation
    #
    # Agent virtual path:
    # /Skills/log-incident-investigation/
    #

    filesystem_backend = FilesystemBackend(
        root_dir=str(PROJECT_ROOT)
    )


    # --------------------------------------------------------
    # SUMMARIZATION MIDDLEWARE
    # --------------------------------------------------------

    summarization_middleware = SummarizationMiddleware(
        model=model,
        backend=filesystem_backend,

        # Begin compaction when accumulated context reaches
        # approximately 90,000 tokens.
        trigger=("tokens", 90000),

        # Keep the most recent 25,000 tokens after compaction.
        keep=("tokens", 25000),
    )


    # --------------------------------------------------------
    # BUILD LOG ANALYZER
    # --------------------------------------------------------

    log_analyzer_agent = build_log_analyzer_agent()


    # --------------------------------------------------------
    # LOG ANALYZER SUBAGENT
    # --------------------------------------------------------

    subagent_middleware = SubAgentMiddleware(
        backend=filesystem_backend,

        subagents=[
            {
                "name": "log-analyzer",

                "description": (
                    "Analyze numbered evidence blocks collected "
                    "by the Supervisor. Identify the first meaningful "
                    "failure, primary exception, exception chain, "
                    "affected components, correlation status, "
                    "evidence-grounded root-cause indicators, and "
                    "remaining evidence gaps. The subagent cannot "
                    "open or search source log files."
                ),

                "runnable": log_analyzer_agent,
            }
        ],
    )


    # --------------------------------------------------------
    # CREATE DEEP SUPERVISOR AGENT
    # --------------------------------------------------------

    supervisor = create_deep_agent(
        model=model,

        # Direct Supervisor tools
        tools=[
            ask_jarvis,
            evaluate_faithfulness,
        ],

        system_prompt=supervisor_prompt,

        # Loads Skills progressively when relevant.
        #
        # This path is relative to FilesystemBackend root_dir.
        skills=[
            "/Skills/log-incident-investigation/"
        ],

        backend=filesystem_backend,

        middleware=[
            summarization_middleware,
            subagent_middleware,
        ],

        response_format=ToolStrategy(
            SupervisorEvidenceBrief
        ),

        name="log-incident-supervisor",
    )

    return supervisor