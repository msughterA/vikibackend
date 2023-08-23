""" These tool would be used to create files in vscode"""
from typing import Optional

from pydantic import Field, BaseModel

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from .base import AgentBaseTool
from typing import Any, Dict, List, Optional, Type
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


class CreateFileArgsSchema(BaseModel):
    folder_dir: str = Field(
        description="""
        The path to folder under which you want to create the file
        example path/to/folder
        """
    )
    filename: str = Field(
        description="""
        the name of the file you want to create with the file extension attached to it
        example models.ts
        """
    )


class CreateFile(AgentBaseTool):
    """Tool adds the capability to create files in vs code"""

    name: str = "createFile"
    description: str = (
        "Use this tool to create files under specific folders"
        "You must be certain the folder your creating the file under exists"
        "You must be certain the folder path is the right place the user wants to place the file"
    )
    args_schema: Type[CreateFileArgsSchema] = CreateFileArgsSchema

    def __init__(
        self,
        channel_name,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self.channel_name = channel_name

    def _run(self, folder_dir: str, filename: str) -> str:
        """Run the tool"""
        data = {
            "folderDir": folder_dir,
            "fileName": filename,
        }
        channel_layer = get_channel_layer()
        channel_layer.send(
            self.channel_name,
            {
                "type": "send.instruction",
                "text": json.dumps(data),
            },
        )

    async def _arun(self, folder_dir: str, filename: str, channel_name: str) -> str:
        """Run the tool."""
        data = {
            "command": self.name,
            "argmuments": {"folderDir": folder_dir, "fileName": filename},
        }
        channel_layer = get_channel_layer()
        await channel_layer.send(
            self.channel_name,
            {
                "type": "send.instruction",
                "text": json.dumps(data),
            },
        )

        # raise NotImplementedError
