import os

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

JARVIS_ASK_URL = os.getenv(
    "JARVIS_ASK_URL",
    "http://127.0.0.1:8000/ask",
)

JARVIS_CONNECT_TIMEOUT = float(
    os.getenv(
        "JARVIS_CONNECT_TIMEOUT",
        "10",
    )
)

# None means wait indefinitely for the FastAPI /ask endpoint
# to finish generating the response.
JARVIS_READ_TIMEOUT = None

JARVIS_MAX_QUESTION_LENGTH = 800


# ============================================================
# JARVIS TOOL
# ============================================================

@tool
def ask_jarvis(question: str) -> dict:
    """
    Query Ollie AI/Jarvis, OpenText's internal RAG-based technical
    knowledge system.

    Call this tool after the Log Analyzer has analyzed the relevant
    log evidence.

    Reframe the user's incident and relevant Log Analyzer findings
    into a focused technical question.

    Include useful technical context such as:
    - Product/component
    - User-reported problem
    - Relevant Log Analyzer findings
    - Error codes
    - HTTP status codes
    - Exception types
    - Error messages
    - Technical symptoms

    Use Ollie/Jarvis to retrieve relevant internal knowledge,
    including:
    - KB articles
    - Reference articles
    - Product documentation
    - Known issues
    - Known causes
    - Troubleshooting guidance
    - Documented fixes or workarounds

    Prefer analyzed technical findings instead of sending large
    amounts of raw log data.

    Do not send credentials, passwords, access tokens, secrets,
    API keys, or other authentication material.

    Ollie/Jarvis is a trusted internal knowledge source. Its
    documented explanations and recommendations may be used as
    supporting troubleshooting knowledge.

    However, do not present a documented possible cause as the
    confirmed cause of the current incident unless the supplied
    log evidence also supports that conclusion.
    """

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if not isinstance(question, str):
        return {
            "status": "error",
            "complete": False,
            "detail": "The Jarvis question must be a string.",
        }

    question = question.strip()

    if not question:
        return {
            "status": "error",
            "complete": False,
            "detail": "The Jarvis question is empty.",
        }

    if len(question) > JARVIS_MAX_QUESTION_LENGTH:
        return {
            "status": "error",
            "complete": False,
            "detail": (
                "The Jarvis question exceeds the maximum "
                f"length of {JARVIS_MAX_QUESTION_LENGTH} characters."
            ),
        }

    print(
        "\n[JARVIS] Request submitted.",
        flush=True,
    )

    print(
        "[JARVIS] Waiting for complete response...",
        flush=True,
    )

    # ========================================================
    # SEND REQUEST
    # ========================================================

    try:
        with requests.Session() as session:

            # Prevent HTTP_PROXY / HTTPS_PROXY environment
            # variables from affecting localhost requests.
            session.trust_env = False

            response = session.post(
                url=JARVIS_ASK_URL,
                json={
                    "prompt": question,
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=(
                    JARVIS_CONNECT_TIMEOUT,
                    JARVIS_READ_TIMEOUT,
                ),
                allow_redirects=True,
            )

    # ========================================================
    # CONNECTION TIMEOUT
    # ========================================================

    except requests.ConnectTimeout as exc:

        detail = (
            "Timed out while connecting to Jarvis. "
            f"{type(exc).__name__}: {exc}"
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "unavailable",
            "complete": False,
            "detail": detail,
        }

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except requests.ConnectionError as exc:

        detail = (
            f"Could not connect to {JARVIS_ASK_URL}. "
            f"{type(exc).__name__}: {exc}"
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "unavailable",
            "complete": False,
            "detail": detail,
        }

    # ========================================================
    # READ TIMEOUT
    # ========================================================

    except requests.ReadTimeout as exc:

        detail = (
            "Jarvis did not finish before the configured "
            "read timeout. "
            f"{type(exc).__name__}: {exc}"
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "unavailable",
            "complete": False,
            "detail": detail,
        }

    # ========================================================
    # OTHER REQUEST ERRORS
    # ========================================================

    except requests.RequestException as exc:

        detail = (
            "The Jarvis HTTP request failed. "
            f"{type(exc).__name__}: {exc}"
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "unavailable",
            "complete": False,
            "detail": detail,
        }

    # ========================================================
    # HTTP RESPONSE
    # ========================================================

    print(
        f"[JARVIS] HTTP response received: "
        f"{response.status_code}",
        flush=True,
    )

    if response.status_code != 200:

        response_preview = response.text[:1000].strip()

        known_errors = {
            409: (
                "Jarvis is currently processing "
                "another request."
            ),

            422: (
                "Jarvis rejected the request body. "
                "The /ask endpoint expects JSON containing "
                "the field 'prompt'."
            ),

            502: (
                "Jarvis could not complete the browser "
                "operation."
            ),

            503: (
                "Jarvis is not ready. Check the browser "
                "and Jarvis FastAPI service."
            ),

            504: (
                "The Jarvis API timed out while waiting "
                "for the browser operation."
            ),
        }

        detail = known_errors.get(
            response.status_code,
            (
                f"Jarvis returned HTTP "
                f"{response.status_code}. "
                f"Response: {response_preview}"
            ),
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "unavailable",
            "complete": False,
            "http_status": response.status_code,
            "detail": detail,
            "response_preview": response_preview,
        }

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:
        data = response.json()

    except ValueError as exc:

        detail = (
            "Jarvis returned invalid JSON. "
            f"{type(exc).__name__}: {exc}"
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "error",
            "complete": False,
            "detail": detail,
            "response_preview": (
                response.text[:1000].strip()
            ),
        }

    # ========================================================
    # VALIDATE JSON
    # ========================================================

    if not isinstance(data, dict):

        detail = (
            "Jarvis returned an unexpected JSON type: "
            f"{type(data).__name__}."
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "error",
            "complete": False,
            "detail": detail,
        }

    # ========================================================
    # EXTRACT RESPONSE
    # ========================================================

    answer = data.get("answer")
    complete = data.get("complete")

    if not isinstance(answer, str) or not answer.strip():

        detail = (
            "Jarvis returned no valid answer text. "
            f"Available fields: {list(data.keys())}"
        )

        print(
            f"[JARVIS] {detail}",
            flush=True,
        )

        return {
            "status": "error",
            "complete": False,
            "detail": detail,
        }

    answer = answer.strip()

    # ========================================================
    # COMPLETE RESPONSE
    # ========================================================

    if complete is True:

        print(
            "[JARVIS] Complete answer received.",
            flush=True,
        )

        return {
            "status": "ok",
            "complete": True,
            "answer": answer,
        }

    # ========================================================
    # PARTIAL RESPONSE
    # ========================================================

    detail = (
        "The /ask endpoint returned complete=false. "
        "The server returned an answer before marking "
        "the response complete."
    )

    print(
        f"[JARVIS] {detail}",
        flush=True,
    )

    return {
        "status": "partial",
        "complete": False,
        "answer": answer,
        "detail": detail,
    }