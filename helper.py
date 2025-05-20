# Moved methods that aren't APIS into this helper file. Used to separate concerns into another file

from openai import Stream
from openai.types.chat import (
    ChatCompletionChunk,
)
import json

# Method Imports
from sqlite import save_message, get_messages_by_session_id_order_by_date_asc, get_sessions_with_session_id
from llm import create_OpenAIMessageType_list_from_existing_messages, OpenAIMessageType

# Enum Import
from llm_enum import Source


async def stream_response(llm_stream: Stream, session_id: str):
    """
    Method that takes in a stream and uses the SSE mechanism to return and display the words as they are streamed
    Prints out the content if no functions are used, 
    and if they are used, pieces together the JSON the function creates through the ChoiceDeltaToolCallFunction class
    If its a function, then we want to print out the refactored json instead of using the yield while building
    Possibility of the api using both a function and content, so created 2 strings to build from that
    If theres a function used, then we yield the json output, but we save the parsed json string to the messages db
    Saves the final message to the messages table, source is "assistant"
    :param session_id: session id being used and messages will be stored to
    :param stream: stream created by the llm and used to pull answers from chunks that are produced
    :return: returns the content from the llm
    """
    # creating 2 different strings since the api occasionally used a function halfway through,
    # We want to process functions and content differently
    # Used example + documentation https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi
    content_message, function_message = "", ""
    async for chunk in llm_stream:
        content = get_content_from_chunk(chunk=chunk)
        functions = get_function_from_chunk(chunk=chunk)
        if content:
            yield content
            content_message += content
        elif functions:
            yield functions
            function_message += functions
    # If we want to correctly parse the json, will need to wait until everything is back, but thats not using SSE.
    # Currently yielding parts of the json as they come in and then yielding the entire thing when its done processing,
    # also saving the processed json to the messages table
    json_parsed_function_message = convert_json_to_string(
        json_message=function_message)
    yield json_parsed_function_message
    combined_message = content_message + json_parsed_function_message
    save_message(session_id=session_id,
                 message=combined_message, source=Source.Assistant.value)


def convert_json_to_string(json_message: str) -> str:
    """
    Parses out the json values and creates a string without the keys. If its not a json, just returns back the message

    :param: json_message: the string that is getting parsed
    :return: returns a string parsed from json values
    """
    try:
        return ' '.join(json.loads(s=json_message).values())
    except ValueError as e:
        return json_message


def get_open_ai_message_list_by_session_id(session_id: int) -> list[OpenAIMessageType]:
    """
    method that returns a list of OpenAIMessageType, created from existing messages.
    Meant to be passed back to the llm to produce more results

    :param: session_id: the session for which we want to pull all of the exisiting messages
    :return: returns a list of existing messages from the messages table, converted to the OpenAIMessage Type
    """
    message_history = get_messages_by_session_id_order_by_date_asc(session_id)
    existing_messages = [(message[1], message[0])
                         for message in message_history]
    return create_OpenAIMessageType_list_from_existing_messages(
        existing_messages=existing_messages)


def verify_chat_session_exists(session_id: int) -> bool:
    """
    Ensure that the session_id already exists in the session table before any operations are done with the session_id
    Raises an exception if one session doesn't already exist, or there are too many sessions

    :param session_id: used to query whether the session exists already
    :return: true or false based on whether the session exists and is the only one in the table
    """
    sessions = get_sessions_with_session_id(session_id=session_id)
    if len(sessions) != 1:
        raise ValueError(f"Invalid Session Id: {session_id}")


def get_function_from_chunk(chunk: ChatCompletionChunk) -> str:
    """
    Will try to return the function arguments from the chunk, unless its empty, which it will return NONE

    :params: ChatCompletionChunk: a chunk of stream output from the api which we will extract the function
    :return: function args from the chunk or None if its empty 
    """
    try:
        return chunk.choices[0].delta.tool_calls[0].function.arguments
    except Exception as e:
        return None


def get_content_from_chunk(chunk: ChatCompletionChunk) -> str:
    """
    Will try to return the content from the chunk, unless its empty, which it will return NONE

    :params: ChatCompletionChunk: a chunk of stream output from the api which we will extract the content:
    :return: content from the chunk or None if its empty 
    """
    try:
        return chunk.choices[0].delta.content
    except Exception as e:
        return None
