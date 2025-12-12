from aidial_client import Dial, AsyncDial
import os

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        os.environ['DIAL_API_KEY'] = self._api_key
        self._client = Dial(base_url=DIAL_ENDPOINT, api_key=self._api_key)
        self._aclient = AsyncDial(base_url=DIAL_ENDPOINT, api_key=self._api_key)

    def get_completion(self, messages: list[Message]) -> Message:
        payload = [m.to_dict() for m in messages]
        resp = self._client.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=payload,
            stream=False,
        )
        if not resp.choices:
            raise Exception("No choices in response found")
        content = resp.choices[0].message.content or ""
        print(content)
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        payload = [m.to_dict() for m in messages]
        chunks = await self._aclient.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=payload,
            stream=True,
        )
        contents: list[str] = []
        async for chunk in chunks:
            delta = getattr(chunk.choices[0], 'delta', None)
            part = getattr(delta, 'content', '') if delta else ''
            if part:
                print(part, end="")
                contents.append(part)
        print()
        return Message(role=Role.AI, content="".join(contents))
