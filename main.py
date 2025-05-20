"""Main project file"""

from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

# Helper Classes
from helper import stream_response, get_open_ai_message_list_by_session_id, verify_chat_session_exists
from sqlite import save_new_session, get_messages_by_session_id_order_by_date_asc, save_message
from llm import prompt_llm_async

# Enum Import
from llm_enum import Source

app = FastAPI()


# used pydantic documentation to write these validation classes
class LLM_Query_Request_Params(BaseModel):
    session_id: int
    message: str


class Chat_History_Request_Params(BaseModel):
    session_id: int


@app.get("/create-new-chat-session")
async def create_new_chat_session() -> int:
    """
    Endpoint that helps a user create a new session and returns a session_id to use later on
    :return: a newly created session_id
    """

    return save_new_session()


@app.post("/prompt-llm-response")
async def prompt_llm_response(params: LLM_Query_Request_Params) -> EventSourceResponse:
    """
    Pass in a session_id and prompt to recieve a response from the llm, 
    Streams the responses from the API using the SSE mechanism,
    and then saves the user query and the response in the messages table
    Has some verification to ensure the chat session exists already, otherwise an exception is raised
    Also creates a list of previously user submitted messages that will be passed to the api to use for existing messages
    :param session_id: session id being used and messages will be stored to
    :param message: prompt message that will be used to get a prompt from the llm
    :return: content or function data from the llm
    """
    verify_chat_session_exists(session_id=params.session_id)
    open_ai_messages_list = get_open_ai_message_list_by_session_id(
        session_id=params.session_id)
    save_message(session_id=params.session_id,
                 message=params.message, source=Source.User.value)

    # We wait for the stream to be created and pass it to be streamed through the event source response
    returned_llm_stream = await prompt_llm_async(
        user_message_content=params.message, existing_messages=open_ai_messages_list)
    return EventSourceResponse(stream_response(
        llm_stream=returned_llm_stream, session_id=params.session_id))


@app.post("/get-chat-history")
async def get_chat_history(params: Chat_History_Request_Params) -> list[str]:
    """
    Pulls the entire chat history of a session, user prompts, date created and llm responses
    Has some verification to ensure the chat session exists already, otherwise an exception is raised
    :param session_id: session id being used to pull all related messages
    :returns: a list of session messages from the llm and the user
    """
    verify_chat_session_exists(session_id=params.session_id)
    messages = get_messages_by_session_id_order_by_date_asc(
        session_id=params.session_id)
    return [' : '.join(message) for message in messages]
