from dataclasses import dataclass


@dataclass
class LabError(Exception):
    stage: str
    message: str
    detail: str
    status_code: int = 400

    def __str__(self) -> str:
        return f"{self.message} ({self.detail})"

    def as_payload(self) -> dict[str, dict[str, str]]:
        return {
            "error": {
                "stage": self.stage,
                "message": self.message,
                "detail": self.detail,
            }
        }
