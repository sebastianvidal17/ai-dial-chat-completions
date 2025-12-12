import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import API_KEY
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
        self._api_key = API_KEY

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {"api-key": self._api_key, "Content-Type": "application/json"}
        request_data = {"messages": [m.to_dict() for m in messages]}
        response = requests.post(self._endpoint, headers=headers, json=request_data, timeout=30)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise Exception("No choices in response found")
        content = choices[0]["message"]["content"] or ""
        print(content)
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {"api-key": self._api_key, "Content-Type": "application/json"}
        request_data = {"stream": True, "messages": [m.to_dict() for m in messages]}
        contents: list[str] = []
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, json=request_data, headers=headers) as resp:
                async for raw in resp.content:
                    line = raw.decode(errors="ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    snippet = self._get_content_snippet(line)
                    if snippet is None:
                        break
                    if snippet:
                        print(snippet, end="")
                        contents.append(snippet)
        print()
        return Message(role=Role.AI, content="".join(contents))

    def _get_content_snippet(self, line: str) -> str | None:
        prefix = "data: "
        if not line.startswith(prefix):
            return ""
        payload = line[len(prefix):]
        if payload.strip() == "[DONE]":
            return None
        try:
            obj = json.loads(payload)
        except Exception:
            return ""
        choices = obj.get("choices", [])
        if not choices:
            return ""
        delta = choices[0].get("delta", {})
        return delta.get("content", "")

