import praw
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Reddit API credentials
reddit = praw.Reddit(client_id='rbVN6t-9h2vXeZ0aVgp2aQ',
                     client_secret='d9jH8BP9-LriEhiimK2RnFnkYya6nw',
                     user_agent='true_crime_stories_Own_Fuel4403')

# Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\gavin\Downloads\true-crime-stories-78e4a58c4509.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Reddit True Crime Stories").sheet1

# Function to fetch all existing post URLs from Google Sheets
def get_existing_post_urls():
    try:
        records = sheet.get_all_records()
        urls = {record.get('Post URL') for record in records if record.get('Post URL')}
        logging.info("Fetched existing URLs from Google Sheets.")
        return urls
    except Exception as e:
        logging.error("Error fetching existing post URLs: %s", e)
        return set()

# Function to fetch top posts from r/TrueCrime
def fetch_top_posts(subreddit_name, time_filter='week', limit=10):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        logging.info("Accessed subreddit: %s", subreddit.display_name)
        top_posts = subreddit.top(time_filter, limit=limit)
        logging.info("Fetched top posts from subreddit: %s", subreddit_name)
        return top_posts
    except Exception as e:
        logging.error("Error fetching posts from subreddit %s: %s", subreddit_name, e)
        return []

# Fetch posts from r/TrueCrime
subreddit_name = 'TrueCrime'
top_posts = fetch_top_posts(subreddit_name, limit=10)

# Get existing post URLs from Google Sheets
existing_urls = get_existing_post_urls()

# Prepare data for Google Sheets
added = False

for post in top_posts:
    if post.url not in existing_urls:
        try:
            # Ensure post.content is not None or empty
            post_content = post.selftext if post.selftext else "No content available"
            row = [
                post.title,
                post_content,
                post.url,
                post.score,
                post.subreddit.display_name,
                time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(post.created_utc))
            ]
            sheet.append_row(row)
            logging.info("Added post to Google Sheets: %s", post.title)
            added = True
            break  # Exit loop after adding the first unique post
        except Exception as e:
            logging.error("Error adding post to Google Sheets: %s", e)
    else:
        logging.info("Post already exists in Google Sheets: %s", post.title)

if not added:
    logging.info("No new unique posts found.")
