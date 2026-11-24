from langchain_core.tools import tool

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

    if not user_input.strip():
        return {
            "status": "error",
            "metric": "faithfulness",
            "detail": "User input is empty.",
        }

    if not response.strip():
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

    try:
        result = await faithfulness_metric.ascore(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts,
        )

        score = float(result.value)

        return {
            "status": "ok",
            "metric": "faithfulness",
            "evaluation_method": "RAGAS",
            "score": round(score, 4),
        }

    except Exception as exc:
        return {
            "status": "error",
            "metric": "faithfulness",
            "evaluation_method": "RAGAS",
            "detail": f"{type(exc).__name__}: {exc}",
        }