from pydantic import BaseModel, Field


class LogFinding(BaseModel):
    file: str = Field(
        description="Exact virtual file path from the evidence."
    )

    lines: str = Field(
        description=(
            "Exact line number or line range. "
            "Use Unknown when unavailable."
        )
    )

    timestamp: str = Field(
        description=(
            "Exact event timestamp. "
            "Use Unknown when unavailable."
        )
    )

    message: str = Field(
        description="Short factual description of the log event."
    )

    excerpt: str = Field(
        description=(
            "Relevant original log lines with secrets redacted."
        )
    )

    correlation_status: str = Field(
        description=(
            "Use VERIFIED, POTENTIALLY_RELATED, or UNCORRELATED."
        )
    )

    note: str | None = Field(
        default=None,
        description=(
            "Relevant context, evidence limitations, repetition, "
            "or correlation explanation."
        ),
    )


class LogAnalysis(BaseModel):
    findings: list[LogFinding] = Field(
        default_factory=list,
        max_length=5,
        description=(
            "Up to five findings supported by the supplied evidence."
        ),
    )