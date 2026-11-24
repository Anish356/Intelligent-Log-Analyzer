import asyncio

from langchain_core.tools import tool

from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import Faithfulness
from ragas.llms import LangchainLLMWrapper

from Models.model import model


# ============================================================
# RAGAS LLM JUDGE
# ============================================================

judge_llm = LangchainLLMWrapper(model)

faithfulness_metric = Faithfulness(
    llm=judge_llm,
)


# ============================================================
# EVALUATION TOOL
# ============================================================

@tool
async def evaluate_faithfulness(
    user_input: str,
    response: str,
    retrieved_contexts: list[str],
) -> dict:
    """
    Evaluate whether the LogAnalyzer response is faithful to
    the exact log evidence supplied to it.

    Args:
        user_input:
            Original incident/log investigation request.

        response:
            LogAnalyzer response that needs to be evaluated.

        retrieved_contexts:
            Exact log excerpts used by LogAnalyzer.

    Returns:
        Faithfulness evaluation result.
    """

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not isinstance(user_input, str) or not user_input.strip():
        return {
            "status": "error",
            "metric": "faithfulness",
            "detail": "User input is empty.",
        }

    if not isinstance(response, str) or not response.strip():
        return {
            "status": "error",
            "metric": "faithfulness",
            "detail": "LogAnalyzer response is empty.",
        }

    if not retrieved_contexts:
        return {
            "status": "error",
            "metric": "faithfulness",
            "detail": "No log evidence was supplied.",
        }

    # --------------------------------------------------------
    # RAGAS FAITHFULNESS
    # --------------------------------------------------------

    try:

        sample = SingleTurnSample(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts,
        )

        score = await faithfulness_metric.single_turn_ascore(
            sample
        )

        score = float(score)

        return {
            "status": "ok",
            "metric": "faithfulness",
            "evaluation_method": "RAGAS",
            "score": round(score, 4),
            "percentage": round(score * 100, 2),
        }

    except Exception as exc:

        return {
            "status": "error",
            "metric": "faithfulness",
            "evaluation_method": "RAGAS",
            "detail": f"{type(exc).__name__}: {exc}",
        }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    async def test():

        test_input = {
            "user_input": (
                "Login is failing with HTTP 401. "
                "Investigate the logs."
            ),

            "response": (
                "The logs show an HTTP 401 authentication failure "
                "with error code E_GENERAL_AUTHENTICATION_ERROR. "
                "An AuthenticationCredentialsNotFoundException "
                "was also recorded."
            ),

            "retrieved_contexts": [
                (
                    "Evidence 1: "
                    "2026-10-23 07:21:34.844 [WARN] "
                    "Status: 401, "
                    "code: E_GENERAL_AUTHENTICATION_ERROR, "
                    "message: Authentication failed."
                ),
                (
                    "Evidence 2: "
                    "org.springframework.security.authentication."
                    "AuthenticationCredentialsNotFoundException: "
                    "An Authentication object was not found "
                    "in the SecurityContext."
                ),
            ],
        }

        print(
            "\n========== RAGAS FAITHFULNESS TEST ==========\n"
        )

        result = await evaluate_faithfulness.ainvoke(
            test_input
        )

        print(result)


    asyncio.run(test())