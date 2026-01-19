import yt_dlp

def fetch_tiktok_metadata(video_url: str):
    """
        Extracts metadata (description, tags, etc.) from a TikTok URL
        without downloading the video file.
        """
    ydl_opts = {
        'skip_download': True,  # We only want text data
        'quiet': True,  # Don't print huge logs
        'no_warnings': True,
        'extract_flat': True,  # Fast extraction
    }

    print(f"🔍 Scraping metadata for: {video_url}...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # Extract the useful bits for the AI
            data = {
                "id": info.get("id"),
                "uploader": info.get("uploader"),
                "description": info.get("description", ""),  # This is the Caption
                "tags": info.get("tags", []),
                "title": info.get("title", "")
            }

            return data

    except Exception as e:
        print(f"❌ Error scraping TikTok: {e}")
        return None


# Quick test if you run this file directly
if __name__ == "__main__":
    # Test with a known movie clip (e.g., an Interstellar clip or similar)
    test_url = "https://www.tiktok.com/@netflix/video/733838..."  # Replace with a REAL link from your collection
    result = fetch_tiktok_metadata(test_url)
    print(result)