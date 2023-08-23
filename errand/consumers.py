from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
from .errand import run_errand, continue_errand
import asyncio
import json
from django.core.cache import cache


class ErrandConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.previously = []
        self.instruction = ""
        print("Websocket connection initiated")
        await self.send(
            {
                "type": "websocket.accept",
            }
        )

    async def websocket_disconnect(self, event):
        # cache_backend.delete('my_key')
        cache.delete(self.channel_name)
        self.send({"type": "websocket.disconnect"})

    async def websocket_receive(self, event):
        print(event)
        # receive the instruction here
        # load the json to extract the instruction
        data = json.loads(event["text"])
        if data["type"] == "instruction":
            self.instruction = data["instruction"]
            print(f"channel name is {self.channel_name}")
            print(f"instruction is {self.instruction}")
            await run_errand(self.instruction, self.channel_name)
        elif data["type"] == "result":
            # retreive the last action result dict object
            obj = self.previously[-1]
            obj["result"] = data["result"]
            self.previously[-1] = obj
            await continue_errand(self.instruction, self.channel_name, self.previously)
        elif data["type"] == "finish":
            self.previously = []

        # await self.send({"type": "websocket.send", "text": event["text"]})

    # send instruction from agent to vscode instance
    async def send_instruction(self, event):
        text = event["text"]
        data = json.loads(text)
        self.previously.append({"action": data["action"], "result": ""})
        del data["action"]
        # send message to the websocket
        await self.send({"type": "websocket.send", "text": json.dumps(data)})
