# SWE, Backend & Applied ML take-home assignment

The goal of this take-home assignment is to assess aptitude for back-end engineering with tools and technologies that we use every day:

- OpenAI Python SDK (making calls to GPT-3.5/4/etc)
- FastAPI (with streaming responses)
- Pydantic
- SQL

While the project is much more simplified than our production codebase, it is very similar in many ways.

We also hope the assignment is fun and provides you with a more detailed look into day-to-day work in the role.

It's perfectly fine to use outside resources such Google, Stackoverflow, and even ChatGPT itself.

If you do, we ask that you note it in a comment next to any code that needed referencing outside sources.

If you're going to use ChatGPT, use it _narrowly_, e.g. ask only specific questions about one part of the project.

DO NOT USE CHATGPT (OR SIMILAR TOOLS) TO COMPLETE THE ASSIGNMENT FOR YOU.

Be aware that we have run this assignment itself through ChatGPT several times and are keenly familiar with the kind of output it will provide.

## Assignment

In `main.py`, we have provided a shell of a FastAPI app. It includes one route that demonstrates streaming data using Server-Sent Events (SSEs)

In `llm.py`, we have provided some code for prompting the Large Language Model (LLM) both synchronously and asynchronously. The prompts can be left as-is for this assignment. But we want to see aptitude in calling the LLM API and properly handling the response. See https://platform.openai.com/docs/api-reference/chat and https://platform.openai.com/docs/guides/text-generation/chat-completions-api?lang=python for more information about OpenAI's Chat Completions service. See https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb for information about receiving streaming results.

Please modify the file (or add your own files and organize them in any way you like) such that:

- The API provides a barebones Chat service that a front-end client can use.
- The service should have the following capabilities:
  - an HTTP client can create a new chat session
  - given a chat session (e.g. its ID), an HTTP client can send a message on behalf of the user, and receive the "AI" response from the LLM.
  - responses from the AI should be streamed using the SSE mechanism mentioned above.\*
  - an HTTP client can also fetch the entire message history for a given session
- Persistence of sessions and messages implemented in an RDBMS of your choosing (SQLite is probably best but Postgres etc are great too if you prefer)

\*A note on handling function calls: The model is expected to occasionally return functions in addition to plain text and your code should handle this.
It is sufficient to just return the JSON provided by the model to the user as text but if you'd like to go for extra credit, feel free to consider other ways the model's function output could be handled.

The database design does not have to be complicated at all, we're mostly interested in seeing that you understand the basics.
For this reason, we strongly prefer that you do not use an ORM such as SQLAlchemy in your code. Instead, please write your SQL queries and commands directly (using parameterized queries to prevent SQL injection!).

Do not worry about things like user authentication or really any other production consideration not already mentioned above.

Feel free to add new dependencies to `requirements.txt` as needed.

## Starting the project

To run the provided code, you'll need Python 3.10.x (other versions might work, but the project was written against 3.10.7).

Install dependencies: `pip install requirements.txt`

Add OpenAI API keys to the environment. Use `.env.example` and/or `llm.py` as a guide. DO NOT INCLUDE API KEYS IN YOUR SUBMISSION. Please obtain your own keys from your own account. If you are unable to do this, let us know and we'll find an alternative approach.

Running the local server:

```
uvicorn main:app --reload
```

To prompt the LLM at the CL (good way to learn about it):

```
python llm.py "hey who are you and what can you do for me?"
```

And to see how the model behaves when it's streaming back a function, try:

```
python llm.py "please explain the joke: why did the chicken cross the road?"
```

## Submitting the assignment

Please clone this repository, complete the assignment, and share your private clone or fork of the repository with github user cmorbidelli. Please do not open a pull request off of this repo or create a public repository with your solution.

Also, please do not send the code zip file as an email attachment as it may cause the email to be blocked by company email security policies.

## Evaluation

We're going to view the submission holistically, but evaluation will focus on several key areas:

- Does the submission accomplish the required tasks?
- Code quality: is the code well-organized, documented (e.g. docstrings), and easy-to-understand?
- Use of types: we love typed Python on the CoCounsel team, and it works really well with FastAPI and Pydantic. For more info, see https://docs.python.org/3/library/typing.html.
- Data safety and validity: are SQL inputs sanitized? are proper measures taken to ensure data validity is checked both statically (e.g. through typing) and at runtime? consider the validity of data returned from the LLM's function calls.
- Design: is the database schema well-designed? are database calls reasonably efficient?
- Sensibility: do the names and HTTP methods for the routes effectively convey their purpose?
- Easy to operate: does the HTTP API make it easy for a client (e.g. HTML/JS web app) to provide a user interface?
- Proper use of asynchronous and synchronous Python code.

A successful submission will hit most of the points above.
A standout submission will hit all of the points above.
A stellar submission will also demonstrate innovation at the prompt-level (e.g. modify the system prompt, add creative new function calls, you name it ...)
