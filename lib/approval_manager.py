"""
Approval Manager - Handles draft approval and logging for LinkedIn comments.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime


class ApprovalManager:
    """Manages comment draft approval flow and logging."""

    def __init__(self, auto_approve: bool = False, verbose: bool = False):
        self.auto_approve = auto_approve
        self.verbose = verbose
        self.log_file = os.getenv("APPROVAL_LOG_PATH", "logs/comment_approvals.json")

        # Ensure logs directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def present_variants(self, variants: List[Dict], post_url: str,
                         post_content: Dict) -> Optional[Dict]:
        """Present comment variants for user approval."""
        if not variants:
            return None

        print(f"\n  📋 Drafts generated for: {post_url}")
        print(f"  Post: {post_content.get('text', '')[:100]}...\n")

        for i, variant in enumerate(variants, 1):
            print(f"  --- Variant {i} ---")
            print(f"  Pattern: {variant.get('pattern', 'N/A')}")
            print(f"  Reaction: {variant.get('reaction', 'LIKE')}")
            print(f"  Rationale: {variant.get('rationale', 'N/A')}")
            print(f"  Text: {variant.get('text', '')}")
            print(f"  Length: {len(variant.get('text', ''))} chars")
            print()

        # Auto-approve mode
        if self.auto_approve:
            print("  ✅ Auto-approve enabled, posting variant 1")
            return variants[0]

        # Manual approval
        try:
            choice = input("  Approve which variant? (1-3, or 0 to skip): ").strip()
            if choice == "0" or not choice:
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(variants):
                selected = variants[idx].copy()
                selected["approved_at"] = datetime.now().isoformat()
                return selected
            else:
                print("  Invalid choice, skipping")
                return None
        except (ValueError, EOFError):
            print("  No input received, skipping")
            return None

    def log_post(self, post_url: str, draft: Dict, publish_result: Dict):
        """Log successful post for tracking."""
        record = {
            "post_url": post_url,
            "comment_text": draft.get("text", ""),
            "pattern": draft.get("pattern", ""),
            "reaction": draft.get("reaction", ""),
            "rationale": draft.get("rationale", ""),
            "published_at": draft.get("approved_at", datetime.now().isoformat()),
            "publish_result": publish_result
        }

        # Read existing log
        records = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    records = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                records = []

        # Append and save
        records.append(record)
        with open(self.log_file, "w") as f:
            json.dump(records, f, indent=2)

        if self.verbose:
            print(f"  📝 Logged to {self.log_file}")