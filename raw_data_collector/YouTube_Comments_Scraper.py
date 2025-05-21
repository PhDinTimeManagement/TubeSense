from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

# Replace with your YouTube API Key
DEVELOPER_KEY = "AIzaSyAKLFmwDR3RHqjSp8i8mFeIAcaR4dpQnO0"

# Replace with the video ID of the YouTube video
VIDEO_ID = "87Jor5G_NBs"


def get_comments(video_id, part="snippet", max_pages=200):
    """
    Retrieves comments from a YouTube video, paging through up to `max_pages`.

    Args:
        video_id (str): The ID of the YouTube video.
        part (str): The part of the comment snippet to retrieve.
        max_pages (int): The maximum number of pages to retrieve (you can adjust as needed).

    Returns:
        list[dict]: A list of dictionaries containing comment text and number of likes.
    """
    youtube = build("youtube", "v3", developerKey=DEVELOPER_KEY)

    comments = []
    page_token = None
    page_count = 0

    try:
        while page_count < max_pages:
            response = youtube.commentThreads().list(
                part=part,
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,  # Up to 100 per page
                pageToken=page_token  # Start from the next page if available
            ).execute()

            # Extract comments from this page
            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comment_text = snippet["textDisplay"]
                likes = snippet["likeCount"]
                reply_count = snippet.get("totalReplyCount", 0)
                comments.append({
                    "comment": comment_text,
                    "num_of_likes": likes,
                    "reply_count": reply_count
                })

            # Check if there's another page
            page_token = response.get("nextPageToken")
            if not page_token:
                # No more pages
                break

            page_count += 1

        return comments

    except HttpError as error:
        print(f"An HTTP error {error.http_status} occurred:\n {error.content}")
        return []


def main():
    # Get comments from the video
    comments = get_comments(VIDEO_ID)

    if comments:
        # Create a pandas dataframe from the comments list
        df = pd.DataFrame(comments)

        # Sort dataframe by number of likes in descending order
        df = df.sort_values(by=['num_of_likes'], ascending=False)

        # Print dataframe
        print(df)

        # Export dataframe to a CSV file named "comments.csv"
        df.to_csv("../raw_data/comments.csv", index=False)
    else:
        print("Error: Could not retrieve comments from video.")


if __name__ == "__main__":
    main()