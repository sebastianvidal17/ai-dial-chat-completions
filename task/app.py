import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    deployment = "gpt-4o"
    client = DialClient(deployment)
    custom_client = CustomDialClient(deployment)
    conversation = Conversation()
    print("Provide System prompt or press 'enter' to continue.")
    sp = input("> ")
    sp = sp.strip() or DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=sp))
    while True:
        print("\nType your question or 'exit' to quit.")
        user = input("> ")
        if user.strip().lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break
        conversation.add_message(Message(role=Role.USER, content=user))
        if stream:
            ai_msg = await client.stream_completion(conversation.get_messages())
        else:
            ai_msg = client.get_completion(conversation.get_messages())
        conversation.add_message(ai_msg)


asyncio.run(
    start(True)
)
