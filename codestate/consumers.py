from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
import asyncio
import json
from .state import State
import time


class StateConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.send(
            {
                "type": "websocket.accept",
            }
        )
        self.session_id = "AD123456ASE"
        self.state = State(self.session_id)

    async def websocket_disconnect(self, event):
        self.send({"type": "websocket.disconnect"})

    async def websocket_receive(self, event):
        # print(event)
        data = json.loads(event["text"])
        if data["command"] == "INITIALIZE":
            print("initializing")
            self.state.initialize(data["files"])
        elif data["command"] == "FILEOPEN":
            self.state.on_file_open(
                data["filePath"],
                data["fileExtension"],
                data["fileContent"],
            )
        elif data["command"] == "FILECLOSE":
            self.state.on_file_close(data["filePath"])

        elif data["command"] == "FILEMODIFY":
            self.state.on_file_modify(
                data["filePath"], data["fileExtension"], data["fileContent"]
            )
