from __future__ import annotations
import logging
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Part, PartModelMapping, Model, User, Order, Transaction
from app.rag.retrieval import retrieve_documents
from app.llm.client import get_chat_client, get_default_model
from app.router.intents import RouteDecision
from app.config.prompts import GLOBAL_STYLE, PRODUCT_INFO_PROMPT, REPAIR_HELP_PROMPT, ORDER_SUPPORT_PROMPT
from app.config.urls import (
    REPAIR_URL,
    INSTANT_REPAIRMAN_URL,
    REMOTE_SERVICER_URL,
    BROWSE_PARTS_URL,
    CONTACT_SUPPORT_URL,
    CUSTOMER_SUPPORT_URL,
    RETURNS_POLICY_URL,
    WARRANTY_URL,
    SHIPPING_URL,
    PRICE_MATCH_URL,
    SELF_SERVICE_RETURN_URL,
    BLOG_RESOURCES_URL,
)
from app.config.constants import (
    LLM_MAX_RETRIES,
    LLM_TEMPERATURE,
    LLM_RETRY_BACKOFF_BASE,
    RAG_TOP_K,
    RAG_CONTEXT_SEPARATOR,
    ERROR_LLM_FAILED,
    ERROR_PART_NOT_FOUND,
    ERROR_ORDER_NOT_FOUND,
    ERROR_COMPAT_MISSING_INFO,
    ERROR_COMPAT_NOT_FOUND,
    ERROR_PART_CATALOG_NOT_FOUND,
    ERROR_RAG_NO_DOCS,
    ERROR_ORDER_REQUIRED,
    ERROR_RETURN_REQUIRED,
    ERROR_CLARIFICATION_GENERIC,
    ERROR_FALLBACK,
    MESSAGE_COMPATIBLE,
    MESSAGE_RAG_FOOTER,
    MESSAGE_POLICY_DEFAULT,
)
from app.agent.utils import escape_like, link_metadata, clean_llm_response
from app.agent.db_queries import (
    find_part_by_id,
    find_part_by_mpn,
    find_part_by_model,
    find_part_by_name,
    resolve_part_identifier,
    check_compatibility,
    get_order_with_details,
    get_model_info,
)

logger = logging.getLogger(__name__)


# =====================================================================
#  ONE FAST, SIMPLE LLM CALL HELPER WITH RETRY LOGIC
# =====================================================================

def llm_answer(system_prompt: str, user_prompt: str, context: str = "", max_retries: int = LLM_MAX_RETRIES) -> str:
    """
    Shared helper for all LLM calls (DeepSeek or OpenAI).
    Applies a global style + task-specific instructions + optional CONTEXT.
    Includes retry logic with exponential backoff for transient errors.
    """
    full_system = GLOBAL_STYLE + "\n\n" + system_prompt.strip()

    messages = [{"role": "system", "content": full_system}]

    if context.strip():
        messages.append({"role": "system", "content": f"CONTEXT:\n{context}"})

    messages.append({"role": "user", "content": user_prompt})

    logger.debug("LLM messages: %s", messages)

    client = get_chat_client()
    model = get_default_model()
    
    last_error = None
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=LLM_TEMPERATURE,
            )
            response = completion.choices[0].message.content
            if not response or not response.strip():
                raise ValueError("Empty response from LLM")
            # Clean up any markdown formatting
            return clean_llm_response(response)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = LLM_RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                logger.error(f"LLM call failed after {max_retries} attempts: {e}")
    
    # Fallback response if all retries fail
    error_msg = str(last_error) if last_error else "Unknown error"
    logger.error(f"All LLM retries exhausted. Last error: {error_msg}")
    return ERROR_LLM_FAILED


# =====================================================================
#  RAG SHARED LOGIC (REPAIR / BLOG)
# =====================================================================

