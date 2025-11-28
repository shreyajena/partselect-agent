# app/agent/chat_agent.py

from __future__ import annotations
from sqlalchemy.orm import Session

from app.router.router import route_intent
from app.router.intents import Intent, RouteDecision
from app.agent import handlers

def _format_response(payload):
    if isinstance(payload, dict) and "reply" in payload:
        return payload
    return {"reply": str(payload), "metadata": None}


def handle_message(
    user_message: str,
    db: Session,
    conversation_snippet: str | None = None,  # kept for API compatibility
) -> dict:
    """
    Main entrypoint for the chat agent.

    - Routes the message using a lightweight, rule-based router
    - Dispatches to the appropriate handler
    - Returns a final natural-language answer

    conversation_snippet is currently unused, but retained to avoid breaking the FastAPI endpoint.
    """

    decision: RouteDecision = route_intent(user_message)
    intent = decision.intent

    if intent == Intent.REPAIR_HELP:
        return _format_response(handlers.handle_repair_help(decision, db))

    if intent == Intent.BLOG_HOWTO:
        return _format_response(handlers.handle_blog_howto(decision, db))

    if intent == Intent.PRODUCT_INFO:
        return _format_response(handlers.handle_product_info(decision, db))

    if intent == Intent.COMPAT_CHECK:
        return _format_response(handlers.handle_compat_check(decision, db))

    if intent == Intent.ORDER_SUPPORT:
        return _format_response(handlers.handle_order_support(decision, db))

    if intent == Intent.POLICY:
        return _format_response(handlers.handle_policy(decision, db))

    if intent == Intent.OUT_OF_SCOPE:
        return _format_response(handlers.handle_out_of_scope(decision, db))

    if intent == Intent.CLARIFICATION:
        return _format_response(handlers.handle_clarification(decision, db))

    # Super defensive fallback
    return _format_response(
        "I’m not entirely sure how to handle that. "
        "I’m best at refrigerator and dishwasher parts, compatibility, and repair help. "
        "Could you rephrase your question with a bit more detail?"
    )
