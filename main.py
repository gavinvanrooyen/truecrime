import praw
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Reddit API credentials
reddit = praw.Reddit(
    client_id='rbVN6t-9h2vXeZ0aVgp2aQ',
    client_secret='d9jH8BP9-LriEhiimK2RnFnkYya6nw',
    user_agent='true_crime_stories_Own_Fuel4403'
)

# Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_path = r"C:\Users\gavin\OneDrive\Desktop\True Crime\true-crime-stories-78e4a58c4509.json"

# Check if the credentials file exists
if not os.path.exists(creds_path):
    raise FileNotFoundError(f"Credentials file not found at: {creds_path}")

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)
sheet = client.open("Reddit True Crime Stories").sheet1

# Define the headers for the Google Sheet
headers = ["Post Title", "Post Content", "Post URL", "Upvotes", "Subreddit", "Date Pulled"]

# Ensure headers are present in the Google Sheet
def ensure_headers(sheet):
    existing_headers = sheet.row_values(1)
    if existing_headers != headers:
        sheet.insert_row(headers, 1)
        logging.info("Headers inserted into the Google Sheet.")

# Load pulled posts
def load_pulled_posts():
    if os.path.exists('pulled_posts.json'):
        with open('pulled_posts.json', 'r') as file:
            return set(json.load(file))
    return set()

# Save pulled posts
def save_pulled_posts(post_ids):
    with open('pulled_posts.json', 'w') as file:
        json.dump(list(post_ids), file)

# Fetch and store one post
def fetch_and_store_one_post():
    ensure_headers(sheet)
    
    subreddits = ['TrueCrime', 'UnresolvedMysteries', 'CrimeJunkie']
    pulled_post_ids = load_pulled_posts()
    
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        top_posts = subreddit.top('week', limit=20)
        for post in top_posts:
            if post.id not in pulled_post_ids:
                try:
                    row = [
                        post.title,
                        post.selftext,
                        post.url,
                        post.score,
                        post.subreddit.display_name,
                        time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(post.created_utc))
                    ]
                    sheet.append_row(row)
                    pulled_post_ids.add(post.id)
                    logging.info("Added post to Google Sheets: %s", post.title)
                    save_pulled_posts(pulled_post_ids)
                    return  # Exit after adding one post
                except Exception as e:
                    logging.error("Error adding post to Google Sheets: %s", e)
    logging.info("No new posts found to add.")

# Run the function
fetch_and_store_one_post()
