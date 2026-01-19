import os
from dotenv import load_dotenv
from src.tiktok_loader import fetch_tiktok_metadata
from src.ai_agent import extract_movie_from_text

# Load env variables
load_dotenv()


def run_pipeline(tiktok_url):
    print("--- STARTING PIPELINE ---")

    # Fetch Data
    metadata = fetch_tiktok_metadata(tiktok_url)
    if not metadata:
        return

    # Combine caption and tags for the AI
    # oin hashtags into a string so the AI sees them clearly
    full_text = f"Caption: {metadata['description']}\nTags: {', '.join(metadata['tags'])}"

    print(f"\n📝 Extracted Text: {full_text[:100]}...")  # Print first 100 chars

    # Analyze Data
    print("\n🤖 Sending to AI Agent...")
    result = extract_movie_from_text(full_text)

    if result:
        print("\n✅ RESULT FOUND:")
        print(f"Movie: {result.movie_title}")
        print(f"Confidence: {result.confidence_score}/10")
        print(f"Reasoning: {result.reasoning}")
    else:
        print("❌ AI could not extract a movie.")


if __name__ == "__main__":
    # COPY A LINK FROM YOUR TIKTOK FAVORITES COLLECTION HERE
    my_link = input("Paste a TikTok link: ")
    run_pipeline(my_link)