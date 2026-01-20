import yt_dlp


def fetch_tiktok_metadata(video_url: str):
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        # YOUR CHANGES HERE:
        'extract_flat': False,  # Must be False to get comments
        'get_comments': True,  # Turn on comments
        'cookiefile': 'cookies.txt',
    }

    print(f"🔍 Scraping metadata (and comments) for: {video_url}...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # NEW: Extract top 10 comments
            # yt-dlp returns them in a list called 'comments'
            raw_comments = info.get("comments", [])
            top_comments = []

            # Grab the text from the first 10 comments
            for comment in raw_comments[:10]:
                text = comment.get("text")
                if text:
                    top_comments.append(text)

            data = {
                "id": info.get("id"),
                "uploader": info.get("uploader"),
                "description": info.get("description", ""),
                "tags": info.get("tags", []),
                "title": info.get("title", ""),
                "comments": top_comments  # <--- We added this
            }

            return data

    except Exception as e:
        print(f"❌ Error scraping TikTok: {e}")
        return None