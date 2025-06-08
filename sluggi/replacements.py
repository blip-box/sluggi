"""Replacement engine for sluggi: staged (pre/post/both) replacements."""

import re
from dataclasses import dataclass, field
from typing import Callable, Literal, Optional

Stage = Literal[
    "pre",
    "post",
    "both",
]


@dataclass(frozen=True)
class ReplacementRule:
    """Defines a single replacement rule for the ReplacementEngine."""

    old: str
    new: str
    stage: Stage = "both"
    use_regex: bool = False
    func: Optional[Callable[[str], str]] = None  # Custom logic (optional)


@dataclass
class ReplacementConfig:
    """Holds a list of replacement rules for the engine configuration."""

    rules: list[ReplacementRule] = field(default_factory=list)


class ReplacementEngine:
    """Engine to apply staged replacements using a list of rules."""

    def __init__(
        self,
        config: ReplacementConfig,
    ):
        """Initialize the engine and precompile regex rules."""
        self.config = config
        # Precompile regex rules for performance
        self._compiled_rules: list[tuple[ReplacementRule, Optional[re.Pattern]]] = []
        for rule in config.rules:
            pattern = re.compile(rule.old) if rule.use_regex else None
            self._compiled_rules.append((rule, pattern))

    def apply(
        self,
        text: str,
        stage: Stage,
    ) -> tuple[str, list[ReplacementRule]]:
        """Apply all rules for the given stage to the text.

        Returns (result_text, list_of_applied_rules).
        """
        applied = []
        for rule, pattern in self._compiled_rules:
            if rule.stage not in (stage, "both"):
                continue
            original = text
            if rule.func is not None:
                text = rule.func(text)
            elif rule.use_regex and pattern is not None:
                new_text, n = pattern.subn(rule.new, text)
                if n > 0:
                    text = new_text
            else:
                if rule.old in text:
                    text = text.replace(rule.old, rule.new)
            if text != original:
                applied.append(rule)
        return text, applied


# Utility: Convert legacy custom_map to ReplacementConfig


def custom_map_to_config(
    custom_map: Optional[dict],
    stage: Stage = "both",
) -> ReplacementConfig:
    """Convert a custom mapping dictionary to a ReplacementConfig."""
    if not custom_map:
        return ReplacementConfig()
    rules = [ReplacementRule(old=k, new=v, stage=stage) for k, v in custom_map.items()]
    return ReplacementConfig(rules=rules)
