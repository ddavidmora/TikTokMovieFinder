import csv
import time
import os
import sys
from src.tiktok_loader import fetch_tiktok_metadata
from src.ai_agent import extract_movie_from_text
from src.tmdb_client import search_tmdb

# --- SETTINGS ---
INPUT_FILE = "links.txt"
OUTPUT_FILE = "my_movie_collection.csv"


def process_single_link(tiktok_url):
    """
    SPEED MODE: Only checks Text/Metadata. If hard, SKIPS immediately.
    """
    try:
        print(f"\n🎬 Processing: {tiktok_url}")

        # 1. Scrape Text
        metadata = fetch_tiktok_metadata(tiktok_url)
        if not metadata:
            return None

        full_text = f"Caption: {metadata['description']} Comments: {metadata['comments']}"

        # 2. AI Text Analysis
        ai_result = extract_movie_from_text(full_text)

        # If AI is unsure or didn't find a movie, we just GIVE UP immediately.
        if not ai_result or not ai_result.found_movie:
            print("   ⏩ Skipping (AI couldn't find a movie name in text).")
            return None

        if ai_result.confidence_score < 7:
            print(f"   ⏩ Skipping (Confidence too low: {ai_result.confidence_score}/10).")
            return None

        # 3. TMDB Verification
        details = search_tmdb(ai_result.movie_title)
        if not details:
            print(f"   ⚠️ Skipping '{ai_result.movie_title}' (Not in TMDB database)")
            return None

        print(f"   ✅ MATCH: {details['title']} ({details['rating']}/10)")

        return {
            "Title": details['title'],
            "Year": details['year'],
            "Rating": float(details['rating']),
            "TikTok_Link": tiktok_url,
            "Poster": details['poster_url'],
            "Reasoning": ai_result.reasoning
        }

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Please create '{INPUT_FILE}' and paste your links there.")
        return

    with open(INPUT_FILE, "r") as f:
        links = [line.strip() for line in f.readlines() if line.strip()]

    print(f"🚀 Starting SPEED RUN for {len(links)} videos...")
    print(f"💾 Results will be saved live to: {OUTPUT_FILE}")
    print(f"🛑 PRESS 'Ctrl+C' (or Cmd+C) AT ANY TIME TO STOP SAFELY.")

    fieldnames = ["Title", "Year", "Rating", "TikTok_Link", "Poster", "Reasoning"]
    file_exists = os.path.isfile(OUTPUT_FILE)

    # We open the file and keep it open, appending row by row
    try:
        with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            for i, link in enumerate(links):
                print(f"--- Video {i + 1}/{len(links)} ---")

                movie_data = process_single_link(link)

                if movie_data:
                    writer.writerow(movie_data)
                    csvfile.flush()  # Force save to disk immediately

                # SLEEP to manage rate limits
                time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n🛑 STOPPING SCRIPT (USER REQUEST)...")
        print(f"✅ Safe exit! All movies found so far are saved in '{OUTPUT_FILE}'")
        sys.exit(0)

    print("\n🎉 BATCH COMPLETE!")
    print(f"📂 Open '{OUTPUT_FILE}' in Excel to see your collection!")


if __name__ == "__main__":
    main()