"""Pydantic data model for the analysis result"""

from pydantic import BaseModel, Field


class CVAnalysis(BaseModel):
    """Data model for the complete analysis of a CV.

    The LLM is forced to return an instance of this class via
    ``with_structured_output``. Each ``Field(description=...)`` is sent to the
    model as part of the schema, so the descriptions are functional
    instructions — they are the contract the model must satisfy, not comments.
    """

    candidate_name: str = Field(
        description="Full name of the candidate, extracted from the CV."
    )

    years_of_experience: int = Field(
        description=(
            "Total number of years of relevant professional work experience, "
            "expressed as a single integer (round to the nearest year)."
        )
    )

    key_skills: list[str] = Field(
        description=(
            "A list of the 5 to 7 skills found in the CV that are most relevant "
            "to the target role. Prefer concrete, role-specific skills "
            "(tools, languages, technologies, methods) over generic ones."
        )
    )

    education: str = Field(
        description=(
            "The candidate's highest level of education together with their "
            "main field of specialization (e.g. 'MSc in Computer Science')."
        )
    )

    relevant_experience: str = Field(
        description=(
            "A short summary (2-4 sentences) of the experience that is most "
            "relevant to THIS specific role, not the candidate's entire history."
        )
    )

    strengths: list[str] = Field(
        description=(
            "A list of the candidate's 3 to 5 main strengths with respect to "
            "the target role, each phrased as a short, concrete statement."
        )
    )

    areas_for_improvement: list[str] = Field(
        description=(
            "A list of 2 to 4 areas or skills the candidate could realistically "
            "develop to better fit the role, framed constructively."
        )
    )

    fit_percentage: int = Field(
        ge=0,
        le=100,
        description=(
            "An integer from 0 to 100 expressing how well the candidate fits "
            "the role (0 = no fit at all, 100 = perfect fit)."
        ),
    )
