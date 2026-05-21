"""In-memory pub/sub broker for chat subscriptions.

Each connected subscriber gets a per-user asyncio.Queue. When a message is
sent, send_message() publishes a payload to the recipient's (and optionally
the sender's) queues so live UIs update instantly.

This is single-process only; for a multi-instance deployment swap this for
Redis pub/sub or similar.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class ChatBroker:
    def __init__(self) -> None:
        self._subscribers: dict[int, set[asyncio.Queue]] = defaultdict(set)

    def subscribe(self, user_id: int) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=256)
        self._subscribers[user_id].add(q)
        return q

    def unsubscribe(self, user_id: int, q: asyncio.Queue) -> None:
        subs = self._subscribers.get(user_id)
        if subs is None:
            return
        subs.discard(q)
        if not subs:
            self._subscribers.pop(user_id, None)

    def publish(self, user_id: int, payload: Any) -> None:
        for q in list(self._subscribers.get(user_id, ())):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                # Drop oldest to keep the stream healthy
                try:
                    q.get_nowait()
                    q.put_nowait(payload)
                except Exception:
                    pass


broker = ChatBroker()
