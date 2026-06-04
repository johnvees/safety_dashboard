"""Web Push (VAPID) delivery helper.

Sends browser push notifications to a user's stored PushSubscription rows so
they pop up natively even when the site/browser is fully closed. Sending runs
on a background thread so it never blocks the GraphQL request, and dead
subscriptions (404/410) are pruned automatically.
"""
from __future__ import annotations

import json
import logging
import os
import threading

from pywebpush import WebPushException, webpush
from py_vapid import Vapid01

log = logging.getLogger("web_push")

_VAPID_PRIVATE = os.getenv("VAPID_PRIVATE_KEY", "")
_VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:admin@example.com")
PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")

_vapid: Vapid01 | None = None


def _get_vapid() -> Vapid01 | None:
    global _vapid
    if _vapid is None and _VAPID_PRIVATE:
        _vapid = Vapid01.from_raw(_VAPID_PRIVATE.encode())
    return _vapid


def is_configured() -> bool:
    return bool(_VAPID_PRIVATE and PUBLIC_KEY)


def _send_one(endpoint: str, p256dh: str, auth: str, payload: str, vapid: Vapid01) -> bool:
    """Send one push. Returns False if the subscription is gone (delete it)."""
    try:
        webpush(
            subscription_info={"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}},
            data=payload,
            vapid_private_key=vapid,
            vapid_claims={"sub": _VAPID_SUBJECT},
            ttl=86400,
        )
        return True
    except WebPushException as e:
        status = getattr(e.response, "status_code", None)
        if status in (404, 410):
            return False  # subscription expired/unsubscribed
        log.warning("web push failed (%s): %s", status, e)
        return True
    except Exception as e:  # network etc. — keep the sub, try again next time
        log.warning("web push error: %s", e)
        return True


def push_to_user(user_id: int, *, title: str, body: str = "", url: str = "/", tag: str = "") -> None:
    """Fire-and-forget push to every subscription of a user (non-blocking)."""
    if not is_configured():
        return
    threading.Thread(
        target=_push_to_user_blocking,
        args=(user_id, title, body, url, tag),
        daemon=True,
    ).start()


def _push_to_user_blocking(user_id: int, title: str, body: str, url: str, tag: str) -> None:
    from app.database import SessionLocal
    from app import models

    vapid = _get_vapid()
    if vapid is None:
        return

    db = SessionLocal()
    try:
        subs = db.query(models.PushSubscription).filter_by(user_id=user_id).all()
        if not subs:
            return
        payload = json.dumps({"title": title, "body": body or "", "url": url or "/", "tag": tag or ""})
        dead: list[int] = []
        for s in subs:
            if not _send_one(s.endpoint, s.p256dh, s.auth, payload, vapid):
                dead.append(s.id)
        if dead:
            db.query(models.PushSubscription).filter(
                models.PushSubscription.id.in_(dead)
            ).delete(synchronize_session=False)
            db.commit()
    except Exception as e:
        log.warning("push_to_user failed: %s", e)
    finally:
        db.close()
