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


class FinishArgsScehme(BaseModel):
    message: str = Field(
        description="""
        The finishing message you have to send.
        """
    )


class Finish(AgentBaseTool):
    """Tool that opens an existing file in the current vs code instance"""

    name: str = "finish"
    result = ""
    description: str = """ 
        Use this tool to tell the vs code instance you have been controlling
        that you have completed the task.
        when you want to stop executing the errand or task.
        use this tool if there is absolutely nothing left to do.
        """
    args_schema: Type[FinishArgsScehme] = FinishArgsScehme

    def __init__(
        self,
        channel_name,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self.channel_name = channel_name

    def _run(self) -> str:
        raise NotImplementedError

    async def _arun(self, message) -> str:
        """Run the tool."""
        data = {
            "command": self.name,
            "arguments": {"action": "Finish"},
            "action": f"{self.name}  execution",
        }

        sent = await self.send_data(data)
        return ""

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


# import faiss

# # create an index
# d = 64
# index = faiss.IndexFlatL2(d)

# # add some vectors
# xb = faiss.rand((100, d))
# index.add(xb)

# # update a vector
# new_vector = faiss.rand((1, d))
# index.replace(0, new_vector)

# # print the updated vector
# print(index.reconstruct(0))
