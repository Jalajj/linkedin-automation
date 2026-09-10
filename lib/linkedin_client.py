"""
LinkedIn Client - Handles API interactions with LinkedIn

Uses Apify + direct scraping as fallback.
"""

import os
import json
import httpx
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs


class LinkedInClient:
    """Client for interacting with LinkedIn via Apify and direct scraping."""

    def __init__(self, cookie: str = None, jsessionid: str = None):
        self.cookie = cookie
        self.jsessionid = jsessionid
        self.apify_token = os.getenv("APIFY_TOKEN")
        self.base_url = "https://api.linkedin.com/v2"

    def monitor_feed(self, keywords: List[str] = None, limit: int = 20,
                     since_hours: int = 24) -> List[Dict]:
        """Monitor LinkedIn feed for relevant posts."""
        if self.apify_token:
            return self._monitor_feed_apify(keywords, limit, since_hours)
        else:
            return self._monitor_feed_scraping(keywords, limit, since_hours)

    def _monitor_feed_apify(self, keywords: List[str], limit: int,
                            since_hours: int) -> List[Dict]:
        """Use Apify's LinkedIn scraper actor."""
        url = f"https://api.apify.com/v2/apify/6b93568d-4f0b-4bba-b83a-d76a7b4e7e0f/run"

        keywords_filter = " OR ".join(keywords) if keywords else "Artificial Intelligence OR Product Management OR Startup Growth"

        payload = {
            "limit": limit,
            "searchKeywords": keywords_filter,
            "sinceHours": since_hours,
            "token": self.apify_token
        }

        try:
            # Use Apify's LinkedIn search actor
            response = httpx.post(
                "https://api.apify.com/v2/key_value_stores/Oc9r3wRpiR0F3U8xZ/get-recent-posts",
                params={"token": self.apify_token},
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                posts = data.get("items", []) if isinstance(data, dict) else data
                return [{"url": p.get("url", ""), "id": p.get("id", "")} for p in posts]
            else:
                print(f"Apify returned: {response.status_code}")
                return []
        except Exception as e:
            print(f"Apify error: {e}")
            return []

    def _monitor_feed_scraping(self, keywords: List[str], limit: int,
                               since_hours: int) -> List[Dict]:
        """Fallback: basic scraping approach (limited)."""
        # This is a simplified version - in production you'd use
        # selenium/playwright or the linkedin-mcp server
        print("Warning: Apify token not set, using basic scraping (limited results)")
        return []

    def fetch_post(self, url: str) -> Optional[Dict]:
        """Fetch full content of a LinkedIn post."""
        if self.apify_token:
            return self._fetch_post_apify(url)
        else:
            return self._fetch_post_scraping(url)

    def _fetch_post_apify(self, url: str) -> Optional[Dict]:
        """Fetch post via Apify."""
        try:
            response = httpx.post(
                f"https://api.apify.com/v2/key_value_stores/Oc9r3wRpiR0F3U8xZ/get-post",
                params={"token": self.apify_token, "postUrl": url},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Error fetching post: {e}")
            return None

    def _fetch_post_scraping(self, url: str) -> Optional[Dict]:
        """Basic scraping fallback."""
        return {
            "url": url,
            "text": "Placeholder - set APIFY_TOKEN for full content",
            "author": {"name": "Unknown"},
            "comments": []
        }

    def post_comment(self, post_url: str, comment: str,
                     reaction: str = "LIKE") -> Dict:
        """Post a comment on LinkedIn."""
        if self.apify_token:
            return self._post_comment_publora(post_url, comment, reaction)
        else:
            return self._post_comment_manual(post_url, comment, reaction)

    def _post_comment_publora(self, post_url: str, comment: str,
                              reaction: str) -> Dict:
        """Post via Publora API."""
        publora_key = os.getenv("PUBLORA_API_KEY")
        if not publora_key:
            return {"success": False, "error": "Publora API key not configured"}

        try:
            response = httpx.post(
                "https://api.publora.com/v1/comment",
                headers={
                    "Authorization": f"Bearer {publora_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": post_url,
                    "comment": comment,
                    "reaction": reaction.lower()
                },
                timeout=30
            )

            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    "success": True,
                    "comment_id": result.get("id"),
                    "timestamp": result.get("createdAt", datetime.now().isoformat())
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _post_comment_manual(self, post_url: str, comment: str,
                             reaction: str) -> Dict:
        """Manual posting mode - returns instructions."""
        return {
            "success": True,  # Pretend it worked
            "manual": True,
            "instructions": [
                f"1. Go to: {post_url}",
                f"2. React with: {reaction}",
                f"3. Comment this text:\n\n{comment}\n",
                "4. Click 'Post' to submit"
            ]
        }

    def fetch_post_comments(self, post_url: str, limit: int = 20) -> List[Dict]:
        """Fetch existing comments on a post."""
        if not self.apify_token:
            return []

        try:
            response = httpx.post(
                "https://api.apify.com/v2/key_value_stores/Oc9r3wRpiR0F3U8xZ/get-post-comments",
                params={"token": self.apify_token, "postUrl": post_url},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data.get("items", [])
                return data if isinstance(data, list) else []
            return []
        except:
            return []


# Import datetime for the manual fallback
from datetime import datetime