from __future__ import annotations

import asyncio
import json
import threading
from collections import defaultdict
from typing import Any

Subscribers = dict[str, set[tuple[asyncio.AbstractEventLoop, asyncio.Queue[str]]]]
_subscribers: Subscribers = defaultdict(set)
_lock = threading.Lock()


def subscribe(run_id: str, loop: asyncio.AbstractEventLoop) -> asyncio.Queue[str]:
    queue: asyncio.Queue[str] = asyncio.Queue()
    with _lock:
        _subscribers[run_id].add((loop, queue))
    return queue


def unsubscribe(run_id: str, queue: asyncio.Queue[str]) -> None:
    with _lock:
        _subscribers[run_id] = {item for item in _subscribers[run_id] if item[1] is not queue}
        if not _subscribers[run_id]:
            _subscribers.pop(run_id, None)


def publish(run_id: str, event: dict[str, Any]) -> None:
    message = json.dumps(event, ensure_ascii=False)
    with _lock:
        subscribers = list(_subscribers.get(run_id, set()))
    for loop, queue in subscribers:
        loop.call_soon_threadsafe(queue.put_nowait, message)
