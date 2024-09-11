from googleapiclient.discovery import build
from textblob import TextBlob
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch
import getpass
import html


# Function to get API key from user
def get_api_key():
    return getpass.getpass(prompt="Enter your YouTube Data API key: ")


# Function to get API service name from user
def get_api_service_name():
    return input('Enter the API service name (default is "youtube"): ') or "youtube"


# Function to get API version from user
def get_api_version():
    version = input('Enter the API version (default is "v3"): ')
    return version if version else "v3"


def get_comments(video_id, api_key, api_service_name, api_version):
    """Fetch comments from a YouTube video."""
    youtube = build(api_service_name, api_version, developerKey=api_key)
    comments = []
    request = youtube.commentThreads().list(
        part="snippet", videoId=video_id, maxResults=100, textFormat="plainText"
    )
    response = request.execute()

    while request is not None:
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(
                {
                    "author": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "like_count": comment["likeCount"],
                }
            )
        request = youtube.commentThreads().list_next(request, response)
        if request:
            response = request.execute()
        else:
            break

    return comments


def analyze_sentiment(comment):
    """Analyze the sentiment of a comment."""
    analysis = TextBlob(comment)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"


def filter_comments(comments, keyword):
    """Filter comments based on a keyword."""
    filtered_comments = []
    for comment in comments:
        if keyword.lower() in comment["text"].lower():
            filtered_comments.append(comment)
    return filtered_comments


def sanitize_text(text):
    """Sanitize text to avoid issues with PDF generation."""
    text = text.replace("\u2019", "'")
    text = html.escape(text)  # Escape HTML characters
    return text


def generate_pdf(comments, filtered_comments, keyword, video_id):
    """Generate a PDF report of the comments."""
    filename = "youtube_comments_analysis.pdf"
    document = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_title = styles["Title"]

    content = []

    # Add title with video link and title
    title = f"YouTube Comments Analysis for Video: {video_id}"
    content.append(Paragraph(title, style_title))

    def add_comments_to_pdf(title, comments_list):
        content.append(Paragraph(title, style_normal))
        for comment in comments_list:
            sanitized_text = sanitize_text(comment["text"])
            comment_text = f"{comment['author']}: {sanitized_text}"
            content.append(Paragraph(comment_text, style_normal))
        content.append(Paragraph("<br/>", style_normal))  # Add space between sections

    # Add Filtered Comments
    add_comments_to_pdf(f"Filtered Comments for Keyword: {keyword}", filtered_comments)

    # Add Positive Comments
    add_comments_to_pdf(
        "Positive Comments:", [c for c in comments if c["sentiment"] == "Positive"]
    )

    # Add Negative Comments
    add_comments_to_pdf(
        "Negative Comments:", [c for c in comments if c["sentiment"] == "Negative"]
    )

    # Build PDF
    document.build(content)
    print(f"PDF generated: {filename}")


def main(video_id, keyword):
    # Get API key from user
    api_key = get_api_key()

    # Get API service name and version from user
    api_service_name = get_api_service_name()
    api_version = get_api_version()

    # Fetch comments from YouTube
    comments = get_comments(video_id, api_key, api_service_name, api_version)

    # Analyze sentiment for each comment
    for comment in comments:
        comment["sentiment"] = analyze_sentiment(comment["text"])

    # Filter comments based on the keyword
    filtered_comments = filter_comments(comments, keyword)

    # Generate the PDF report
    generate_pdf(comments, filtered_comments, keyword, video_id)


# Example usage
if __name__ == "__main__":
    video_id = input("Enter the video ID: ")  # Get video ID from user
    keyword = input("Enter the keyword to search for: ")  # Get keyword from user
    main(video_id, keyword)
