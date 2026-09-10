#!/usr/bin/env python3
"""
OpenRouter API Connection Test
Reads API key from temporary file to avoid shell masking
"""
import httpx
import os

# Try multiple sources for the API key
sources = [
    os.getenv("OPENROUTER_API_KEY"),
    os.getenv("OPENROUTER_KEY"),
]

# Also try reading from a secrets file if it exists
secrets_file = "/c/Users/jalaj/InterviewBriefing/linkedin-automation/.api_key"
if os.path.exists(secrets_file):
    with open(secrets_file, "r") as f:
        sources.insert(0, f.read().strip())

api_key = None
for s in sources:
    if s and len(s) > 10 and s.startswith("sk-or-"):
        api_key = s
        break

if not api_key:
    print("❌ No valid API key found")
    print("Set it via:")
    print("  export OPENROUTER_API_KEY='your-key-here'")
    print("Or save to .api_key file")
    exit(1)

print(f"✅ Found API key: {api_key[:7]}...")

# Test the API connection
print("\nTesting OpenRouter connection...")
try:
    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": "Reply with exactly: HELLO_WORKING"}],
            "max_tokens": 10
        },
        timeout=30
    )
    
    print(f"HTTP Status: {resp.status_code}")
    
    if resp.status_code == 200:
        response_text = resp.json()["choices"][0]["message"]["content"].strip()
        print(f"Response: {response_text}")
        print("✅ OpenRouter API is working!")
    else:
        print(f"❌ API Error: {resp.text[:300]}")
        print(f"Status code details: {resp.json() if resp.headers.get('content-type', '').startswith('application/json') else 'N/A'}")
        
except httpx.TimeoutException:
    print("❌ Timeout - check your internet connection")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")