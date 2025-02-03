from typing import Any

from fastapi.exceptions import RequestValidationError
from pydantic import model_validator


class CustomCheckAtLeastOnePairValidator:
    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_key_value_pair_is_received(cls, data: Any) -> Any:
        if isinstance(data, dict):
            c = data.values()
            if not c:
                raise RequestValidationError(
                    "At least one {'key':'value'} pair is expected"
                )
            return data
