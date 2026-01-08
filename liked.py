import os
import csv
import requests
from datetime import datetime
from requests_oauthlib import OAuth1

USER_FILE = "twitter_usernames.txt"
OUTPUT_FILE = "liked_tweets.csv"

API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


def get_user(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    r = requests.get(url, auth=auth)
    if r.status_code != 200:
        print(f"[ERR user] {username}: {r.text}")
        return None
    return r.json().get("data")


def get_liked(user_id, max_results):
    url = (
        f"https://api.twitter.com/2/users/{user_id}/liked_tweets"
        f"?max_results={max_results}&tweet.fields=created_at"
    )
    r = requests.get(url, auth=auth)
    if r.status_code != 200:
        print(f"[ERR likes] {r.status_code}: {r.text}")
        return []
    return r.json().get("data", [])


def build_url(tweet_id):
    return f"https://x.com/i/web/status/{tweet_id}"


def main():
    count = int(os.environ.get("LIKE_COUNT", 1))
    usernames = [u.strip() for u in open(USER_FILE) if u.strip()]

    out_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not out_exists:
            writer.writerow(["timestamp", "liked_by", "tweet_url", "tweet_created_at"])

        for uname in usernames:
            user = get_user(uname)
            if not user:
                continue

            likes = get_liked(user["id"], count)
            for t in likes:
                writer.writerow([
                    datetime.utcnow().isoformat(),
                    uname,
                    build_url(t["id"]),
                    t.get("created_at", "")
                ])


if __name__ == "__main__":
    main()
