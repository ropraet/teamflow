"""
Bug Registry — central feature flag system for injecting controlled bugs.
Each bug has an ID, metadata, and an active/inactive state.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

GROUND_TRUTH_PATH = Path(__file__).parent.parent / "bugs" / "ground_truth.json"

PRESETS: dict[str, list[str]] = {
    "none": [],
    "easy": [
        "form_missing_title_validation",
        "crud_edit_doesnt_save",
        "broken_nav_link",
        "a11y_missing_form_labels",
        "security_no_csp",
    ],
    "medium": [
        # easy +
        "form_missing_title_validation",
        "crud_edit_doesnt_save",
        "broken_nav_link",
        "a11y_missing_form_labels",
        "security_no_csp",
        # + 10 more
        "form_accepts_invalid_email",
        "form_submit_no_feedback",
        "crud_delete_item_reappears",
        "search_no_results_state_missing",
        "filter_resets_on_pagination",
        "auth_session_not_cleared",
        "auth_expired_no_redirect",
        "export_missing_columns",
        "error_generic_500_message",
        "img_missing_alt",
    ],
    "hard": [],  # filled dynamically with ALL bugs
}


class BugRegistry:
    def __init__(self) -> None:
        self._active: set[str] = set()
        self._catalog: dict[str, dict[str, Any]] = {}
        self._load_ground_truth()
        # hard preset = all bugs
        PRESETS["hard"] = list(self._catalog.keys())

    def _load_ground_truth(self) -> None:
        if GROUND_TRUTH_PATH.exists():
            data = json.loads(GROUND_TRUTH_PATH.read_text())
            self._catalog = data.get("bugs", {})
        else:
            self._catalog = {}

    def is_active(self, bug_id: str) -> bool:
        return bug_id in self._active

    def activate(self, bug_id: str) -> None:
        self._active.add(bug_id)

    def deactivate(self, bug_id: str) -> None:
        self._active.discard(bug_id)

    def toggle(self, bug_id: str) -> bool:
        if bug_id in self._active:
            self._active.discard(bug_id)
            return False
        self._active.add(bug_id)
        return True

    def apply_preset(self, preset_name: str) -> list[str]:
        bugs = PRESETS.get(preset_name, [])
        self._active = set(bugs)
        return bugs

    def list_bugs(self) -> list[dict[str, Any]]:
        result = []
        for bug_id, meta in self._catalog.items():
            result.append({
                "id": bug_id,
                "active": bug_id in self._active,
                **meta,
            })
        return result

    def get_active_ids(self) -> list[str]:
        return sorted(self._active)

    def get_preset_names(self) -> list[str]:
        return list(PRESETS.keys())


# Singleton
bug_registry = BugRegistry()
