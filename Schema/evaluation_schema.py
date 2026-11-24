from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):

    status: str = Field(
        description="Execution status of the evaluation."
    )

    metric: str = Field(
        default="faithfulness"
    )

    evaluation_method: str = Field(
        default="RAGAS"
    )

    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="RAGAS faithfulness score."
    )

    passed: bool | None = Field(
        default=None,
        description=(
            "Whether the score passed the configured "
            "production threshold."
        )
    )

    threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
    )

    detail: str | None = Field(
        default=None,
        description="Evaluation error or diagnostic details."
    )