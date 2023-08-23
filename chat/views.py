from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .run_agent import run_agent, run_agent_with_history
import json
from .guide import simple_chat, simple_chat_test


# Create your views here.
class ChatView(APIView):
    def post(self, request):
        # load the json data from the request
        data = request.data
        if ("query" in request.data) and ("chat_history" in request.data):
            self.query = data["query"]
            self.chat_history = data["chat_history"]
            # output = run_agent(self.query, self.chat_history)
            output = simple_chat_test(self.query, history=self.chat_history)
            print(output)
            return Response(
                data={"status": True, "output": output},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(data={"status": False, "data": "An error occured"})


# from langchain.chat_models import ChatOpenAI
# from langchain.agents import initialize_agent, AgentType, Tool
# from langchain.memory import ChatMessageHistory
# import os
# from typing import Any, Dict, List
# from langchain.chains import ConversationChain
# from langchain.memory import ConversationSummaryMemory
# from langchain.llms import OpenAI

# # do the major and necessary initializations
# # OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or "OPENAI_API_KEY"

# # initialize LLM (we use ChatOpenAI because we'll later define a `chat` agent)
# llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")


# def run_agent(query: str, chat_history=[]):
#     # Create a ChatMessageHistory object
#     history = ChatMessageHistory()
#     for chat in chat_history:
#         history.add_user_message(chat["input"])
#         history.add_ai_message(chat["output"])
#     memory = ConversationSummaryMemory.from_messages(
#         llm=OpenAI(temperature=0), chat_memory=history, return_messages=True
#     )

#     # initialize agent with tools
#     llm = OpenAI(temperature=0)
#     conversation_with_summary = ConversationChain(
#         llm=llm, memory=ConversationSummaryMemory(llm=OpenAI()), verbose=True
#     )
#     ouput = conversation_with_summary.predict(input=query)
#     return ouput
