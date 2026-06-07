"""Pydantic data model for the analysis result"""

from pydantic import BaseModel, Field


class CVAnalysis(BaseModel):
    """Data model for the complete analysis of a CV."""

    candidate_name: str = Field(
        description="Full name of the candidate, extracted from the CV."
    )

    # Your turn — add the remaining fields described below.
    # Hint: use list[str] for collections, int for numeric fields,
    # and constrain the fit_percentage to the 0-100 range with ge=0, le=100.
