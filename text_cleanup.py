import re


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def should_remove_paragraph(text: str) -> bool:
    """
    Decide whether a paragraph should be removed entirely from output.

    This function is intentionally aggressive:
    - removes boilerplate, CTAs, legal text
    - removes community / engagement sections
    - removes orphaned punctuation left behind by HTML cleanup
    """
    norm = _normalize(text)

    # ------------------------------------------------------------
    # DROP ORPHANED PUNCTUATION / QUOTES
    # ------------------------------------------------------------
    # Examples:
    #   ","
    #   "."
    #   "“"
    #   ".”"
    if re.fullmatch(r"[.,;:!?\"'“”‘’()\[\]\-–—…]+", norm):
        return True

    # ------------------------------------------------------------
    # HARD REMOVALS — NEVER EDITORIAL
    # ------------------------------------------------------------

    # Newsletter tagline
    if norm.startswith("a weekly newsletter by david pierce"):
        return True

    # Email delivery / recipient boilerplate
    if (
        norm.startswith("you’re receiving this email")
        or norm.startswith("this email was sent to")
    ):
        return True

    # Vox Media legal / affiliate boilerplate
    legal_signals = [
        "vox media has affiliate partnerships",
        "do not influence editorial content",
        "ethics policy",
        "privacy policy",
        "terms of service",
        "all rights reserved",
        "vox media,",
    ]
    if any(s in norm for s in legal_signals):
        return True

    # Generic unsubscribe boilerplate
    if "unsubscribe" in norm and "installer" not in norm:
        return True

    # ------------------------------------------------------------
    # INSTALLER COMMUNITY / CTA BLOCKS
    # ------------------------------------------------------------

    # Block A: "best part of Installer" CTA
    installer_cta_signals = [
        "best part of installer",
        "your ideas and tips",
        "what are you reading",
        "what are you watching",
        "what are you playing",
        "what are you building",
        "what are you snacking",
        "tell me everything",
        "forward it to them",
        "subscribe here",
    ]
    if any(s in norm for s in installer_cta_signals):
        return True

    # Block B: "Installer community" recommendations intro
    installer_community_signals = [
        "installer community",
        "what you’re into",
        "feature some of our favorites",
        "email installer@theverge.com",
        "message me on signal",
        "signal —",
        "threads",
        "bluesky",
    ]
    if any(s in norm for s in installer_community_signals):
        return True

    # ------------------------------------------------------------
    # KEEP EVERYTHING ELSE
    # ------------------------------------------------------------

    return False
