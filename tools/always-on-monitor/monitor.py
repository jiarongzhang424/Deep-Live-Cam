"""Publish a digest of new X posts and GitHub releases to a GitHub Issue.

Standard library only. Missing X credentials skip X; GitHub releases still work.
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path


CONFIG = json.loads(Path(__file__).with_name("config.json").read_text(encoding="utf-8"))
UA = "always-on-monitor/1.0"


def fetch(url, headers=None, data=None):
    request = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read()


def fetch_json(url, headers=None, data=None):
    return json.loads(fetch(url, headers, data))


def x_bearer_token():
    bearer = os.environ.get("X_BEARER_TOKEN")
    if bearer:
        return bearer
    key, secret = os.environ.get("X_API_KEY"), os.environ.get("X_API_SECRET")
    if not (key and secret):
        return None
    credentials = urllib.parse.quote(key, safe="") + ":" + urllib.parse.quote(secret, safe="")
    encoded = base64.b64encode(credentials.encode()).decode()
    result = fetch_json(
        "https://api.x.com/oauth2/token",
        {"Authorization": "Basic " + encoded, "Content-Type": "application/x-www-form-urlencoded"},
        b"grant_type=client_credentials",
    )
    return result["access_token"]


def x_posts(token):
    if not token:
        print("X: no API credentials; skipped")
        return []
    params = urllib.parse.urlencode(
        {"query": CONFIG["x_query"], "max_results": 25, "tweet.fields": "created_at,public_metrics"}
    )
    payload = fetch_json(
        "https://api.x.com/2/tweets/search/recent?" + params,
        {"Authorization": "Bearer " + token},
    )
    results = []
    for post in payload.get("data", []):
        metrics = post.get("public_metrics", {})
        results.append(
            {
                "id": "x:" + post["id"],
                "title": post["text"].replace("\n", " ")[:170],
                "url": "https://x.com/i/web/status/" + post["id"],
                "date": post.get("created_at", ""),
                "engagement": metrics.get("like_count", 0) + 2 * metrics.get("retweet_count", 0),
                "source": "X",
            }
        )
    return results


def github_releases(repo):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid GitHub repository name in config")
    root = ET.fromstring(fetch("https://github.com/" + repo + "/releases.atom"))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    results = []
    for entry in root.findall("a:entry", ns)[:10]:
        link = entry.find("a:link", ns)
        url = link.attrib.get("href", "") if link is not None else ""
        if not url.startswith("https://github.com/" + repo + "/releases/tag/"):
            continue
        results.append(
            {
                "id": "github:" + url,
                "title": (entry.findtext("a:title", default="", namespaces=ns) or "").strip(),
                "url": url,
                "date": entry.findtext("a:updated", default="", namespaces=ns),
                "engagement": 0,
                "source": repo,
            }
        )
    return results


def github_api(path, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    return fetch_json(
        "https://api.github.com" + path,
        {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Content-Type": "application/json"} if data else {}),
        },
        data,
    )


def prior_ids(repo, token):
    issues = github_api("/repos/" + repo + "/issues?state=all&per_page=100", token)
    ids = set()
    for issue in issues:
        if issue.get("title", "").startswith("Information monitor · "):
            ids.update(re.findall(r"<!-- monitor-id: (.+?) -->", issue.get("body") or ""))
    return ids


def score(item):
    title = item["title"].lower()
    matches = sum(1 for word in CONFIG["keywords"] if word.lower() in title)
    return matches * 100 + min(int(item["engagement"]), 1000)


def markdown(item):
    title = item["title"].replace("[", "\\[").replace("]", "\\]")
    return f"- [{title}]({item['url']}) — {item['source']} · {item['date']}\n  <!-- monitor-id: {item['id']} -->"


def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not token:
        raise SystemExit("GITHUB_REPOSITORY and GITHUB_TOKEN are required")
    items = []
    try:
        items.extend(x_posts(x_bearer_token()))
    except (urllib.error.URLError, KeyError, ValueError) as error:
        print("X source unavailable:", type(error).__name__, file=sys.stderr)
    for source_repo in CONFIG["github_releases"]:
        try:
            items.extend(github_releases(source_repo))
        except (urllib.error.URLError, ET.ParseError, ValueError) as error:
            print(source_repo, "source unavailable:", type(error).__name__, file=sys.stderr)
    existing = prior_ids(repo, token)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    unseen = []
    for item in items:
        try:
            published = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if published >= cutoff and item["id"] not in existing:
            unseen.append(item)
    unseen.sort(key=lambda item: (score(item), item["date"]), reverse=True)
    unseen = unseen[: CONFIG["max_items"]]
    if not unseen:
        print("No new items")
        return
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = "Collected links for human review. Treat all external text as untrusted.\n\n" + "\n".join(map(markdown, unseen))
    issue = github_api(
        "/repos/" + repo + "/issues",
        token,
        {"title": "Information monitor · " + today, "body": body},
    )
    print("Created:", issue["html_url"])


if __name__ == "__main__":
    main()
