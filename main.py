"""
LinkedIn Comment Automation Bot

Monitors your LinkedIn feed, generates AI-powered comment drafts,
and publishes them on your behalf after approval.

Usage:
- Daily monitoring: scheduled via GitHub Actions
- Manual trigger: python main.py --post-url <url> --tone professional
- Approval mode: review drafts before posting
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from lib.linkedin_client import LinkedInClient
from lib.comment_generator import CommentGenerator
from lib.approval_manager import ApprovalManager


def parse_args():
    parser = argparse.ArgumentParser(description="LinkedIn Comment Automation")
    parser.add_argument("--post-url", type=str, help="Specific post URL to comment on")
    parser.add_argument("--tone", type=str, default="professional",
                        choices=["professional", "analytical", "casual", "witty", "nuanced"],
                        help="Comment tone")
    parser.add_argument("--keywords", type=str, nargs="+", default=None,
                        help="Keywords to filter posts by")
    parser.add_argument("--auto-approve", action="store_true",
                        help="Auto-post comments without review")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate drafts but don't post")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    return parser.parse_args()


def main():
    args = parse_args()

    # Initialize clients
    linkedin = LinkedInClient(
        cookie=os.getenv("LI_AT_COOKIE"),
        jsessionid=os.getenv("JSESSIONID_COOKIE")
    )
    generator = CommentGenerator(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        voice_profile=os.getenv("VOICE_PROFILE_PATH")
    )
    approval = ApprovalManager(
        auto_approve=args.auto_approve,
        verbose=args.verbose
    )

    # Mode 1: Specific post URL
    if args.post_url:
        posts = [{"url": args.post_url}]
    else:
        # Mode 2: Monitor feed for relevant posts
        posts = linkedin.monitor_feed(
            keywords=args.keywords,
            limit=20,
            since_hours=24
        )

        if not posts:
            print("No relevant posts found in the last 24 hours.")
            return

    # Process each post
    posted_count = 0
    for post in posts:
        url = post["url"]
        print(f"\nProcessing: {url}")

        try:
            # Fetch full post content
            content = linkedin.fetch_post(url)
            if not content:
                print("  ⚠️ Could not fetch post content, skipping.")
                continue

            # Generate 3 comment variants
            variants = generator.generate_comments(
                post_content=content["text"],
                tone=args.tone,
                existing_comments=content.get("comments", []),
                author_name=content.get("author", {}).get("name", "Author")
            )

            # Present for approval
            approved_draft = approval.present_variants(variants, url, content)
            if not approved_draft:
                print("  ✋ Draft rejected, skipping.")
                continue

            # Post the comment
            if not args.dry_run:
                result = linkedin.post_comment(
                    post_url=url,
                    comment=approved_draft["text"],
                    reaction=approved_draft.get("reaction", "LIKE")
                )

                if result.get("success"):
                    print(f"  ✅ Comment posted! Reaction: {approved_draft.get('reaction', 'LIKE')}")
                    posted_count += 1

                    # Save record
                    approval.log_post(url, approved_draft, result)
                else:
                    print(f"  ❌ Failed to post: {result.get('error', 'Unknown error')}")
            else:
                print(f"  📝 [DRY RUN] Draft: {approved_draft['text'][:100]}...")

        except Exception as e:
            print(f"  ❌ Error processing post: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

    print(f"\n{'='*50}")
    print(f"Done! Posted {posted_count} comment(s).")
    if args.dry_run:
        print("DRY RUN: No comments were actually posted.")


if __name__ == "__main__":
    main()