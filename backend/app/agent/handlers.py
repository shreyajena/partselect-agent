from __future__ import annotations
import logging
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Part, PartModelMapping, Model, User, Order, Transaction
from app.rag.retrieval import retrieve_documents
from app.llm.client import get_chat_client, get_default_model
from app.router.intents import RouteDecision


def _escape_like(term: str) -> str:
    """Escape LIKE wildcards to reduce injection risk."""
    return (
        term.replace("\\", "\\\\")
        .replace("%", r"\%")
        .replace("_", r"\_")
    )

logger = logging.getLogger(__name__)

# =====================================================================
#  GLOBAL ASSISTANT STYLE
# =====================================================================

GLOBAL_STYLE = """
You are the PartSelect helper bot for refrigerator and dishwasher questions.
Be friendly, concise, and practical.
Base every answer ONLY on the structured data or context provided.
Keep answers short (about 2–4 sentences, max ~120 words).
If you are unsure, say so and point the user to the relevant PartSelect page.
End every answer with the sentence: "Source: PartSelect data."
"""


# =====================================================================
#  ONE FAST, SIMPLE LLM CALL HELPER WITH RETRY LOGIC
# =====================================================================

def llm_answer(system_prompt: str, user_prompt: str, context: str = "", max_retries: int = 3) -> str:
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
                temperature=0.5,
            )
            response = completion.choices[0].message.content
            if not response or not response.strip():
                raise ValueError("Empty response from LLM")
            return response
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
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
    return (
        "I'm having trouble processing that right now. "
        "Please try again in a moment, or visit PartSelect.com for immediate assistance."
    )


# =====================================================================
#  RAG SHARED LOGIC (REPAIR / BLOG)
# =====================================================================

def _rag_answer(decision: RouteDecision, preferred_source: str) -> str:
    docs = retrieve_documents(
        decision.normalized_query,
        top_k=6,
        preferred_source=preferred_source,
    )
    logger.info("RAG retrieved %d docs for source=%s", len(docs), preferred_source)

    # Define repair URLs
    REPAIR_URL = "https://www.partselect.com/Repair/"
    INSTANT_REPAIRMAN_URL = "https://www.partselect.com/Instant-Repairman/"

    if not docs:
        # fallback when vector store is empty or miss
        return (
            "I couldn't find enough local repair information for that. "
            f"You can get detailed step-by-step help on PartSelect's repair pages: "
            f"{REPAIR_URL} or the Instant Repairman tool: {INSTANT_REPAIRMAN_URL}"
        )

    context = "\n\n---\n\n".join([d["text"] for d in docs])

    system_prompt = """
You are helping with repair troubleshooting for refrigerators and dishwashers ONLY.

CRITICAL: Only answer if the question is about a refrigerator or dishwasher. 
If the question is about any other appliance (TV, microwave, oven, etc.), politely decline and say you can only help with refrigerators and dishwashers.

If the context describes a repair for a refrigerator or dishwasher:
- List 2–3 likely causes and 2–3 safe checks or steps from the context.
- Emphasize unplugging / cutting power and when to call a technician.
- Keep the answer tight and practical (2-3 sentences maximum).
- ONLY use information from the provided context. Do NOT make assumptions.

If the context is more about usage, modes, or cycles:
- Briefly explain what the context says in plain language.
- Give 1–2 practical tips from the context.

Always mention that the advice comes from the PartSelect guides.
If the context doesn't have enough information, keep your answer short.
"""


    # Get LLM response
    llm_response = llm_answer(system_prompt, decision.normalized_query, context)
    
    # Always append repair URLs
    return (
        f"{llm_response}\n\n"
        f"For more detailed repair guides, visit: {REPAIR_URL}\n"
        f"Or use our Instant Repairman tool: {INSTANT_REPAIRMAN_URL}"
    )


# ---------------------------------------------------------------------
#  REPAIR HELP
# ---------------------------------------------------------------------

def handle_repair_help(decision: RouteDecision, db: Session) -> str:
    return _rag_answer(decision, preferred_source="repairs")


# ---------------------------------------------------------------------
#  BLOG / HOW-TO
# ---------------------------------------------------------------------

def handle_blog_howto(decision: RouteDecision, db: Session) -> str:
    return _rag_answer(decision, preferred_source="blogs")


# =====================================================================
#  PRODUCT INFO (SQL ONLY, ID-FIRST)
# =====================================================================

