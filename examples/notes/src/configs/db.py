
import asyncio
import inspect
import os
import threading

from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv()

# Every module that holds models goes in this list: add yours next to the one of the starter.
TORTOISE_ORM = {
    "connections": {"default": os.getenv("DATABASE_URL", "sqlite://dev.db")},
    "apps": {
        "models": {
            "models": ["src.models.note_model", "aerich.models"],
            "default_connection": "default",
        }
    },
}

# Tortoise is async and its connections belong to the event loop that opened them. Nexy pages run
# in the server's loop and cannot wait on it, so Tortoise gets a loop of its own, in one thread:
#   run(coroutine)        from sync code, such as a page: runs it there and returns the result
#   await arun(coroutine) from async code, such as a controller: the same, without blocking
_ready = False


def _database_loop() -> asyncio.AbstractEventLoop:
    loop = getattr(Tortoise, "_nexy_loop", None)
    if loop is None:
        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever, name="tortoise", daemon=True).start()
        # Kept on Tortoise, not here: `nexy dev` imports this file again after a save.
        Tortoise._nexy_loop = loop
    return loop


# Tortoise 1 keeps its connections in the task that opened them, and each call here is a task of
# its own: the global fallback lets the next ones find them. Tortoise 0 has global state already.
_SHARED = {"_enable_global_fallback": True}
if "_enable_global_fallback" not in inspect.signature(Tortoise.init).parameters:
    _SHARED = {}


async def _on_database_loop(coroutine):
    global _ready
    if not _ready:
        # After `nexy dev` imports the models again, the previous setup still holds the old ones.
        await Tortoise.close_connections()
        await Tortoise.init(config=TORTOISE_ORM, **_SHARED)
        _ready = True
    return await coroutine


def run(coroutine):
    return asyncio.run_coroutine_threadsafe(_on_database_loop(coroutine), _database_loop()).result()


async def arun(coroutine):
    job = asyncio.run_coroutine_threadsafe(_on_database_loop(coroutine), _database_loop())
    return await asyncio.wrap_future(job)