def _rag_answer(decision: RouteDecision, preferred_source: str) -> dict:
    docs = retrieve_documents(
        decision.normalized_query,
        top_k=RAG_TOP_K,
        preferred_source=preferred_source,
    )
    logger.info("RAG retrieved %d docs for source=%s", len(docs), preferred_source)

    # Determine links based on preferred_source (intent), not the actual top result
    # This ensures repair queries show repair links, blog queries show blog links
    if preferred_source == "blogs":
        # Blog/how-to queries - show blog-related links
        link_meta = link_metadata(
            [
                {"label": "PartSelect Blog", "url": BLOG_RESOURCES_URL},
                {"label": "Repair Guides", "url": REPAIR_URL},
            ]
        )
        footer_text = "For more usage tips and guides, visit the PartSelect Blog or browse our Repair Guides."
    else:
        # Repair queries - show repair links
        link_meta = link_metadata(
            [
                {"label": "Repair Guides", "url": REPAIR_URL},
                {"label": "Instant Repairman", "url": INSTANT_REPAIRMAN_URL},
                {"label": "Find a Technician", "url": REMOTE_SERVICER_URL},
            ]
        )
        footer_text = MESSAGE_RAG_FOOTER

    if not docs:
        return {"reply": ERROR_RAG_NO_DOCS, "metadata": link_meta}

    context = RAG_CONTEXT_SEPARATOR.join([d["text"] for d in docs])

    # Get LLM response
    llm_response = llm_answer(REPAIR_HELP_PROMPT, decision.normalized_query, context)
    
    reply = f"{llm_response}\n\n{footer_text}"

    return {"reply": reply, "metadata": link_meta}

# ---------------------------------------------------------------------
#  REPAIR HELP
# ---------------------------------------------------------------------

def handle_repair_help(decision: RouteDecision, db: Session) -> dict:
    return _rag_answer(decision, preferred_source="repairs")


# ---------------------------------------------------------------------
#  BLOG / HOW-TO
# ---------------------------------------------------------------------

def handle_blog_howto(decision: RouteDecision, db: Session) -> dict:
    return _rag_answer(decision, preferred_source="blogs")


# =====================================================================
#  PRODUCT INFO (SQL ONLY, ID-FIRST)
# =====================================================================

def handle_product_info(decision: RouteDecision, db: Session) -> str:
    part: Optional[Part] = None

    # 1) Strongest identifier: PartSelect ID.
    if decision.metadata.part_id:
        part = find_part_by_id(db, decision.metadata.part_id)

    # 2) Manufacturer part number.
    if not part and getattr(decision.metadata, "manufacturer_part_number", None):
        mpn = decision.metadata.manufacturer_part_number
        part = find_part_by_mpn(db, mpn)

    # 3) Model-based lookup 
    if not part and decision.metadata.model_number:
        part = find_part_by_model(db, decision.metadata.model_number)

    # 4) Very soft fallback: name fuzzy search
    if not part:
        part = find_part_by_name(db, decision.normalized_query)

    if not part:
        return ERROR_PART_NOT_FOUND

    context = (
        f"PartSelect ID: {part.part_id}\n"
        f"Manufacturer Part Number: {part.manufacturer_part_number}\n"
        f"Name: {part.part_name}\n"
        f"Brand: {part.brand}\n"
        f"Appliance type: {part.appliance_type}\n"
        f"Install difficulty: {part.install_difficulty}\n"
        f"Install time: {part.install_time}\n"
        f"Description and Help: {part.description}\n"
        f"Symptoms: {part.symptoms}\n"
        f"Replace parts: {part.replace_parts}\n"
        f"Price: {part.part_price}\n"
        f"Availability: {part.availability}\n"
        f"URL: {part.product_url}\n"
    )

    metadata = {
        "type": "product_info",
        "product": {
            "id": part.part_id,
            "name": part.part_name,
            "price": str(part.part_price) if part.part_price is not None else None,
            "url": part.product_url,
            "brand": part.brand,
            "applianceType": part.appliance_type,
            "installDifficulty": part.install_difficulty,
            "installTime": part.install_time
        },
    }

    reply_text = llm_answer(PRODUCT_INFO_PROMPT, decision.normalized_query, context)
    return {"reply": reply_text, "metadata": metadata}


# =====================================================================
#  COMPATIBILITY CHECK (SQL ONLY, NO LLM)
# =====================================================================