def handle_product_info(decision: RouteDecision, db: Session) -> str:
    part: Optional[Part] = None

    # 1) Strongest identifier: PartSelect ID.
    if decision.metadata.part_id:
        part = db.query(Part).filter(Part.part_id == decision.metadata.part_id).one_or_none()

    # 2) Manufacturer part number.
    if not part and getattr(decision.metadata, "manufacturer_part_number", None):
        mpn = decision.metadata.manufacturer_part_number
        escaped_mpn = _escape_like(mpn)
        part = (
            db.query(Part)
            .filter(Part.manufacturer_part_number.ilike(f"%{escaped_mpn}%", escape="\\"))
            .first()
        )

    # 3) Model-based lookup (optional, if you wired a relation).
    if not part and decision.metadata.model_number:
        model_number = decision.metadata.model_number
        part = (
            db.query(Part)
            .join(PartModelMapping, Part.part_id == PartModelMapping.part_id)
            .join(Model, Model.model_number == PartModelMapping.model_number)
            .filter(Model.model_number == model_number)
            .first()
        )

    # 4) Very soft fallback: name fuzzy search.
    if not part:
        fuzzy_query = _escape_like(decision.normalized_query)
        part = (
            db.query(Part)
            .filter(Part.part_name.ilike(f"%{fuzzy_query}%", escape="\\"))
            .first()
        )

    if not part:
        return (
            "I couldn't find that part in my local PartSelect catalog. "
            "Could you double-check the part ID or share the product page URL?"
        )

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

    system_prompt = """
You are a PartSelect parts expert.  
Base your answer ONLY on the structured part context provided below.  
Never use outside knowledge, never invent symptoms, steps, or claims.

Follow these rules depending on the user’s question:

1) If the user asks “what is this part / what does it do?”:
   - Explain the part’s function using the description field.
   - Mention one or two symptoms from the symptoms list if relevant.

2) If the user asks about installation (“how to install / replace it”):
   - Give a very SHORT 1–2 sentence installation summary based on the 
     install_difficulty + install_time + description fields.
   - Do NOT guess model-specific steps.
   - If the part is “easy / tool-free”, mention that.

3) If the user describes a problem (“leaking / won’t dispense ice / door won’t close”):
   - Check if that symptom appears in the part’s symptom list.
   - If yes: confirm that this part commonly fixes that issue.
   - If no: politely say the context does not list that symptom.

4) ALWAYS:
   - Keep the entire answer within 2–4 sentences.
   - Be friendly and conversational.
   - End with: “You can confirm fit and see full details here: <URL>”.

Keep it to 2–4 sentences total.

Do not mention any fields that are empty or missing.
Do NOT list the entire symptom list unless directly relevant.
Only use what is in the provided SQL context.
"""

    return llm_answer(system_prompt, decision.normalized_query, context)


# =====================================================================
#  COMPATIBILITY CHECK (SQL ONLY, NO LLM)
# =====================================================================
def resolve_part_identifier(db: Session, part_id: str | None, mpn: str | None):
    """
    Return a Part object if either part_id or MPN matches.
    Prefer explicit PartSelect ID if available.
    """
    if part_id:
        part = db.query(Part).filter(Part.part_id == part_id).one_or_none()
        if part:
            return part
    
    if mpn:
        part = (
            db.query(Part)
            .filter(Part.manufacturer_part_number.ilike(f"%{mpn}%"))
            .first()
        )
        if part:
            return part

    return None


def handle_compat_check(decision: RouteDecision, db: Session) -> str:
    part_id = decision.metadata.part_id
    mpn = decision.metadata.manufacturer_part_number
    model_number = decision.metadata.model_number

    if not (part_id or mpn) or not model_number:
        return (
            "To check compatibility I need both:\n"
            "- a PartSelect part ID (for example PS11752778) or manufacturer part number, and\n"
            "- your appliance model number (for example WDT780SAEM1)."
        )

    # Resolve the part using either part_id or MPN
    part = resolve_part_identifier(db, part_id, mpn)
    if not part:
        identifier = part_id or mpn or "the part"
        return (
            f"I couldn't find {identifier} in my catalog. "
            "Please double-check the part number or share the PartSelect product page URL."
        )

    # Check compatibility using the resolved part_id
    compat = (
        db.query(PartModelMapping)
        .filter(
            PartModelMapping.part_id == part.part_id,
            PartModelMapping.model_number == model_number,
        )
        .one_or_none()
    )

    if not compat:
        identifier = part_id or mpn or part.part_id
        return (
            f"I don't see {identifier} listed as compatible with model {model_number}. "
            "Please double-check on the PartSelect product page "
            "or with support before ordering."
        )

    model = db.query(Model).filter(Model.model_number == model_number).one_or_none()
    identifier = part_id or mpn or part.part_id

    reply_lines = [
        f"Based on my compatibility data, part {identifier} (PartSelect ID: {part.part_id}) "
        f"is compatible with model {model_number}.",
    ]
    if part and part.product_url:
        reply_lines.append(f"You can review and buy it here: {part.product_url}")
    if model and model.brand:
        reply_lines.append(f"Appliance brand: {model.brand}")

    return "\n".join(reply_lines)


