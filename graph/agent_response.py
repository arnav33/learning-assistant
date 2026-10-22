from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    detailed: str = Field(
        description=(
            "A structured detailed and relevent answer from an unstructured data. "
            "Include reference links to the source of the information."
        ),
    )
    compact: str = Field(
        description=(
            "A short and concise answer created from detailed field. "
            "Prefer single word over phrase and sentence. "
            "Prefer phrase over sentence. "
            "Prefer sentence over paragraph. "
            "Prefer paragraph over long text. "
            "Don't include reference links to the source of the information."
        ),
    )