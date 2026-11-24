import asyncio
import logging

from Agents.supervisorAgent import build_supervisor_agent
from Schema.supervisor_schema import SupervisorEvidenceBrief


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("log-investigation")


# Hide unnecessary HTTP/model-client logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


# ============================================================
# TOOL CALL TRACE
# ============================================================

def print_tool_call(tool_name: str, args: dict) -> None:
    """
    Print the tool decision made by the Supervisor LLM.
    """

    print("\n")
    print("-" * 70)
    print(f"[LLM -> TOOL] {tool_name}")
    print("-" * 70)

    # --------------------------------------------------------
    # GLOB
    # --------------------------------------------------------

    if tool_name == "glob":

        print(f"Pattern     : {args.get('pattern')}")
        print(f"Path        : {args.get('path')}")

    # --------------------------------------------------------
    # GREP
    # --------------------------------------------------------

    elif tool_name == "grep":

        print(f"Pattern     : {args.get('pattern')}")
        print(f"Path        : {args.get('path')}")
        print(f"Glob        : {args.get('glob')}")
        print(f"Output Mode : {args.get('output_mode')}")
        print(f"Max Count   : {args.get('max_count')}")

        print(
            "\n>>> LLM GENERATED SEARCH KEYWORD:",
            args.get("pattern"),
        )

    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    elif tool_name == "read_file":

        print(f"File Path   : {args.get('file_path')}")
        print(f"Offset      : {args.get('offset')}")
        print(f"Limit       : {args.get('limit')}")

    # --------------------------------------------------------
    # LOG ANALYZER SUBAGENT
    # --------------------------------------------------------

    elif tool_name == "task":

        print(
            f"Subagent    : "
            f"{args.get('subagent_type')}"
        )

        print(
            f"Description : "
            f"{args.get('description')}"
        )

    # --------------------------------------------------------
    # JARVIS / OLLIE
    # --------------------------------------------------------

    elif tool_name == "ask_jarvis":

        print("Question:")
        print(args.get("question"))

    # --------------------------------------------------------
    # RAGAS FAITHFULNESS
    # --------------------------------------------------------

    elif tool_name == "evaluate_faithfulness":

        print(
            f"User Input  : "
            f"{args.get('user_input')}"
        )

        print("\nResponse:")
        print(args.get("response"))

        print("\nRetrieved Contexts:")

        contexts = args.get(
            "retrieved_contexts",
            [],
        )

        if isinstance(contexts, list):

            for index, context in enumerate(
                contexts,
                start=1,
            ):
                print(
                    f"\nEvidence Context {index}:"
                )
                print(context)

        else:

            # Useful for detecting wrong LLM argument shape
            print(contexts)

    # --------------------------------------------------------
    # OTHER TOOLS
    # --------------------------------------------------------

    else:

        print(f"Arguments   : {args}")


# ============================================================
# TOOL RESULT TRACE
# ============================================================

def print_tool_result(message) -> None:
    """
    Print the result returned from a tool to the Supervisor.
    """

    tool_name = getattr(
        message,
        "name",
        "unknown",
    )

    print("\n")
    print("-" * 70)
    print(f"[TOOL -> LLM] {tool_name}")
    print("-" * 70)

    print(message.content)


# ============================================================
# EXECUTION TRACE
# ============================================================

def print_execution_trace(result: dict) -> None:
    """
    Print observable Supervisor tool decisions and tool results.
    """

    print("\n")
    print("=" * 70)
    print("AGENT EXECUTION TRACE")
    print("=" * 70)

    messages = result.get(
        "messages",
        [],
    )

    for message in messages:

        # ----------------------------------------------------
        # LLM -> TOOL
        # ----------------------------------------------------

        tool_calls = getattr(
            message,
            "tool_calls",
            None,
        )

        if tool_calls:

            for call in tool_calls:

                tool_name = call.get(
                    "name",
                    "unknown",
                )

                args = call.get(
                    "args",
                    {},
                )

                print_tool_call(
                    tool_name,
                    args,
                )

        # ----------------------------------------------------
        # TOOL -> LLM
        # ----------------------------------------------------

        message_type = getattr(
            message,
            "type",
            None,
        )

        if message_type == "tool":

            print_tool_result(
                message
            )


# ============================================================
# STRUCTURED RESPONSE
# ============================================================

def print_structured_response(result: dict) -> None:
    """
    Print and validate the final SupervisorEvidenceBrief.
    """

    print("\n")
    print("=" * 70)
    print("STRUCTURED SUPERVISOR EVIDENCE BRIEF")
    print("=" * 70)

    structured_response = result.get(
        "structured_response"
    )

    # --------------------------------------------------------
    # NO STRUCTURED RESPONSE
    # --------------------------------------------------------

    if structured_response is None:

        print(
            "Supervisor completed without returning "
            "a structured response."
        )

        # Show final message as fallback
        messages = result.get(
            "messages",
            [],
        )

        if messages:

            final_message = messages[-1]

            content = getattr(
                final_message,
                "content",
                None,
            )

            if content:

                print("\nFinal message:")
                print(content)

        return

    # --------------------------------------------------------
    # VERIFY SCHEMA
    # --------------------------------------------------------

    print(
        "\nStructured response type:"
    )

    print(
        type(structured_response)
    )

    if not isinstance(
        structured_response,
        SupervisorEvidenceBrief,
    ):

        print(
            "\nWARNING: Structured response is not a "
            "SupervisorEvidenceBrief instance."
        )

    # --------------------------------------------------------
    # PRINT JSON
    # --------------------------------------------------------

    if hasattr(
        structured_response,
        "model_dump_json",
    ):

        print("\nJSON:")
        print(
            structured_response.model_dump_json(
                indent=2
            )
        )

    else:

        print(
            "\nStructured response:"
        )

        print(
            structured_response
        )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("\n")
    print("=" * 70)
    print("AI LOG INCIDENT INVESTIGATOR")
    print("=" * 70)

    # --------------------------------------------------------
    # BUILD SUPERVISOR
    # --------------------------------------------------------

    logger.info(
        "Building Supervisor Agent"
    )

    supervisor = build_supervisor_agent()

    # --------------------------------------------------------
    # TEST USER REQUEST
    # --------------------------------------------------------

    user_request = """
    which user is running the longest thread from 9:30pm  to 10:30 pm for all days  and  the longest  running query 
    Investigate the logs.
    """.strip()

    logger.info(
        "Starting investigation"
    )

    logger.info(
        "User request: %s",
        user_request,
    )

    # --------------------------------------------------------
    # RUN INVESTIGATION
    # --------------------------------------------------------

    try:

        result = await supervisor.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_request,
                    }
                ]
            }
        )

        # ----------------------------------------------------
        # DEBUG / OBSERVABILITY
        # ----------------------------------------------------

        print_execution_trace(
            result
        )

        # ----------------------------------------------------
        # FINAL STRUCTURED RESULT
        # ----------------------------------------------------

        print_structured_response(
            result
        )

    # --------------------------------------------------------
    # USER CANCELLED
    # --------------------------------------------------------

    except KeyboardInterrupt:

        print(
            "\nInvestigation cancelled."
        )

    # --------------------------------------------------------
    # FAILURE
    # --------------------------------------------------------

    except Exception as exc:

        logger.exception(
            "Investigation failed: %s: %s",
            type(exc).__name__,
            exc,
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())