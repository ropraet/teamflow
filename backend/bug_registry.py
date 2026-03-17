"""
Bug Registry — central feature flag system for injecting controlled bugs.
Each bug has an ID, metadata, and an active/inactive state.
State is persisted to disk so it survives restarts.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

GROUND_TRUTH_PATH = Path(__file__).parent.parent / "bugs" / "ground_truth.json"
STATE_PATH = Path(os.getenv("DB_PATH", "teamflow.db")).parent / "bug_state.json"

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
        PRESETS["hard"] = list(self._catalog.keys())
        self._load_state()

    def _load_ground_truth(self) -> None:
        if GROUND_TRUTH_PATH.exists():
            data = json.loads(GROUND_TRUTH_PATH.read_text())
            self._catalog = data.get("bugs", {})
        else:
            self._catalog = {}

    def _load_state(self) -> None:
        if STATE_PATH.exists():
            try:
                data = json.loads(STATE_PATH.read_text())
                self._active = set(data.get("active", []))
            except (json.JSONDecodeError, KeyError):
                self._active = set()

    def _save_state(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps({"active": sorted(self._active)}))

    def is_active(self, bug_id: str) -> bool:
        return bug_id in self._active

    def activate(self, bug_id: str) -> None:
        self._active.add(bug_id)
        self._save_state()

    def deactivate(self, bug_id: str) -> None:
        self._active.discard(bug_id)
        self._save_state()

    def toggle(self, bug_id: str) -> bool:
        if bug_id in self._active:
            self._active.discard(bug_id)
            active = False
        else:
            self._active.add(bug_id)
            active = True
        self._save_state()
        return active

    def apply_preset(self, preset_name: str) -> list[str]:
        bugs = PRESETS.get(preset_name, [])
        self._active = set(bugs)
        self._save_state()
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
