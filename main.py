import asyncio
import logging

from Agents.supervisorAgent import build_supervisor_agent


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("log-investigation")

# Hide unnecessary HTTP request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


# ============================================================
# MAIN
# ============================================================

async def main():

    supervisor = build_supervisor_agent()

    user_request = """
    Login is failing with HTTP 401.
    Investigate the logs.
    """

    logger.info("Starting investigation")
    logger.info("User request: %s", user_request.strip())

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

        # ====================================================
        # PRINT COMPLETE AGENT TRACE
        # ====================================================

        print("\n")
        print("=" * 70)
        print("LLM SEARCH / TOOL DECISIONS")
        print("=" * 70)

        for message in result["messages"]:

            # ================================================
            # LLM -> TOOL
            # ================================================

            tool_calls = getattr(message, "tool_calls", None)

            if tool_calls:

                for call in tool_calls:

                    tool_name = call.get("name", "unknown")
                    args = call.get("args", {})

                    print("\n")
                    print("-" * 70)
                    print(f"[LLM -> TOOL] {tool_name}")
                    print("-" * 70)

                    # ----------------------------------------
                    # GLOB
                    # ----------------------------------------

                    if tool_name == "glob":

                        print(
                            f"Pattern     : "
                            f"{args.get('pattern')}"
                        )

                        print(
                            f"Path        : "
                            f"{args.get('path')}"
                        )

                    # ----------------------------------------
                    # GREP
                    # ----------------------------------------

                    elif tool_name == "grep":

                        print(
                            f"Pattern     : "
                            f"{args.get('pattern')}"
                        )

                        print(
                            f"Path        : "
                            f"{args.get('path')}"
                        )

                        print(
                            f"Glob        : "
                            f"{args.get('glob')}"
                        )

                        print(
                            f"Output Mode : "
                            f"{args.get('output_mode')}"
                        )

                        print(
                            f"Max Count   : "
                            f"{args.get('max_count')}"
                        )

                        print()
                        print(
                            ">>> LLM GENERATED SEARCH KEYWORD: "
                            f"{args.get('pattern')}"
                        )

                    # ----------------------------------------
                    # READ FILE
                    # ----------------------------------------

                    elif tool_name == "read_file":

                        print(
                            f"Arguments   : {args}"
                        )

                    # ----------------------------------------
                    # OTHER TOOL
                    # ----------------------------------------

                    else:

                        print(
                            f"Arguments   : {args}"
                        )

            # ================================================
            # TOOL -> LLM
            # ================================================

            message_type = getattr(
                message,
                "type",
                None,
            )

            if message_type == "tool":

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

        # ====================================================
        # FINAL SUPERVISOR RESPONSE
        # ====================================================

        print("\n")
        print("=" * 70)
        print("SUPERVISOR RESPONSE")
        print("=" * 70)

        final_message = result["messages"][-1]

        print(final_message.content)

    except KeyboardInterrupt:

        print("\nInvestigation cancelled.")

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