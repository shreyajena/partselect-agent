# app/config/constants.py
"""
Application constants and configuration values.
"""

# LLM Settings
LLM_MAX_RETRIES = 3
LLM_TEMPERATURE = 0.5
LLM_RETRY_BACKOFF_BASE = 2  # Exponential backoff: 2^attempt seconds

# RAG Settings
RAG_TOP_K = 6
RAG_CONTEXT_SEPARATOR = "\n\n---\n\n"

# Error Messages
ERROR_LLM_FAILED = (
    "I'm having trouble processing that right now. "
    "Please try again in a moment, or visit PartSelect.com for immediate assistance."
)

ERROR_PART_NOT_FOUND = (
    "I couldn't find that part in my local PartSelect catalog. "
    "Could you double-check the part ID or share the product page URL?"
)

ERROR_ORDER_NOT_FOUND = "Order #{order_id} not found."

ERROR_COMPAT_MISSING_INFO = (
    "To check compatibility I need both:\n"
    "- a PartSelect part ID (for example PS11752778) or manufacturer part number, and\n"
    "- your appliance model number (for example WDT780SAEM1)."
)

ERROR_COMPAT_NOT_FOUND = (
    "I don't see {identifier} listed as compatible with model {model_number}. "
    "Please double-check on the PartSelect product page or with support before ordering."
)

ERROR_PART_CATALOG_NOT_FOUND = (
    "I couldn't find {identifier} in my catalog. "
    "Please double-check the part number or share the PartSelect product page URL."
)

ERROR_RAG_NO_DOCS = (
    "I couldn't find enough local repair information for that. "
    "You can get detailed step-by-step help on PartSelect's repair pages "
    "or use the Instant Repairman tool."
)

ERROR_ORDER_REQUIRED = (
    "To check your orders, please provide your order number.\n"
    "For example: 'Track order #1' or 'What is the status of order #2?'"
)

ERROR_RETURN_REQUIRED = (
    "To check your return status, please provide your order number.\n"
    "For example: 'Was my return accepted for order #3?'"
)

ERROR_CLARIFICATION_GENERIC = (
    "I need a bit more information to help. "
    "Could you share which appliance this is for, the model number, "
    "and any Part IDs or a link to the PartSelect page?"
)

ERROR_FALLBACK = (
    "I'm not entirely sure how to handle that. "
    "I'm best at refrigerator and dishwasher parts, compatibility, and repair help. "
    "Could you rephrase your question with a bit more detail?"
)

# Response Messages
MESSAGE_COMPATIBLE = (
    "Based on my compatibility data, part {identifier} (PartSelect ID: {part_id}) "
    "is compatible with model {model_number}."
)

MESSAGE_RAG_FOOTER = (
    "For more detailed repair guides, visit PartSelect's Repair page or use the Instant Repairman tool."
)

MESSAGE_POLICY_DEFAULT = "Here are our key policies. Tap any link to learn more:"

