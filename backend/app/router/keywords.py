# app/router/keywords.py
"""
Static keyword lists for intent routing.
"""

# Policy-related keywords
POLICY_KEYWORDS = [
    "return policy",
    "return window",
    "policy",
    "why shop",
    "warranty",
    "guarantee",
    "shipping policy",
    "price match",
]

# Order support keywords
ORDER_KEYWORDS = [
    "order",
    "ordr",
    "oder",
    "oroder",
    "tracking",
    "track shipment",
    "track",
    "shipment",
    "shipping",
    "my order",
    "order status",
    "refund my",
    "my return",
    "return status",
    "is my return",
    "return my order",
    "need to return",
]

# Compatibility check keywords
COMPAT_KEYWORDS = [
    "compatible",
    "fit",
    "work with",
]

# General repair words (for appliance type + repair detection)
GENERAL_REPAIR_WORDS = [
    "repair",
    "fix",
    "broken",
    "issue",
    "problem",
    "trouble",
    "not working",
    "malfunction",
    "error",
    "fault",
    "check",
    "what should",
    "what to do",
    "help with",
]

# Specific repair symptom keywords
REPAIR_KEYWORDS = [
    "leak",
    "leaking",
    "noisy",
    "noise",
    "won't start",
    "wont start",
    "not starting",
    "not working",
    "stopped working",
    "not dispensing",
    "not making ice",
    "warm",
    "too warm",
    "not cooling",
    "not cold",
    "freezing up",
    "icing up",
    "smell",
    "odor",
    "won't fill",
    "wont fill",
    "won't drain",
    "wont drain",
    "drain",
    "draining",
    "stuck",
    "jammed",
    "overflow",
    "flooding",
]

# How-to / usage keywords
HOWTO_KEYWORDS = [
    "how to",
    "how do i",
    "what is",
    "what does",
    "explain",
    "cycle",
    "mode",
    "eco",
    "sanitize",
    "quick wash",
    "settings",
    "reset",
    "clean cycle",
]