def handle_compat_check(decision: RouteDecision, db: Session) -> dict:
    part_id = decision.metadata.part_id
    mpn = decision.metadata.manufacturer_part_number
    model_number = decision.metadata.model_number

    if not (part_id or mpn) or not model_number:
        metadata = link_metadata(
            [{"label": "Browse parts", "url": BROWSE_PARTS_URL}]
        )
        return {"reply": ERROR_COMPAT_MISSING_INFO, "metadata": metadata}

    # Resolve the part using either part_id or MPN
    part = resolve_part_identifier(db, part_id, mpn)
    if not part:
        identifier = part_id or mpn or "the part"
        reply = ERROR_PART_CATALOG_NOT_FOUND.format(identifier=identifier)
        metadata = link_metadata(
            [
                {"label": "Browse parts", "url": BROWSE_PARTS_URL},
                {"label": "Contact support", "url": CONTACT_SUPPORT_URL},
            ]
        )
        return {"reply": reply, "metadata": metadata}

    # Check compatibility using the resolved part_id
    is_compatible = check_compatibility(db, part.part_id, model_number)

    if not is_compatible:
        identifier = part_id or mpn or part.part_id
        reply = ERROR_COMPAT_NOT_FOUND.format(
            identifier=identifier,
            model_number=model_number
        )
        metadata = link_metadata(
            [
                {"label": "View product", "url": part.product_url} if part.product_url else {},
                {"label": "Contact support", "url": CUSTOMER_SUPPORT_URL},
            ]
        )
        return {"reply": reply, "metadata": metadata}

    model = get_model_info(db, model_number)
    identifier = part_id or mpn or part.part_id

    reply_lines = [
        MESSAGE_COMPATIBLE.format(
            identifier=identifier,
            part_id=part.part_id,
            model_number=model_number
        ),
    ]
    links = []
    if part.product_url:
        links.append({"label": "View product", "url": part.product_url})
    if model and model.brand:
        reply_lines.append(f"Appliance brand: {model.brand}")

    metadata = link_metadata(links)
    return {"reply": "\n".join(reply_lines), "metadata": metadata}


# =====================================================================
#  ORDER SUPPORT (QUERY DATABASE)
# =====================================================================

def handle_order_support(decision: RouteDecision, db: Session) -> dict:
    """
    Simple order support handler for dummy data.
    Handles: "Track order #1", "What did I order last?", "Was my return accepted?"
    """
    query_lower = decision.normalized_query.lower()
    
    # Extract order_id
    order_id = None
    if decision.metadata.order_id:
        try:
            order_id = int(decision.metadata.order_id)
        except (ValueError, TypeError):
            pass
    
    if not order_id:
        import re
        match = re.search(r'order\s*#?\s*(\d+)', query_lower)
        if match:
            try:
                order_id = int(match.group(1))
            except ValueError:
                pass
    
    # Look up specific order
    if order_id:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            part = db.query(Part).filter(Part.part_id == order.part_id).first() if order.part_id else None
            transaction = db.query(Transaction).filter(Transaction.order_id == order_id).first()
            
            # Build context for LLM
            context_parts = [f"Order #{order.order_id}"]
            context_parts.append(f"Status: {order.order_status.title()}")
            if part:
                context_parts.append(f"Part: {part.part_name} (ID: {part.part_id})")
            if transaction:
                context_parts.append(f"Amount: ${transaction.amount}")
                context_parts.append(f"Payment status: {transaction.status}")
            if order.shipping_type:
                context_parts.append(f"Shipping: {order.shipping_type}")
            if order.order_date:
                context_parts.append(f"Order date: {order.order_date.strftime('%B %d, %Y')}")
            if order.return_eligible:
                context_parts.append("Return eligible: Yes")
            
            context = "\n".join(context_parts)
            
            # Generate contextual reply
            reply_text = llm_answer(ORDER_SUPPORT_PROMPT, decision.normalized_query, context)
            
            # Return with metadata for order card
            metadata = {
                "type": "order_info",
                "order": {
                    "id": order.order_id,
                    "status": order.order_status,
                    "date": order.order_date.isoformat() if order.order_date else None,
                    "shippingType": order.shipping_type,
                    "partName": part.part_name if part else None,
                    "partId": part.part_id if part else None,
                    "partUrl": part.product_url if part else None,
                    "amount": str(transaction.amount) if transaction else None,
                    "transactionStatus": transaction.status if transaction else None,
                    "returnEligible": order.return_eligible,
                },
            }
            return {"reply": reply_text, "metadata": metadata}
        return {"reply": f"Order #{order_id} not found.", "metadata": None}
    
    # "What did I order last?" - requires order ID
    if any(p in query_lower for p in ["last order", "my order", "what did i order"]):
        return {
            "reply": ERROR_ORDER_REQUIRED,
            "metadata": None
        }
    
    # "Was my return accepted?" - requires order ID
    if "return" in query_lower or "refund" in query_lower:
        if order_id:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order and order.order_status == "returned":
                txn = db.query(Transaction).filter(Transaction.order_id == order_id).first()
                if txn and txn.status == "refunded":
                    return {"reply": f"Yes, your return for order #{order_id} was accepted. Refund: ${txn.amount}", "metadata": None}
                return {"reply": f"Return for order #{order_id} is being processed.", "metadata": None}
            elif order:
                return {"reply": f"Order #{order_id} is not marked as returned.", "metadata": None}
            else:
                return {"reply": f"Order #{order_id} not found.", "metadata": None}
        
        return {
            "reply": ERROR_RETURN_REQUIRED,
            "metadata": None
        }
    
    # Fallback
    return {
        "reply": ERROR_ORDER_REQUIRED,
        "metadata": None
    }




