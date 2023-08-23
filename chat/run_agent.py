from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ChatMessageHistory
import os
from typing import Any, Dict, List
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate
from vikichat.initialize import initialize_viki_chat_agent


# do the major and necessary initializations
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or "OPENAI_API_KEY"


def run_agent(query: str, chat_history=[]):
    # Create a ChatMessageHistory object
    history = ChatMessageHistory()
    for chat in chat_history:
        history.add_user_message(chat["input"])
        history.add_ai_message(chat["output"])
    memory = ConversationSummaryMemory.from_messages(
        llm=OpenAI(temperature=0),
        chat_memory=history,
        return_messages=True,
    )

    # initialize agent with tools
    llm = OpenAI(temperature=0)

    conversation_with_summary = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True,
    )
    ouput = conversation_with_summary.predict(input=query)
    return ouput


def run_agent_with_history(query: str, chat_history=[]):
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    tools = []
    memory = ConversationBufferMemory(memory_key="chat_history")
    for chat in chat_history:
        memory.chat_memory.add_user_message(chat["input"])
        memory.chat_memory.add_ai_message(chat["output"])

    agent_chain = initialize_viki_chat_agent(
        tools,
        llm,
        verbose=True,
        memory=memory,
    )
    template = """{question}"""
    prompt_template = PromptTemplate(template=template, input_variables=["question"])
    output = agent_chain.run(prompt_template.format_prompt(question=query))
    return output


sys_msg = """Assistant is a large language model trained by OpenAI.

Assistant is designed to assist a programmer or developer working on a project in visual studio code on a wide range of tasks, from answering simple questions , writing accurate code in different programming language and providing in-depth explanations and discussions on a wide range of computer and programming related topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, code, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text and code based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range to the developer. Assistant properly examines the input it is given and provides the developer with the best and most proffessional response.
Assistant should properly format Code using the markdown syntax as follows
Some text here...
			\`\`\`javascript
			const greeting = 'Hello, world!';
			console.log(greeting);
			\`\`\`
			
			More text...
			
			\`\`\`python
			def say_hello():
				print("Hello, world!")
			
			say_hello()
			\`\`\``
Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
"""
