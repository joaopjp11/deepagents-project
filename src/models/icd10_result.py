from pydantic import BaseModel, ValidationError, field_validator
from typing import Union, List
import json
import ast
import re

class ICD10Result(BaseModel):
    icd10_codes: List[str]
    confidence: Union[float, List[float]]
    notes: str
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        """
        Valida os valores de confiança.
        Aceita tanto um valor único quanto uma lista de valores.
        """
        if isinstance(v, (int, float)):
            # Valor único - verificar se está entre 0 e 1
            if not (0 <= v <= 1):
                raise ValueError("Confidence must be between 0 and 1")
            return v
        elif isinstance(v, list):
            # Lista de valores - verificar se todos estão entre 0 e 1
            if not all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in v):
                raise ValueError("All confidence values must be numbers between 0 and 1")
            return v
        else:
            raise ValueError("Confidence must be a number or list of numbers between 0 and 1")


def parse_icd10_result(raw_output: str):
    """
    Convert the model's response to the ICD10Result format,
    removing any potential markdown blocks and handling both single and multiple confidence values.
    """
    try:
        # Handle different input types
        if isinstance(raw_output, list):
            raw_output = "".join(str(x) for x in raw_output)
        
        # Check if it's a dictionary-like string (from LangChain format)
        if isinstance(raw_output, str) and raw_output.strip().startswith("{") and "'type':" in raw_output:
            try:
                # Parse as Python literal (handles single quotes)
                parsed_dict = ast.literal_eval(raw_output)
                if isinstance(parsed_dict, dict) and 'text' in parsed_dict:
                    raw_output = parsed_dict['text']
            except (ValueError, SyntaxError):
                # If parsing fails, continue with original string
                pass
        
        # Remove markdown blocks
        cleaned = raw_output.strip()
        
        # Remove various markdown formats
        markdown_patterns = [
            r'```json\s*',
            r'```\s*',
            r'`json\s*',
            r'`\s*'
        ]
        
        for pattern in markdown_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Handle escaped newlines and quotes
        cleaned = cleaned.replace('\\n', '\n').replace('\\"', '"')
        
        # Try to parse as JSON first
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to convert single quotes to double quotes
            # This is a simple approach - for more complex cases, use ast.literal_eval
            try:
                # Replace single quotes with double quotes for JSON compatibility
                json_compatible = cleaned.replace("'", '"')
                data = json.loads(json_compatible)
            except json.JSONDecodeError:
                # Last attempt: use ast.literal_eval for Python dict format
                try:
                    data = ast.literal_eval(cleaned)
                    if not isinstance(data, dict):
                        raise ValueError("Parsed data is not a dictionary")
                except (ValueError, SyntaxError) as e:
                    raise json.JSONDecodeError(f"Could not parse as JSON or Python dict: {str(e)}", cleaned, 0)
        
        # Validar estrutura básica
        required_fields = ["icd10_codes", "confidence", "notes"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Validar correspondência entre códigos e confidências (se confidence for lista)
        if isinstance(data["confidence"], list):
            if len(data["icd10_codes"]) != len(data["confidence"]):
                raise ValueError(
                    f"Mismatch between number of codes ({len(data['icd10_codes'])}) "
                    f"and confidence values ({len(data['confidence'])})"
                )
        
        # Criar e validar o modelo
        result = ICD10Result(**data)
        return result.model_dump()

    except json.JSONDecodeError as e:
        return {
            "error": f"Invalid JSON format: {str(e)}",
            "raw_output": raw_output
        }
    except ValidationError as e:
        return {
            "error": f"Validation error: {str(e)}",
            "raw_output": raw_output
        }
    except ValueError as e:
        return {
            "error": f"Data validation error: {str(e)}",
            "raw_output": raw_output
        }
    except Exception as e:
        return {
            "error": f"Unexpected error parsing response: {str(e)}",
            "raw_output": raw_output
        }