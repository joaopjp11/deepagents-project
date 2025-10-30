from pydantic import BaseModel, ValidationError
import json

class ICD10Result(BaseModel):
    icd10_codes: list[str]
    confidence: float
    notes: str


def parse_icd10_result(raw_output: str):
    """
    Convert the model's response to the ICD10Result format,
    removing any potential markdown blocks.
    """
    try:
        # Remove blocos Markdown tipo ```json ... ```
        cleaned = (
            raw_output.strip()
            .removeprefix("```json")
            .removesuffix("```")
            .strip()
        )

        data = json.loads(cleaned)
        return ICD10Result(**data).model_dump()

    except (json.JSONDecodeError, ValidationError) as e:
        return {
            "error": f"Failed to interpret structured response: {str(e)}",
            "raw_output": raw_output
        }