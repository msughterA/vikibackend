from tools.create_file import CreateFile
from tools.open_file import OpenFile
from tools.finish import Finish
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from vikierrand.initialize import initialize_viki_errand_agent


# create the function that takes in the instruction and runs the errand
async def run_errand(instruction: str, channel_name: str):
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    template = """
    {instruction} using the tools your given
    to interact remotely with a visual studio instance
    to accomplish the task."""
    tools_for_agent = [
        CreateFile(channel_name=channel_name),
        OpenFile(channel_name=channel_name),
    ]

    agent = initialize_viki_errand_agent(
        tools=tools_for_agent,
        verbose=True,
        llm=llm,
    )

    prompt_template = PromptTemplate(template=template, input_variables=["instruction"])
    # agent.run(
    #     prompt_template.format_prompt(
    #         channel_name=channel_name, instruction=instruction
    #     )
    # )
    output = await agent.arun(prompt_template.format_prompt(instruction=instruction))


async def continue_errand(instruction: str, channel_name: str, previously: list):
    previous_action_observation = ""
    for index, obj in enumerate(previously):
        print(obj)
        previous_action_observation = (
            previous_action_observation
            + f"{str(index)}. action: {obj['action']}\n observation: {obj['result']}"
        )

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    template = """
    Goal:'{instruction}' make sure to look at your previous actions and observations and
    continue from where to stop deciding whether to use the finish tool or not.
    USE FINISH TOOL IF THE ABOVE LIST CONTAINS EVERYTHING YOU NEED TO ACHIEVE THE GOAL!!!
    """
    tools_for_agent = [
        CreateFile(channel_name=channel_name),
        OpenFile(channel_name=channel_name),
        Finish(channel_name=channel_name),
    ]

    agent = initialize_viki_errand_agent(
        tools=tools_for_agent,
        history=previously,
        verbose=True,
        llm=llm,
    )

    prompt_template = PromptTemplate(
        template=template,
        input_variables=["instruction", "previous_action_observation"],
    )
    # agent.run(
    #     prompt_template.format_prompt(
    #         channel_name=channel_name, instruction=instruction
    #     )
    # )

    output = await agent.arun(
        prompt_template.format_prompt(
            instruction=instruction,
            previous_action_observation=previous_action_observation,
        ),
    )


sys_message = """
Respond to the human as helpfully and accurately as possible. You have access to the following tools:

createFile: Use this tool to create files under specific foldersYou must be certain the folder your creating the file under existsYou must be certain the folder path is the right place the user wants to place the file, args: {{{{'folder_dir': {{{{'title': 'Folder Dir', 'description': '\n        The path to folder under which you want to create the file\n        example path/to/folder\n        ', 'type': 'string'}}}}, 'filename': {{{{'title': 'Filename', 'description': '\n        the name of the file you want to create with the file extension attached to it\n        example models.ts\n        ', 'type': 'string'}}}}}}}}
openFile:
        Use this tool to open a file an existing file in the vs code instance
        You must be make sure your opening the right file under the right folder
        , args: {{{{'folder_dir': {{{{'title': 'Folder Dir', 'description': '\n        The folder path of the file you want to create\n        example path/to/folder, ./ for root dir\n        ', 'type': 'string'}}}}, 'filename': {{{{'title': 'Filename', 'description': '\n        The name of the file you want to open with its extentiion\n        example main.py\n        ', 'type': 'string'}}}}}}}}
finish:
        Use this tool to tell the vs code instance you have been controlling
        that you have completed the task
        , args: {{{{'message': {{{{'title': 'Message', 'description': '\n        The finishing message you have to send.\n        ', 'type': 'string'}}}}}}}}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or createFile, openFile, finish

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```

Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation:.
Thought:
"""
