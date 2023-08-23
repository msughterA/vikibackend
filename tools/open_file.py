from typing import Optional

from pydantic import Field, BaseModel

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from .base import AgentBaseTool, receive_and_handle_messages, receive_message
from typing import Any, Dict, List, Optional, Type
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import asyncio
from .constants import IDE_FEED_BACK_TIMEOUT
from django.core.cache import cache
import asyncio


class OpenFileArgsScehme(BaseModel):
    folder_dir: str = Field(
        description="""
        The folder path of the file you want to create
        example path/to/folder, ./ for root dir
        """
    )

    filename: str = Field(
        description="""
        The name of the file you want to open with its extentiion
        example main.py
        """
    )


class OpenFile(AgentBaseTool):
    """Tool that opens an existing file in the current vs code instance"""

    name: str = "openFile"
    result = ""
    description: str = """ 
        Use this tool to open a file an existing file in the vs code instance
        You must be make sure your opening the right file under the right folder
        """
    args_schema: Type[OpenFileArgsScehme] = OpenFileArgsScehme

    def __init__(
        self,
        channel_name,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self.channel_name = channel_name

    def _run(self, folder_dir: str, filename: str) -> str:
        raise NotImplementedError

    async def _arun(self, folder_dir: str, filename: str) -> str:
        """Run the tool."""
        data = {
            "command": self.name,
            "arguments": {"folderDir": folder_dir, "fileName": filename},
            "action": {
                "action": {
                    "action_input": {"folder_dir": folder_dir, "filename": filename}
                }
            },
        }

        sent = await self.send_data(data)

        return f"Command to Open the File {filename} under the folder {folder_dir} sent to vs code instance"

    async def send_data(self, data):
        channel_layer = get_channel_layer()
        result = await channel_layer.send(
            self.channel_name,
            {
                "type": "send.instruction",
                "text": json.dumps(data),
            },
        )

        return True
