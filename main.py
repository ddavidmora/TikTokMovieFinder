import os
from dotenv import load_dotenv
from src.tiktok_loader import fetch_tiktok_metadata
from src.audio_loader import download_audio_from_tiktok
from src.ai_agent import extract_movie_from_text, analyze_audio_for_movie
from src.tmdb_client import search_tmdb

# Load env variables
load_dotenv()


def get_best_candidate(metadata, tiktok_url):
    """
    Phase 1: Determine the best movie candidate using Text first, then Audio if needed.
    """
    # 1. Prepare Text
    full_text = f"""
    Caption: {metadata['description']}
    Tags: {', '.join(metadata['tags'])}
    User Comments:
    {', '.join(metadata['comments'])}
    """
    print(f"📝 Found Text: {full_text[:200]}...")

    # 2. Analyze Text
    print("\n--- 2. ANALYZING TEXT ---")
    ai_result = extract_movie_from_text(full_text)

    # 3. Check Confidence (The "Guard Clause")
    # If we are confident (7+), return immediately. No need to download audio.
    if ai_result and ai_result.found_movie and ai_result.confidence_score >= 7:
        return ai_result

    # 4. If we are here, Text failed. Switch to Audio.
    if ai_result:
        print(f"⚠️ Text confidence low ({ai_result.confidence_score}/10). Trying audio...")
    else:
        print("⚠️ Text analysis failed. Trying audio...")

    print("\n--- 👂 SWITCHING TO AUDIO ANALYSIS ---")
    audio_path = download_audio_from_tiktok(tiktok_url)

    if not audio_path:
        print("❌ Could not download audio.")
        return ai_result  # Return the weak text result as fallback

    # 5. Analyze Audio
    audio_result = analyze_audio_for_movie(audio_path)

    # Cleanup file immediately
    if os.path.exists(audio_path):
        os.remove(audio_path)

    # If audio found something, it wins. Otherwise, return the weak text result.
    if audio_result and audio_result.found_movie:
        print(f"✅ Audio Analysis Succeeded! Found: {audio_result.movie_title}")
        return audio_result

    print("❌ Audio analysis also failed.")
    return ai_result


def verify_and_print(candidate):
    """
    Phase 2: Take the best candidate and verify it with TMDB.
    """
    if not candidate or not candidate.found_movie:
        print("\n❌ FAILED: AI could not find a movie in this TikTok.")
        return

    print(f"\n🤖 Final Guess: '{candidate.movie_title}' (Confidence: {candidate.confidence_score}/10)")
    print(f"🧠 Reasoning: {candidate.reasoning}")

    print("\n--- 3. VERIFYING WITH TMDB ---")
    movie_details = search_tmdb(candidate.movie_title)

    if movie_details:
        print(f"🎉 SUCCESS! Official Data Found:")
        print(f"🎬 Title:  {movie_details['title']} ({movie_details['year']})")
        print(f"⭐ Rating: {movie_details['rating']}/10")
        print(f"📜 Plot:   {movie_details['overview'][:100]}...")
        print(f"🖼️ Poster: {movie_details['poster_url']}")
    else:
        print("⚠️ AI found a name, but it's not in the movie database.")


def run_pipeline(tiktok_url):
    """
    The Orchestrator: Now simple and linear.
    """
    print("--- 1. FETCHING TIKTOK DATA ---")
    metadata = fetch_tiktok_metadata(tiktok_url)
    if not metadata:
        print("❌ Could not scrape TikTok.")
        return

    # Step A: Get the AI's opinion (Text or Audio)
    best_candidate = get_best_candidate(metadata, tiktok_url)

    # Step B: Verify it
    verify_and_print(best_candidate)


if __name__ == "__main__":
    link = input("Paste a TikTok link: ")
    run_pipeline(link)