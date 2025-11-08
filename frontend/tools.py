"""
Tool definitions and (optional) handlers for backend-linked functions.

This exposes function-calling schemas for the LLM and async handlers that
call the Flask backend endpoints.
"""

import os
from typing import Any, Dict, Callable, Awaitable

import aiohttp
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


# ---- Tool Schemas (OpenAI-style function tools) ----

send_message_schema = FunctionSchema(
    name="send_message",
    description="Send a text message to a contact.",
    properties={
            "contact": {
                "type": "string",
                "description": "The contact name to send the message to."
                },
            "message": {
                "type": "string",
                "description": "The message body to send."
            }
        },
    required =  ["contact", "message"]
    
)

request_call_schema = FunctionSchema(
    name="request_call",
    description="Request a voice or video call with a contact.",
    properties={
            "contact": {
                "type": "string",
                "description": "Contact to call."
            },
            "call_type": {
                "type": "string",
                "enum": ["voice", "video"],
                "description": "Type of call to initiate."
            }
        },
    required = ["contact", "call_type"]
)

respond_to_call_schema = FunctionSchema(
    name="respond_to_call",
    description="Accept or reject an incoming call.",
    properties={
            "call_id": {
                "type": "string",
                "description": "ID of the call."
            },
            "accept": {
                "type": "boolean",
                "description": "True to accept, False to reject."
            }
        },
    required = ["call_id", "accept"]
)

end_call_schema = FunctionSchema(
    name="end_call",
    description="End an active call.",
    properties={
            "call_id": {
                "type": "string",
                "description": "ID of the active call."
            }
        },
    required = ["call_id"]
)

get_message_history_schema = FunctionSchema(
    name="get_message_history",
    description="Get recent message history with a contact.",
    properties={
            "contact": {
                "type": "string",
                "description": "Contact name."
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 200,
                "default": 50
            }
        },
    required = ["contact"]
)



tools = ToolsSchema(
    standard_tools=[
        send_message_schema,
        request_call_schema,
        respond_to_call_schema,
        end_call_schema,
        get_message_history_schema,
    ]
)


# ---- Optional: Async handlers that call the backend ----

async def handle_send_message(args: Dict[str, Any]) -> Dict[str, Any]:
    contact = args.get("contact", "")
    message = args.get("message", "")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/api/messages/send",
            json={"contact": contact, "message": message}
        ) as resp:
            data = await resp.json()
            return data


async def handle_request_call(args: Dict[str, Any]) -> Dict[str, Any]:
    contact = args.get("contact", "")
    call_type = args.get("call_type", "voice")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/api/calls/request",
            json={"contact": contact, "type": call_type}
        ) as resp:
            data = await resp.json()
            return data


async def handle_respond_to_call(args: Dict[str, Any]) -> Dict[str, Any]:
    call_id = args.get("call_id", "")
    accept = bool(args.get("accept", False))
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/api/calls/respond",
            json={"call_id": call_id, "accept": accept}
        ) as resp:
            data = await resp.json()
            return data


async def handle_end_call(args: Dict[str, Any]) -> Dict[str, Any]:
    call_id = args.get("call_id", "")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/api/calls/end",
            json={"call_id": call_id}
        ) as resp:
            data = await resp.json()
            return data


async def handle_get_message_history(args: Dict[str, Any]) -> Dict[str, Any]:
    contact = args.get("contact", "")
    limit = int(args.get("limit", 50))
    params = {"contact": contact, "limit": str(limit)}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/api/messages/history", params=params) as resp:
            data = await resp.json()
            return data


def get_tools() -> ToolsSchema:
    """Return the function/tool schemas for the LLM context."""
    return tools


def get_tool_handlers() -> Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]]:
    """Return a mapping from tool name to async handler that hits the backend.

    Note: You still need to wire a tools-execution processor in the pipeline
    if you want automatic execution of function calls returned by the LLM.
    """
    return {
        "send_message": handle_send_message,
        "request_call": handle_request_call,
        "respond_to_call": handle_respond_to_call,
        "end_call": handle_end_call,
        "get_message_history": handle_get_message_history,
    }