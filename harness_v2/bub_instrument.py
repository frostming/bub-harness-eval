"""Observe Anthropic usage without changing prompts, requests, or response events."""
import json
import os
import runpy
import time
import uuid
from pathlib import Path

from anthropic import AsyncStream
from anthropic.resources.messages import AsyncMessages


def record(payload):
    path = Path(os.environ["FH_USAGE_PATH"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps({"time": time.time(), **payload}) + "\n")


original_create = AsyncMessages.create
original_stream = AsyncStream.__stream__
original_init = AsyncStream.__init__


def stream_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    self._fh_call_id = uuid.uuid4().hex
    record({"event": "request", "call_id": self._fh_call_id, "stream": True})


async def create(self, *args, **kwargs):
    if kwargs.get("stream"):
        return await original_create(self, *args, **kwargs)
    call_id = uuid.uuid4().hex
    record({"event": "request", "call_id": call_id, "model": kwargs.get("model")})
    try:
        result = await original_create(self, *args, **kwargs)
    except BaseException as exc:
        record({"event": "error", "call_id": call_id, "error_type": type(exc).__name__})
        raise
    if isinstance(result, AsyncStream):
        result._fh_call_id = call_id
    elif getattr(result, "usage", None) is not None:
        record({"event": "usage", "call_id": call_id,
                "usage": result.usage.model_dump(exclude_none=True)})
    return result


async def stream(self):
    usage = {}
    complete = False
    try:
        async for event in original_stream(self):
            if getattr(event, "type", None) == "message_start":
                usage.update(event.message.usage.model_dump(exclude_none=True))
            elif getattr(event, "type", None) == "message_delta" and event.usage:
                usage.update(event.usage.model_dump(exclude_none=True))
            elif getattr(event, "type", None) == "message_stop":
                complete = True
            yield event
    finally:
        if usage:
            record({"event": "usage" if complete else "partial_usage",
                    "call_id": getattr(self, "_fh_call_id", None), "usage": usage})


AsyncMessages.create = create
AsyncStream.__init__ = stream_init
AsyncStream.__stream__ = stream
runpy.run_module("bub", run_name="__main__")
