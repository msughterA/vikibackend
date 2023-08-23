import guidance
from codestate.state import State
from django.core.cache import cache

# we will use GPT-3 for most of the examples in this tutorial
guidance.llm = guidance.llms.OpenAI("gpt-3.5-turbo")


def simple_chat(prompt: str, history: str):
    history_program = guidance(
        """
    {{#each history}}
    {{#user~}}
    {{this.input}}
    {{~/user}}
    
    {{#assistant~}}
    {{this.output}}
    {{~/assistant}}
    {{/each~}}"""
    )
    program = guidance(
        """
    {{#system~}}
    You are a helpful assistant. who has extensive knowledge in computer science and programming.
    built to assist a programmer develop software in visual studio code.
    make sure to put all code your outputting in the approprate markdown format
     {{! the code related to the question asked by the developer would be passed here }}
  
    {{~/system}}
    
    {{>history_program}}
    
    {{#user~}}
    {{conversation_question}}
    {{~/user}}

    {{! this is a comment. note that we don't have to use a stop="stop_string" for the gen command below because Guidance infers the stop string from the role tag }}
    {{#assistant~}}
    {{gen 'response'}}
    {{~/assistant}}"""
    )

    executed_program = program(
        conversation_question=prompt, history_program=history_program, history=history
    )
    print(f"THIS IS THE PROGRAM {program}")
    return executed_program["response"]


def context_retriever():
    files = []
    sessionid = "AD123456ASE"
    if cache.get(sessionid) is not None:
        data_dict = cache.get(sessionid)
        filepaths = data_dict["filepaths"]
        for filepath in filepaths:
            my_dict = {}
            my_dict["filepath"] = filepath
            my_dict["content"] = data_dict[filepath]["content"]
            files.append(my_dict)
    return files


def simple_chat_test(prompt: str, history: str):
    files = context_retriever()

    history_program = guidance(
        """
    {{#each history}}
    {{#user~}}
    {{this.input}}
    {{~/user}}
    
    {{#assistant~}}
    {{this.output}}
    {{~/assistant}}
    {{/each~}}"""
    )
    files_program = guidance(
        """
        {{#each files}}
         filepath : {{this.filepath}},
         filecontent: {{this.content}}
        {{/each~}}
        """
    )
    program = guidance(
        """
    {{#system~}}
    You are a helpful assistant. who has extensive knowledge in computer science and programming.
    built to assist a programmer develop software in visual studio code.
    make sure to put all code your outputting in the approprate markdown format
     {{! the code related to the question asked by the developer would be passed here }}
     Here are a list of filepaths and their contents currently open in the users IDE.
     Use the information to answer the users question when appropriate.
     {{>files_program}}
    {{~/system}}
    
    {{>history_program}}
    
    {{#user~}}
    {{conversation_question}}
    {{~/user}}

    {{! this is a comment. note that we don't have to use a stop="stop_string" for the gen command below because Guidance infers the stop string from the role tag }}
    {{#assistant~}}
    {{gen 'response'}}
    {{~/assistant}}"""
    )

    executed_program = program(
        conversation_question=prompt,
        history_program=history_program,
        files_program=files_program,
        history=history,
        files=files,
    )
    print(f"THIS IS THE PROGRAM {program}")
    return executed_program["response"]