# =====================================================================
#  POLICY / WHY SHOP HERE (STATIC URLS)
# =====================================================================

def handle_policy(decision: RouteDecision, db: Session) -> dict:
    """
    Return static policy page URLs based on query keywords.
    Only handles policy information, not order return status.
    """
    query_lower = decision.normalized_query.lower()
    
    # Map keywords to specific policy URLs
    default_links = [
        {"label": "Fast Shipping", "url": SHIPPING_URL},
        {"label": "365-Day Returns", "url": RETURNS_POLICY_URL},
        {"label": "One-Year Warranty", "url": WARRANTY_URL},
        {"label": "Price Match", "url": PRICE_MATCH_URL},
    ]

    if "policy" in query_lower or "return window" in query_lower:
        reply = "You can review our 365-Day Returns policy online."
        links = [{"label": "365-Day Returns", "url": RETURNS_POLICY_URL}]
    elif "warranty" in query_lower or "guarantee" in query_lower:
        reply = "Here's a quick look at our One-Year Warranty."
        links = [{"label": "One-Year Warranty", "url": WARRANTY_URL}]
    elif "shipping" in query_lower or "fast shipping" in query_lower:
        reply = "We offer fast shipping on many parts—details are below."
        links = [{"label": "Fast Shipping", "url": SHIPPING_URL}]
    elif "price match" in query_lower:
        reply = "We do offer price matching. See the guidelines:"
        links = [{"label": "Price Match", "url": PRICE_MATCH_URL}]
    else:
        return {"reply": MESSAGE_POLICY_DEFAULT, "metadata": link_metadata(default_links)}

    return {"reply": reply, "metadata": link_metadata(links)}


# =====================================================================
#  OUT OF SCOPE
# =====================================================================

def handle_out_of_scope(decision: RouteDecision, db: Session) -> str:
    return (
        "I can help with refrigerator and dishwasher parts, "
        "repair troubleshooting, and customer transactions "
        "(order tracking, returns, etc.). I can't assist with questions outside of that scope.\n\n"
        "For other inquiries, please visit PartSelect.com or contact our support team."
    )


# =====================================================================
#  CLARIFICATION
# =====================================================================

def handle_clarification(decision: RouteDecision, db: Session) -> str:
    missing = decision.metadata.missing_fields or []
    prompts = []

    if "part_id" in missing:
        prompts.append("the PartSelect part ID (for example PS11752778)")
    if "model_number" in missing:
        prompts.append("the appliance model number (usually on a label inside the door frame)")
    if "order_id" in missing:
        prompts.append("your order number so I can talk about status/returns")

    if not prompts:
        return ERROR_CLARIFICATION_GENERIC

    return "To help with that, please provide " + "; ".join(prompts) + "."
