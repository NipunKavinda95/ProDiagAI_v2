import re
from typing import Any

MAX_COPILOT_QUESTION_LENGTH = 1000
MAX_CONVERSATION_MESSAGES = 20
MAX_MESSAGE_LENGTH = 2000


def validate_copilot_question(question: Any) -> str:
    if not isinstance(question, str):
        raise ValueError("Engineer question must be text.")

    question = question.strip()

    if not question:
        raise ValueError("Engineer question is required.")

    if len(question) > MAX_COPILOT_QUESTION_LENGTH:
        raise ValueError(
            f"Engineer question must be {MAX_COPILOT_QUESTION_LENGTH} "
            "characters or fewer."
        )

    # Remove control characters while preserving normal
    # engineering text, punctuation and units.
    question = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", " ", question)

    question = re.sub(r"\s+", " ", question).strip()

    if detect_prompt_injection(question):
        raise ValueError("The request contains an unsupported instruction pattern.")

    return question


def validate_conversation_history(history: Any) -> list[dict[str, str]]:
    if history is None:
        return []

    if not isinstance(history, list):
        raise ValueError("conversation_history must be a list.")

    if len(history) > MAX_CONVERSATION_MESSAGES:
        raise ValueError(
            f"conversation_history cannot contain more than "
            f"{MAX_CONVERSATION_MESSAGES} messages."
        )

    validated_messages: list[dict[str, str]] = []

    for message in history:
        if not isinstance(message, dict):
            raise ValueError("Each conversation message must be an object.")

        role = message.get("role")
        content = message.get("content")

        if role not in {"user", "assistant"}:
            raise ValueError("Conversation message role must be user or assistant.")

        if not isinstance(content, str):
            raise ValueError("Conversation message content must be text.")

        content = content.strip()

        if not content:
            raise ValueError("Conversation message content cannot be empty.")

        if len(content) > MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"Conversation messages must be "
                f"{MAX_MESSAGE_LENGTH} characters or fewer."
            )

        content = re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
            " ",
            content,
        )

        content = re.sub(r"\s+", " ", content).strip()

        validated_messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    return validated_messages


PROMPT_INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?previous\s+instructions\b",
    r"\bignore\s+(all\s+)?prior\s+instructions\b",
    r"\bdisregard\s+(all\s+)?previous\s+instructions\b",
    r"\bdisregard\s+(all\s+)?prior\s+instructions\b",
    r"\boverride\s+(the\s+)?system\s+instructions\b",
    r"\boverride\s+(the\s+)?developer\s+instructions\b",
    r"\breveal\s+(the\s+)?system\s+prompt\b",
    r"\bshow\s+(me\s+)?(the\s+)?system\s+prompt\b",
    r"\breveal\s+(the\s+)?developer\s+prompt\b",
    r"\bshow\s+(me\s+)?(the\s+)?developer\s+prompt\b",
    r"\bprint\s+(the\s+)?system\s+prompt\b",
    r"\bwhat\s+are\s+your\s+hidden\s+instructions\b",
    r"\bshow\s+(me\s+)?your\s+hidden\s+instructions\b",
    r"\breveal\s+(the\s+)?api\s+key\b",
    r"\bshow\s+(me\s+)?the\s+api\s+key\b",
    r"\breveal\s+(the\s+)?environment\s+variables\b",
    r"\bshow\s+(me\s+)?the\s+environment\s+variables\b",
    r"\bdeveloper\s+message\b",
    r"\bsystem\s+message\b",
    r"\bjailbreak\b",
]


def detect_prompt_injection(question: str) -> bool:
    """
    Detect common prompt-injection attempts in engineer input.

    This is a lightweight safety layer. It does not replace
    the system prompt or model-level safety controls.
    """
    if not isinstance(question, str):
        return False

    normalized_question = re.sub(
        r"\s+",
        " ",
        question.lower().strip(),
    )

    return any(
        re.search(pattern, normalized_question) for pattern in PROMPT_INJECTION_PATTERNS
    )


def validate_copilot_response(response: Any) -> dict:
    if not isinstance(response, dict):
        raise ValueError("AI response must be an object.")

    required_fields = {
        "summary",
        "diagnosis",
        "confidence",
        "evidence",
        "recommendations",
        "urgency",
        "safety_note",
        "sources",
    }

    missing_fields = required_fields - response.keys()

    if missing_fields:
        raise ValueError(
            f"AI response is missing required fields: "
            f"{', '.join(sorted(missing_fields))}"
        )

    if not isinstance(response["summary"], str):
        raise ValueError("AI response summary must be text.")

    if not isinstance(response["diagnosis"], str):
        raise ValueError("AI response diagnosis must be text.")

    if len(response["summary"]) > 2000:
        raise ValueError("AI response summary is too long.")

    if len(response["diagnosis"]) > 3000:
        raise ValueError("AI response diagnosis is too long.")

    if response["confidence"] not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError("AI response confidence is invalid.")

    if not isinstance(response["evidence"], list):
        raise ValueError("AI response evidence must be a list.")

    if not isinstance(response["recommendations"], list):
        raise ValueError("AI response recommendations must be a list.")

    if not isinstance(response["sources"], list):
        raise ValueError("AI response sources must be a list.")

    for item in response["evidence"]:
        if not isinstance(item, str):
            raise ValueError("AI response evidence items must be text.")
        if len(item) > 2000:
            raise ValueError("AI response evidence item is too long.")

    for item in response["recommendations"]:
        if not isinstance(item, str):
            raise ValueError("AI response recommendation items must be text.")
        if len(item) > 2000:
            raise ValueError("AI response recommendation item is too long.")

    for item in response["sources"]:
        if not isinstance(item, str):
            raise ValueError("AI response source items must be text.")
        if len(item) > 1000:
            raise ValueError("AI response source item is too long.")

    if response["urgency"] not in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }:
        raise ValueError("AI response urgency is invalid.")

    if not isinstance(response["safety_note"], str):
        raise ValueError("AI response safety_note must be text.")

    if len(response["safety_note"]) > 2000:
        raise ValueError("AI response safety_note is too long.")

    return response


def validate_ai_diagnosis_response(response: Any) -> dict:
    if not isinstance(response, dict):
        raise ValueError("AI diagnosis response must be an object.")

    required_fields = {
        "diagnosis",
        "probable_fault",
        "confidence",
        "evidence",
        "recommended_actions",
        "urgency",
        "requires_escalation",
    }

    missing_fields = required_fields - response.keys()

    if missing_fields:
        raise ValueError(
            f"AI diagnosis response is missing required fields: "
            f"{', '.join(sorted(missing_fields))}"
        )

    if not isinstance(response["diagnosis"], str):
        raise ValueError("AI diagnosis must be text.")

    if not isinstance(response["probable_fault"], str):
        raise ValueError("AI probable fault must be text.")

    if not isinstance(response["confidence"], (int, float)):
        raise ValueError("AI diagnosis confidence must be numeric.")

    if not 0 <= response["confidence"] <= 100:
        raise ValueError("AI diagnosis confidence must be between 0 and 100.")

    if not isinstance(response["evidence"], list):
        raise ValueError("AI diagnosis evidence must be a list.")

    if not isinstance(response["recommended_actions"], list):
        raise ValueError("AI recommended actions must be a list.")

    if response["urgency"] not in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }:
        raise ValueError("AI diagnosis urgency is invalid.")

    if not isinstance(response["requires_escalation"], bool):
        raise ValueError("AI diagnosis requires_escalation must be boolean.")

    return response