# =====================================================================
#  ORDER SUPPORT (QUERY DATABASE)
# =====================================================================

def handle_order_support(decision: RouteDecision, db: Session) -> str:
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
            
            lines = [f"Order #{order.order_id}: {order.order_status.title()}"]
            if part:
                lines.append(f"Part: {part.part_name}")
            if transaction:
                lines.append(f"Amount: ${transaction.amount}")
            if order.shipping_type:
                lines.append(f"Shipping: {order.shipping_type}")
            return "\n".join(lines)
        return f"Order #{order_id} not found."
    
    # "What did I order last?" - requires order ID
    if any(p in query_lower for p in ["last order", "my order", "what did i order"]):
        return (
            "To check your orders, please provide your order number.\n"
            "For example: 'Track order #1' or 'What is the status of order #2?'"
        )
    
    # "Was my return accepted?" - requires order ID
    if "return" in query_lower or "refund" in query_lower:
        if order_id:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order and order.order_status == "returned":
                txn = db.query(Transaction).filter(Transaction.order_id == order_id).first()
                if txn and txn.status == "refunded":
                    return f"Yes, your return for order #{order_id} was accepted. Refund: ${txn.amount}"
                return f"Return for order #{order_id} is being processed."
            elif order:
                return f"Order #{order_id} is not marked as returned."
            else:
                return f"Order #{order_id} not found."
        
        return (
            "To check your return status, please provide your order number.\n"
            "For example: 'Was my return accepted for order #3?'"
        )
    
    # Fallback
    return (
        "I can help with order tracking. Please provide your order number.\n"
        "For example: 'Track order #1' or 'What is the status of order #2?'"
    )




# =====================================================================
#  POLICY / WHY SHOP HERE (STATIC URLS)
# =====================================================================

def handle_policy(decision: RouteDecision, db: Session) -> str:
    """
    Return static policy page URLs based on query keywords.
    Only handles policy information, not order return status.
    """
    query_lower = decision.normalized_query.lower()
    
    # Map keywords to specific policy URLs
    # Only match explicit policy questions
    if "return policy" in query_lower or "return window" in query_lower:
        url = "https://www.partselect.com/365-Day-Returns.htm"
        policy_name = "365-Day Returns"
    elif "warranty" in query_lower or "guarantee" in query_lower:
        url = "https://www.partselect.com/One-Year-Warranty.htm"
        policy_name = "One-Year Warranty"
    elif "shipping" in query_lower or "fast shipping" in query_lower:
        url = "https://www.partselect.com/Fast-Shipping.htm"
        policy_name = "Fast Shipping"
    elif "price match" in query_lower:
        url = "https://www.partselect.com/Price-Match.htm"
        policy_name = "Price Match"
    else:
        # Default: return all policy links
        return (
            "Here are our key policies:\n\n"
            "• Fast Shipping: https://www.partselect.com/Fast-Shipping.htm\n"
            "• 365-Day Returns: https://www.partselect.com/365-Day-Returns.htm\n"
            "• One-Year Warranty: https://www.partselect.com/One-Year-Warranty.htm\n"
            "• Price Match: https://www.partselect.com/Price-Match.htm"
        )
    
    return (
        f"For information about our {policy_name} policy, please visit:\n"
        f"{url}"
    )


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
        return (
            "I need a bit more information to help. "
            "Could you share which appliance this is for, the model number, "
            "and any part IDs or a link to the PartSelect page?"
        )

    return "To help with that, please provide " + "; ".join(prompts) + "."
