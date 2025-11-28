from __future__ import annotations
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Part, PartModelMapping, Model
from app.rag.retrieval import retrieve_documents
from app.llm.client import get_chat_client, get_default_model
from app.router.intents import RouteDecision

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
"""


# =====================================================================
#  ONE FAST, SIMPLE LLM CALL HELPER
# =====================================================================

def llm_answer(system_prompt: str, user_prompt: str, context: str = "") -> str:
    """
    Shared helper for all LLM calls (DeepSeek or OpenAI).
    Applies a global style + task-specific instructions + optional CONTEXT.
    """
    full_system = GLOBAL_STYLE + "\n\n" + system_prompt.strip()

    messages = [{"role": "system", "content": full_system}]

    if context.strip():
        messages.append({"role": "system", "content": f"CONTEXT:\n{context}"})

    messages.append({"role": "user", "content": user_prompt})

    logger.debug("LLM messages: %s", messages)

    completion = get_chat_client().chat.completions.create(
        model=get_default_model(),
        messages=messages,
        temperature=0.5,
    )
    return completion.choices[0].message.content


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

    if not docs:
        # fallback when vector store is empty or miss
        return (
            "I couldn't find enough local repair information for that. "
            "You can get detailed step-by-step help on PartSelect’s repair pages: "
            "https://www.partselect.com/Repair/ or the Instant Repairman tool: "
            "https://www.partselect.com/Instant-Repairman/."
        )

    context = "\n\n---\n\n".join([d["text"] for d in docs])

    system_prompt = """
You are helping with either repair troubleshooting or usage/maintenance,
depending on what the context describes.

If the context clearly describes a repair for this symptom:
- List 2–3 likely causes and 2–4 safe checks or steps.
- Emphasize unplugging / cutting power and when to call a technician.
- Keep the answer tight and practical.

If the context is more about usage, modes, or cycles:
- Briefly explain what it means in plain language.
- Give 1–2 practical tips for when and how to use it.

Always mention that the advice comes from the PartSelect guides.
At the end, in one short sentence, you may point them to the full repair resources:
the main Repair section(https://www.partselect.com/Repair/) or Instant Repairman ("https://www.partselect.com/Instant-Repairman/.") on PartSelect.
"""

    return llm_answer(system_prompt, decision.normalized_query, context)


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
        part = (
            db.query(Part)
            .filter(Part.manufacturer_part_number.ilike(f"%{mpn}%"))
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
        part = (
            db.query(Part)
            .filter(Part.part_name.ilike(f"%{decision.normalized_query}%"))
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
    model_number = decision.metadata.model_number

    if not (part_id or mpn) or not model_number:
        return (
            "To check compatibility I need both:\n"
            "- a PartSelect part ID (for example PS11752778), and\n"
            "- your appliance model number (for example WDT780SAEM1)."
        )

    compat = (
        db.query(PartModelMapping)
        .filter(
            PartModelMapping.part_id == part_id,
            PartModelMapping.model_number == model_number,
        )
        .one_or_none()
    )

    if not compat:
        return (
            f"I don't see {part_id} listed as compatible with model {model_number} "
            "Please double-check on the PartSelect product page"
            "or with the support before ordering."
        )

    part = db.query(Part).filter(Part.part_id == part_id).one_or_none()
    model = db.query(Model).filter(Model.model_number == model_number).one_or_none()

    reply_lines = [
        f"Based on my compatibility data, part {part_id} is compatible with model {model_number}.",
    ]
    if part and part.product_url:
        reply_lines.append(f"You can review and buy it here: {part.product_url}")
    if model and model.brand:
        reply_lines.append(f"Appliance brand: {model.brand}")

    return "\n".join(reply_lines)


# =====================================================================
#  ORDER SUPPORT (STATIC / NO REAL ORDERS)
# =====================================================================

def handle_order_support(decision: RouteDecision, db: Session) -> str:
    system_prompt = """
You are an order-support explainer for PartSelect.
We do NOT have access to real accounts or orders here.

Using only this limitation:
- Explain what customers normally see (order status, shipping, returns).
- Give 2–3 short steps for how they would check this in a real PartSelect account.
- Keep it high-level and under ~120 words.
"""
    return llm_answer(system_prompt, decision.normalized_query)


# =====================================================================
#  POLICY / WHY SHOP HERE (STATIC)
# =====================================================================

def handle_policy(decision: RouteDecision, db: Session) -> str:
    context = """
Why Shop at PartSelect (demo only, not official text):
- OEM refrigerator & dishwasher parts
- Fast shipping on many items
- 365-day returns on most parts (example only)
- Secure online checkout
- Repair guides and videos
- Live phone/chat support

Return denial examples (demo only):
- Installed electrical parts
- Parts damaged by incorrect installation
- Returns outside the allowed window
"""

    system_prompt = """
You are explaining PartSelect-style policies at a high level.
Use ONLY the provided bullets; do NOT invent exact legal guarantees.

Give a short, friendly summary (2–3 sentences max).
You may list 2–3 bullet points if it feels clearer.
"""

    return llm_answer(system_prompt, decision.normalized_query, context)


# =====================================================================
#  SMALL TALK (NO LLM)
# =====================================================================

def handle_small_talk(decision: RouteDecision, db: Session) -> str:
    q = decision.normalized_query.lower()

    if "thank" in q:
        return "You're welcome! If you tell me your fridge or dishwasher issue, I can help you find parts or repair steps."
    if "hi" in q or "hello" in q or "hey" in q:
        return "Hi! I’m the PartSelect helper bot. I can help with parts, compatibility, and basic repair tips."

    return "I’m here for refrigerator and dishwasher questions—what are you working on?"


# =====================================================================
#  OUT OF SCOPE
# =====================================================================

def handle_out_of_scope(decision: RouteDecision, db: Session) -> str:
    return (
        "I’m designed specifically for refrigerator and dishwasher parts, "
        "compatibility, and repair/usage guidance, so I can’t answer that one."
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
