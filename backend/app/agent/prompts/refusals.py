"""Fixed, non-LLM responses used when the agent cannot or must not answer."""

INJECTION_REFUSAL = (
    "I can't help with that request. I'm the OmniCare assistant and can only answer policy "
    "coverage questions, check a claim status, or submit a new claim. How can I help with one of those?"
)

STEP_LIMIT_RESPONSE = (
    "I'm sorry, that request needed more steps than I'm allowed to take. Please simplify it and try again."
)

EMPTY_ANSWER_FALLBACK = "I'm sorry, I couldn't complete that request. Could you rephrase or try again?"
