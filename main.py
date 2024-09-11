from googleapiclient.discovery import build
from textblob import TextBlob
from fpdf import FPDF

# Set up your YouTube Data API key
API_KEY = "AIzaSyDBxNBekeI2MPC7OfQXrfoLtKPT-zflpuo"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_comments(video_id):
    """Fetch comments from a YouTube video."""
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
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
    """Replace problematic characters with a space or other character."""
    return text.replace("\u2019", "'").encode("latin-1", "replace").decode("latin-1")


class PDF(FPDF):
    def header(self):
        self.set_font("DejaVuSans", size=12)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVuSans", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


def generate_pdf(comments, filtered_comments, keyword):
    """Generate a PDF report of the comments."""
    pdf = PDF()

    # Add the DejaVuSans font
    pdf.add_font("DejaVuSans", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVuSans", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)

    pdf.add_page()
    pdf.set_font("DejaVuSans", size=12)

    # Add title
    pdf.cell(
        200,
        10,
        txt=f"YouTube Comments Analysis for Keyword: {keyword}",
        ln=True,
        align="C",
    )

    # Add Positive Comments
    pdf.cell(200, 10, txt="Positive Comments:", ln=True, align="L")
    for comment in comments:
        if comment["sentiment"] == "Positive":
            sanitized_text = sanitize_text(comment["text"])
            pdf.multi_cell(0, 10, f"{comment['author']}: {sanitized_text}")

    # Add Negative Comments
    pdf.cell(200, 10, txt="Negative Comments:", ln=True, align="L")
    for comment in comments:
        if comment["sentiment"] == "Negative":
            sanitized_text = sanitize_text(comment["text"])
            pdf.multi_cell(0, 10, f"{comment['author']}: {sanitized_text}")

    # Add Filtered Comments
    pdf.cell(
        200, 10, txt=f"Filtered Comments for Keyword: {keyword}", ln=True, align="L"
    )
    for comment in filtered_comments:
        sanitized_text = sanitize_text(comment["text"])
        pdf.multi_cell(0, 10, f"{comment['author']}: {sanitized_text}")

    # Save PDF
    pdf.output("youtube_comments_analysis.pdf")


def main(video_id, keyword):
    # Fetch comments from YouTube
    comments = get_comments(video_id)

    # Analyze sentiment for each comment
    for comment in comments:
        comment["sentiment"] = analyze_sentiment(comment["text"])

    # Filter comments based on the keyword
    filtered_comments = filter_comments(comments, keyword)

    # Generate the PDF report
    generate_pdf(comments, filtered_comments, keyword)
    print("PDF generated: youtube_comments_analysis.pdf")


# Example usage
video_id = "uz7dY8qTFJw"  # Replace with the video ID you want to analyze
keyword = "really"  # Replace with the keyword you want to search for
main(video_id, keyword)
