from pydantic import Field
from langchain.tools.base import BaseTool
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


class AgentBaseTool(BaseTool):
    channel_name: str = Field(
        """
        The unique channel name the current vs code instance is connected to.
        you have been already been provided with this channel_name
        """
    )


async def receive_and_handle_messages(channel_name):
    channel_layer = get_channel_layer()
    result = ""
    message = await channel_layer.receive(channel_name)
    print(f"message type is {type(message)}")
    while True:
        if message["type"] == "websocket.disconnect":
            break
        else:
            # handle_message(message)
            data = json.loads(message["text"])
            if data["type"] == "result":
                result = data["result"]
                break
    return result


async def receive_message(channel_name):
    channel_layer = get_channel_layer()
    channel = await channel_layer.get_layer()
    async with channel.typing(channel_name):
        message = await channel.receive(channel_name)
        if message.get("type") == "websocket.receive":
            # Handle the received message here
            text_data = message.get("text")
            data = json.loads(text_data)
            print(data)
