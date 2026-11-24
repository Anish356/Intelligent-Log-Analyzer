from pydantic import BaseModel, Field

from Schema.log_analyzer_schema import LogFinding


class SearchCoverage(BaseModel):
    files_searched: list[str] = Field(
        default_factory=list,
        description="Virtual log file paths searched."
    )

    patterns_searched: list[str] = Field(
        default_factory=list,
        description="Patterns used while searching the log files."
    )

    no_match_searches: list[str] = Field(
        default_factory=list,
        description="Searches that returned no matches."
    )

    failed_searches: list[str] = Field(
        default_factory=list,
        description="Searches that failed."
    )

    truncated_searches: list[str] = Field(
        default_factory=list,
        description="Searches whose results were truncated."
    )

    match_limit: int = Field(
        default=20,
        description="Maximum grep matches returned per search."
    )

    limitations: list[str] = Field(
        default_factory=list,
        description="Other search coverage limitations."
    )


class OllieGuidance(BaseModel):
    status: str = Field(
        description=(
            "Ollie status such as ok, partial, "
            "error, unavailable, or not_called."
        )
    )

    complete: bool = Field(
        default=False,
        description="Whether Ollie returned a complete response."
    )

    answer: str | None = Field(
        default=None,
        description="Guidance returned by Ollie."
    )

    detail: str | None = Field(
        default=None,
        description="Exact error, partial, or availability detail."
    )


class FaithfulnessResult(BaseModel):
    status: str = Field(
        description="Evaluation status such as ok or error."
    )

    metric: str = Field(
        default="faithfulness",
        description="Evaluation metric name."
    )

    evaluation_method: str = Field(
        default="G-Eval-style LLM-as-judge",
        description="Method used for evaluation."
    )

    score: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Faithfulness score between 0 and 1."
    )

    percentage: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Faithfulness percentage."
    )

    total_claims: int | None = Field(
        default=None,
        ge=0,
    )

    supported_claims: int | None = Field(
        default=None,
        ge=0,
    )

    unsupported_claims: list[str] = Field(
        default_factory=list,
    )

    reasoning: str | None = None

    interpretation: str | None = None

    detail: str | None = Field(
        default=None,
        description="Exact failure detail when evaluation fails."
    )


class SupervisorEvidenceBrief(BaseModel):
    findings: list[LogFinding] = Field(
        default_factory=list,
        description="Evidence-grounded findings from LogAnalyzer."
    )

    logs_establish: list[str] = Field(
        default_factory=list,
        description="Facts directly established by log evidence."
    )

    uncertainties: list[str] = Field(
        default_factory=list,
        description=(
            "Things that cannot currently be established "
            "from the available evidence."
        )
    )

    search_coverage: SearchCoverage

    ollie_guidance: OllieGuidance

    faithfulness: FaithfulnessResult