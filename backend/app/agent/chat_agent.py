from __future__ import annotations
from sqlalchemy.orm import Session

from app.router.router import route_intent
from app.router.intents import Intent, RouteDecision
from app.agent import handlers


def handle_message(
    user_message: str,
    db: Session,
    conversation_snippet: str | None = None,  # kept for FastAPI compatibility
) -> str:
    """
    Main entrypoint for the chat agent.

    - Classifies the message using the rule-based router (fast, no LLM)
    - Dispatches to the appropriate handler
    - Returns a final natural-language answer
    """

    decision: RouteDecision = route_intent(user_message)
    intent = decision.intent

    if intent == Intent.REPAIR_HELP:
        return handlers.handle_repair_help(decision, db)

    if intent == Intent.BLOG_HOWTO:
        return handlers.handle_blog_howto(decision, db)

    if intent == Intent.PRODUCT_INFO:
        return handlers.handle_product_info(decision, db)

    if intent == Intent.COMPAT_CHECK:
        return handlers.handle_compat_check(decision, db)

    if intent == Intent.ORDER_SUPPORT:
        return handlers.handle_order_support(decision, db)

    if intent == Intent.POLICY:
        return handlers.handle_policy(decision, db)

    if intent == Intent.SMALL_TALK:
        return handlers.handle_small_talk(decision, db)

    if intent == Intent.OUT_OF_SCOPE:
        return handlers.handle_out_of_scope(decision, db)

    if intent == Intent.CLARIFICATION:
        return handlers.handle_clarification(decision, db)

    # Fallback (should rarely happen)
    return (
        "I’m not entirely sure how to handle that. "
        "I’m best at refrigerator and dishwasher parts, compatibility, and repair help. "
        "Could you rephrase your question with a bit more detail?"
    )
