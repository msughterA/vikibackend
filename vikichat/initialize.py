"""Load agent."""
from typing import Any, Optional, Sequence

from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.tools.base import BaseTool
from .base import VikiChatAgent


def initialize_viki_chat_agent(
    tools: Sequence[BaseTool],
    llm: BaseLanguageModel,
    callback_manager: Optional[BaseCallbackManager] = None,
    agent_kwargs: Optional[dict] = None,
    **kwargs: Any,
) -> AgentExecutor:
    """Load an agent executor given tools and LLM.

    Args:
        tools: List of tools this agent has access to.
        llm: Language model to use as the agent.
        agent: Agent type to use. If None and agent_path is also None, will default to
            AgentType.ZERO_SHOT_REACT_DESCRIPTION.
        callback_manager: CallbackManager to use. Global callback manager is used if
            not provided. Defaults to None.
        agent_path: Path to serialized agent to use.
        agent_kwargs: Additional key word arguments to pass to the underlying agent
        tags: Tags to apply to the traced runs.
        **kwargs: Additional key word arguments passed to the agent executor

    Returns:
        An agent executor
    """

    # agent_cls = AGENT_TO_CLASS[agent]
    agent_cls = VikiChatAgent
    agent_kwargs = agent_kwargs or {}
    agent_obj = agent_cls.from_llm_and_tools(
        llm, tools, callback_manager=callback_manager, **agent_kwargs
    )

    return AgentExecutor.from_agent_and_tools(
        agent=agent_obj,
        tools=tools,
        callback_manager=callback_manager,
        tags=[],
        **kwargs,
    )
