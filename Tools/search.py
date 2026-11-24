from pathlib import Path

from deepagents.backends import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemMiddleware


# ============================================================
# CONFIGURATION
# ============================================================

LOG_DIRECTORY = Path(
    r"C:\Users\ayadav3\Desktop\ML\Hackathon\test\logs"
)

GREP_MAX_COUNT = 20


# ============================================================
# FILESYSTEM SEARCH TOOL
# ============================================================

def create_search_tool() -> FilesystemMiddleware:
    """
    Create the filesystem middleware used by the supervisor
    for log discovery and searching.

    Available tools:
        - glob
        - grep
        - read_file

    The log directory is exposed to the agent as virtual root "/".
    """

    if not LOG_DIRECTORY.is_dir():
        raise FileNotFoundError(
            f"Logs folder not found: {LOG_DIRECTORY}"
        )

    backend = FilesystemBackend(
        root_dir=LOG_DIRECTORY,
        virtual_mode=True,
    )

    filesystem = FilesystemMiddleware(
        backend=backend,
        tools=[
            "glob",
            "grep",
            "read_file",
        ],
        grep_max_count=GREP_MAX_COUNT,

        # Keep filesystem results directly in agent context.
        # We can enable eviction later if needed.
        tool_token_limit_before_evict=None,
    )

    return filesystem