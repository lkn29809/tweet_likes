import os
import csv
import requests
import argparse
from datetime import datetime

USER_FILE = "twitter_usernames.txt"
OUTPUT_FILE = "liked_tweets.csv"

BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}


def get_user(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"[ERR] {username}: {r.text}")
        return None
    return r.json().get("data")


def get_liked(user_id, max_results):
    url = (
        f"https://api.twitter.com/2/users/{user_id}/liked_tweets"
        f"?max_results={max_results}&tweet.fields=created_at"
    )
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"[ERR] likes: {r.text}")
        return []
    return r.json().get("data", [])


def build_url(tweet_id):
    return f"https://x.com/i/web/status/{tweet_id}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()

    if not BEARER_TOKEN:
        print("Missing env X_BEARER_TOKEN")
        return

    if not os.path.exists(USER_FILE):
        print(f"{USER_FILE} not found")
        return

    usernames = [u.strip() for u in open(USER_FILE) if u.strip()]
    if not usernames:
        print("No usernames listed")
        return

    out_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not out_exists:
            writer.writerow(["timestamp", "liked_by", "tweet_url", "tweet_created_at"])

        for uname in usernames:
            user = get_user(uname)
            if not user:
                continue

            likes = get_liked(user["id"], args.count)
            if not likes:
                print(f"[OK] {uname}: none returned")
                continue

            for t in likes:
                writer.writerow([
                    datetime.utcnow().isoformat(),
                    uname,
                    build_url(t["id"]),
                    t.get("created_at", "")
                ])

            print(f"[OK] {uname}: saved {len(likes)}")


if __name__ == "__main__":
    main()

