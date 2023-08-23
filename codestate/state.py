from django.core.cache import cache
import numpy as np
import json
from tree_sitter import Language, Parser
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
from .constants import CHUNK_SIZE
import openai

# class to handle
# 1. handle storage of data
# 2. retrieval of data
# 3. modification of data
# Language.build_library(
#     # Store the library in the `build` directory
#     "build/my-languages.so",
#     # Include one or more languages
#     [
#         "./tree-sitter-javascript",
#         "./tree-sitter-python",
#     ],
# )

# JS_LANGUAGE = Language("build/my-languages.so", "javascript")
# PY_LANGUAGE = Language("build/my-languages.so", "python")
# print("RUNNING STATE")


class State:
    def __init__(self, session_id) -> None:
        self.session_id = session_id
        cache.set(self.session_id, {})

    def embed(self, list_of_string: list):
        # method to embed the strings
        embeddings_dict = openai.Embedding.create(
            input=list_of_string, model="text-embedding-ada-002"
        )["data"]
        embeddings = []
        for embedding in embeddings_dict:
            embeddings.append(embedding["embedding"])

        return embeddings

    def get_context(self, query: str, session_id: str):
        # method to return the best context by rank
        # retrieve the data_dictionary for the session_id from cache
        # get the embeddings and load it with json
        # run the cosine similarity algorithm to get the top 4 most similar text
        # return in a list stating the filename and directory
        pass

    def split_string(self, text: str, file_extension):
        # method to split the strings using text splitter
        if file_extension == "py":
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=Language.PYTHON, chunk_size=300, chunk_overlap=20
            )
            docs = splitter.create_documents([text])
            strings = []
            [strings.append(doc.page_content) for doc in docs]
            return strings
        elif file_extension == "js":
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=Language.JS, chunk_size=300, chunk_overlap=20
            )
            # you can add conditional statements to split only when the text passes a certain threshold
            docs = splitter.create_documents([text])
            strings = []
            [strings.append(doc.page_content) for doc in docs]
            return strings
        return []

    def store_strings_array(
        self, list_of_strings: list, filepath: str, fileextension: str
    ):
        # method to store the list of string in the django cache
        # in the general strings cache
        # also take note of the start and end index and store it
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            if data_dict.get(filepath) is not None:
                file_dict = data_dict[filepath]
            else:
                file_dict = {}
            # file_dict["filename"] = filename
            file_dict["fileextensions"] = fileextension
            # if data_dict.get("strings") == None:
            #     data_dict["strings"] = []
            #     old_list_of_strings = data_dict['strings']
            # else:
            #     old_list_of_strings = data_dict.get("strings")

            old_list_of_strings = data_dict.get("strings") or []

            start_index = len(old_list_of_strings) - 1
            if start_index == -1:
                start_index = 0
            new_list_of_strings = old_list_of_strings + list_of_strings
            end_index = len(new_list_of_strings) - 1
            if end_index == -1:
                end_index = 0
            data_dict["strings"] = new_list_of_strings
            data_dict[filepath] = data_dict
            if data_dict.get("filepaths") != None:
                filepaths = data_dict.get("filepaths")
            else:
                filepaths = []
            filepaths.append(filepath)
            data_dict["filepaths"] = filepaths
            file_dict["startIndex"] = start_index
            file_dict["endIndex"] = end_index
            data_dict[filepath] = file_dict
            cache.set(self.session_id, data_dict)
            print("WE HAVE CACHED IT SUCCESSFULLY")
            return new_list_of_strings

    def store_embedding_array(self, list_of_embeddings: list, filepath: str):
        # method to store the embedding of the file in the general
        # embeddings list for all embeddings of all files
        # also take note of the start and end index
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            # if data_dict.get(filepath) is not None:
            #     file_dict = data_dict[filepath]
            # else:
            #     file_dict = {}

            if data_dict.get("embeddings") == None:
                old_list_of_embeddings = []
            else:
                old_list_of_embeddings = json.loads(data_dict["embeddings"])
            # old_list_of_embeddings = data_dict.get("embeddings") or []
            new_list_of_embeddings = old_list_of_embeddings + list_of_embeddings
            data_dict["embeddings"] = json.dumps(new_list_of_embeddings)
            cache.set(self.session_id, data_dict)

    def modify_strings_array(self, list_of_strings: list, filepath: str):
        # modify the general strings array if the file is updated
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            if data_dict.get("strings") is not None:
                if data_dict.get(filepath) is not None:
                    file_dict = data_dict[filepath]
                    initial_start_index = file_dict["startIndex"]
                    print(f"INITIAL VALUE {initial_start_index}")
                    initial_end_index = file_dict["endIndex"]
                    old_list_of_strings = data_dict["strings"]
                    all_filepaths = data_dict["filepaths"]
                    file_index = all_filepaths.index(filepath)
                    after_filepaths = all_filepaths[file_index + 1 :]
                    print(after_filepaths)
                    indices = []
                    old_length = len(old_list_of_strings) - 1
                    for index, key in enumerate(after_filepaths):
                        indices_dict = {
                            "filepath": key,
                            "startIndex": int(data_dict[key]["endIndex"]),
                            "endIndex": int(data_dict[key]["startIndex"]),
                        }
                        indices.append(indices_dict)
                    # if initial_start_index == 0:
                    #     old_list_of_strings_first_slice = old_list_of_strings[
                    #         :initial_start_index
                    #     ]
                    # else:
                    #     old_list_of_strings_first_slice = old_list_of_strings[
                    #         : initial_start_index + 1
                    #     ]
                    old_list_of_strings_first_slice = old_list_of_strings[
                        :initial_start_index
                    ]
                    # old_list_of_strings_for_file_slice = old_list_of_strings[
                    #     initial_start_index : initial_end_index + 1
                    # ]
                    new_length = len(list_of_strings) - 1
                    old_list_of_strings_remaining_slice = old_list_of_strings[
                        initial_end_index + 1 :
                    ]

                    # old_list_of_strings[start_index : end_index + 1] = list_of_strings
                    delta = -1
                    if old_length > new_length:
                        delta = -new_length
                    else:
                        delta = new_length
                    for index, indices_dict in enumerate(indices):
                        indices[index]["startIndex"] = (
                            indices[index]["startIndex"] + delta
                        )
                        indices[index]["endIndex"] = indices[index]["endIndex"] + delta
                        data_dict[indices_dict["filepath"]]["startIndex"] = str(
                            indices[index]["startIndex"]
                        )
                        data_dict[indices_dict["filepath"]]["endIndex"] = str(
                            indices[index]["endIndex"]
                        )
                    # change the end index of the current filepath
                    data_dict[filepath]["endIndex"] = new_length
                    data_dict["strings"] = (
                        old_list_of_strings_first_slice
                        + list_of_strings
                        + old_list_of_strings_remaining_slice
                    )
                    print(
                        f"THE START INDEX AFTER MODIFICATION IS {data_dict[filepath]['startIndex']}"
                    )
                    cache.set(self.session_id, data_dict)

    def modify_embeddings_array(self, list_of_embeddings: list, filepath: str):
        # modify the general embeddings array if the file is updated
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            if data_dict.get("embeddings") is not None:
                if data_dict.get(filepath) is not None:
                    file_dict = data_dict[filepath]
                    initial_start_index = file_dict["startIndex"]
                    initial_end_index = file_dict["endIndex"]
                    old_list_of_embeddings = json.loads(data_dict["embeddings"])
                    # all_filepaths = data_dict["filepaths"]
                    # file_index = all_filepaths.index(filepath)
                    # after_filepaths = all_filepaths[file_index:]
                    # old_length = len(old_list_of_strings) - 1
                    print(f"Initial start index is {initial_start_index}")
                    old_list_of_embeddings_first_slice = old_list_of_embeddings[
                        :initial_start_index
                    ]
                    # old_list_of_strings_for_file_slice = old_list_of_strings[
                    #     initial_start_index : initial_end_index + 1
                    # ]
                    new_length = len(list_of_embeddings) - 1
                    old_list_of_embeddings_remaining_slice = old_list_of_embeddings[
                        initial_end_index + 1 :
                    ]
                    # change the end index of the current filepath
                    # data_dict[filepath]["endIndex"] = new_length
                    data_dict["embeddings"] = json.dumps(
                        old_list_of_embeddings_first_slice
                        + list_of_embeddings
                        + old_list_of_embeddings_remaining_slice
                    )
                    print(len(data_dict["embeddings"]))
                    cache.set(self.session_id, data_dict)

    def store_indices(self, start_index: int, end_index: int, filepath: str):
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            if data_dict.get(filepath) is not None:
                file_dict = data_dict[filepath]
                file_dict["startIndex"] = str(start_index)
                file_dict["endIndex"] = str(end_index)
                data_dict = file_dict
                cache.set(self.session_id, data_dict)

    def on_file_modify(self, filepath: str, file_extension: str, file_content: str):
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            file_dict = {}
            file_dict["content"] = file_content
            data_dict[filepath] = file_dict
            cache.set(self.session_id, data_dict)
        splitted_string = self.split_string(file_content, file_extension)
        # modify the strings
        self.modify_strings_array(splitted_string, filepath)
        # get embddings
        embeddings = self.embed(splitted_string)
        # modify embeddings
        self.modify_embedding_array(embeddings, filepath)

    def on_file_open(self, filepath: str, file_extension: str, file_content: str):
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            file_dict = {}
            file_dict["content"] = file_content
            data_dict[filepath] = file_dict
            cache.set(self.session_id, data_dict)
            print("CACHE SUCCES")
        splitted_string = self.split_string(file_content, file_extension)
        # store the strings
        self.store_strings_array(
            splitted_string,
            filepath,
            fileextension=file_extension,
        )
        # get embddings
        embeddings = self.embed(splitted_string)
        # store embeddings
        self.store_embedding_array(embeddings, filepath=filepath)

    def on_file_close(self, filepath: str):
        if cache.get(self.session_id) is not None:
            data_dict = cache.get(self.session_id)
            if data_dict.get(filepath) is not None:
                file_dict = data_dict[filepath]
                start_index = file_dict["startIndex"]
                end_index = file_dict["endIndex"]
                length = end_index + 1
                all_filepaths = data_dict["filepaths"]
                file_index = all_filepaths.index(filepath)
                after_filepaths = all_filepaths[file_index + 1 :]
                indices = []
                for index, key in enumerate(after_filepaths):
                    indices_dict = {
                        "filepath": key,
                        "startIndex": int(data_dict[key]["endIndex"]),
                        "endIndex": int(data_dict[key]["startIndex"]),
                    }
                    indices.append(indices_dict)
                for index, indices_dict in enumerate(indices):
                    indices[index]["startIndex"] = indices[index]["startIndex"] - length
                    indices[index]["endIndex"] = indices[index]["endIndex"] - length
                    data_dict[indices_dict["filepath"]]["startIndex"] = str(
                        indices[index]["startIndex"]
                    )
                    data_dict[indices_dict["filepath"]]["endIndex"] = str(
                        indices[index]["endIndex"]
                    )
                embeddings = json.loads(data_dict["embeddings"])
                embeddings[start_index : end_index + 1] = []
                data_dict["embeddings"] = json.dumps(embeddings)
                data_dict["strings"][start_index : end_index + 1] = []
                print(data_dict["embeddings"])
                cache.set(self.session_id, data_dict)

    def initialize(self, files: list[dict]):
        # handle the iniialization of the dictionary
        # use the session id to store an empty dictionay under it
        cache.set(self.session_id, {})
        session_dict = {}
        data_dict = {}
        # loop through the file opened
        for file in files:
            self.on_file_open(
                file_content=file["fileContent"],
                filepath=file["filePath"],
                file_extension=file["fileExtension"],
            )
