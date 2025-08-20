import feedparser
import requests
import time
import hashlib
import argparse
import logging
from pathlib import Path
import json


# Keep track of seen entries (per feed)
def load_seen(path):
    if Path(path).exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_seen(path, seen):
    with open(path, "w") as f:
        json.dump(seen, f)


def get_entry_id(entry):
    """Generate a unique ID for an RSS entry."""
    if "id" in entry:
        return entry.id
    elif "link" in entry:
        return entry.link
    else:
        return hashlib.md5(
            (entry.title + entry.get("published", "")).encode()
        ).hexdigest()


def send_to_mattermost(entry, webhook_url):
    """Send RSS entry to Mattermost via webhook."""
    message = f"**{entry.summary} {entry.title}**\n{entry.link}\n{entry.published}"
    payload = {"text": message}
    logging.info(f"Sending message to Mattermost: {message}")
    if not webhook_url:
        logging.error("❌ No Mattermost webhook URL provided. Not sending.")
        return
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        logging.error(f"❌ Failed to send message: {response.text}")


def check_feed(feed_url, seen, seen_file, webhook_url):
    """Check RSS feed and send new entries to Mattermost."""
    feed = feedparser.parse(feed_url)

    if feed_url not in seen:
        seen[feed_url] = []

    for entry in feed.entries:
        entry_id = get_entry_id(entry)
        if entry_id not in seen[feed_url]:
            logging.info(f"New entry found: {entry.title}")
            send_to_mattermost(entry, webhook_url)
            seen[feed_url].append(entry_id)

    save_seen(seen_file, seen)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="RSS to Mattermost bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("feeds", nargs="+", help="One or more RSS feed URLs")
    parser.add_argument(
        "--interval", type=int, default=300, help="Interval between checks in seconds"
    )
    parser.add_argument(
        "--seen-file",
        default=".rss_seenfiles.json",
        help=f"Path to JSON file storing seen entries",
    )
    parser.add_argument(
        "--mattermost-url", help="Mattermost webhook URL"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not read the cached file"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    seen_entries = load_seen(args.seen_file) if not args.no_cache else {}

    logging.info(
        f"Starting RSS to Mattermost bot... Monitoring {len(args.feeds)} feeds."
    )

    while True:
        try:
            for feed_url in args.feeds:
                check_feed(feed_url, seen_entries, args.seen_file, args.mattermost_url)
        except Exception as e:
            logging.error(f"⚠️ Error: {e}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
