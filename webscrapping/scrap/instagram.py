import os

from dotenv import load_dotenv
from instagrapi import Client


load_dotenv()
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


BASE_HASHTAG = "suisseromande"
SEARCH_HASHTAGS = ["handmade", "homemade"]
SEARCH_TEXTS = ["dm for order", "purchase"]
MAX_POSTS = 10


print("Logging in to Instagram...")
client = Client()
client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
print("Logged!")


def find_users(
    client: Client,
    base_hashtag: str,
    search_hashtags: list[str],
    search_texts: list[str],
    amount: int = 10,
) -> set[str]:
    posts = client.hashtag_medias_top(base_hashtag, amount)
    hashtags_and_texts = [f"#{hashtag}" for hashtag in search_hashtags] + search_texts
    usernames = set()

    for post in posts:
        post_text = post.caption_text.lower()
        print(f"Checking post by {post.user.username}", flush=True)

        if any(t in post_text for t in hashtags_and_texts):
            usernames.add(post.user.username)
            print(f"Match found: {post_text}", flush=True)
            continue

    return usernames


matching_users = find_users(
    client, BASE_HASHTAG, SEARCH_HASHTAGS, SEARCH_TEXTS, MAX_POSTS
)

print("\nMatching users:")
print(matching_users)
