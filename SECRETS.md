# LinkedIn Automation Secrets

Add these secrets to your GitHub repo: https://github.com/Jalajj/linkedin-automation/settings/secrets/actions

| Name | Value | Where to get it |
|------|-------|----------------|
| `LINKEDIN_COOKIE` | li_at cookie value | [LinkedIn Cookies](#get-your-linkedin-cookie) |
| `LINKEDIN_JSESSIONID` | JSESSIONID cookie value | [LinkedIn Cookies](#get-your-linkedin-cookie) |
| `APIFY_TOKEN` | Your Apify API token | https://apify.com/account/api-tokens |
| `OPENROUTER_API_KEY` | Your OpenRouter API key | https://openrouter.ai/keys |
| `PUBLORA_API_KEY` | Your Publora API key | https://app.publora.com/settings/api |

## Get Your LinkedIn Cookie

1. Go to [linkedin.com](https://linkedin.com) and log in
2. Press `F12` to open Developer Tools
3. Go to **Application** tab → **Cookies** → `https://www.linkedin.com`
4. Find `li_at` and copy the **Value** column
5. Find `JSESSIONID` and copy the **Value** (remove surrounding quotes if present)
6. Add as GitHub secrets

## Add a Secret

1. Go to https://github.com/Jalajj/linkedin-automation/settings/secrets/actions
2. Click "New repository secret"
3. Enter name and value
4. Click "Add secret"