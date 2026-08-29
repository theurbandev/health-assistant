import json
from pathlib import Path

from app.garmin.client import GarminDataAccess


def load_skill() -> str:
    path = Path(__file__).parents[1] / "skills" / "garmin-health" / "SKILL.md"
    return path.read_text(encoding="utf-8")


class AgentNotConfigured(RuntimeError):
    pass


class AgentRequestError(RuntimeError):
    pass


class HealthAgent:
    """Model-driven agent with one generic, read-only Garmin data capability."""

    def __init__(self, *, api_key: str | None, model: str, data_access: GarminDataAccess):
        self.api_key = api_key
        self.model = model
        self.data_access = data_access

    def answer(self, message: str) -> str:
        if not self.api_key:
            raise AgentNotConfigured("OPENAI_API_KEY is not configured")

        from openai import OpenAI, OpenAIError

        client = OpenAI(api_key=self.api_key)
        tools = [
            {
                "type": "function",
                "name": "get_garmin_data",
                "description": "Retrieve read-only data from the normalized Garmin cache.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string"},
                        "start": {"type": ["string", "null"]},
                        "end": {"type": ["string", "null"]},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    },
                    "required": ["endpoint"],
                    "additionalProperties": False,
                },
            }
        ]

        try:
            response = client.responses.create(
                model=self.model,
                instructions=load_skill(),
                input=message,
                tools=tools,
            )

            for _ in range(5):
                calls = [
                    item for item in response.output if getattr(item, "type", None) == "function_call"
                ]
                if not calls:
                    return response.output_text

                outputs = []
                for call in calls:
                    arguments = json.loads(call.arguments)
                    result = self.data_access.get_data(**arguments)
                    outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call.call_id,
                            "output": json.dumps(result),
                        }
                    )

                response = client.responses.create(
                    model=self.model,
                    instructions=load_skill(),
                    input=[*response.output, *outputs],
                    tools=tools,
                )
        except OpenAIError as exc:
            raise AgentRequestError("The model provider request failed") from exc

        raise RuntimeError("Model exceeded the maximum number of Garmin data requests")
