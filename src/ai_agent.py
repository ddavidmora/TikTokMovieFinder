import os
import json
import time
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Native Client
client = genai.Client(api_key=api_key)


# 1. Define the Schema
class MovieExtraction(BaseModel):
    found_movie: bool = Field(description="True if a specific movie is mentioned.")
    movie_title: str | None = Field(description="The exact title of the movie, if found.")
    confidence_score: int = Field(description="A score 1-10 of confidence.")
    reasoning: str = Field(description="Brief explanation of why you picked this title.")


def analyze_audio_for_movie(audio_path: str):
    """
    Uploads audio to Gemini and asks for identification.
    Includes a RETRY mechanism for Rate Limits (429).
    """
    print("📤 Uploading audio to Gemini Brain...")

    try:
        # 1. Upload the file
        audio_file = client.files.upload(file=audio_path)

        # 2. Wait for processing
        while audio_file.state.name == "PROCESSING":
            print("...processing audio...")
            time.sleep(1)
            audio_file = client.files.get(name=audio_file.name)

        if audio_file.state.name == "FAILED":
            print("❌ Audio processing failed.")
            return None

        # 3. Prompt the Vision/Audio Model
        prompt = """
        Listen to this audio clip carefully. 
        It likely contains dialogue, music, or sound effects from a movie or TV show.

        1. Identify the movie.
        2. Explain what is being said or heard that makes you sure.

        Return JSON matching this schema.
        """

        # --- RETRY LOGIC START ---
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[audio_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MovieExtraction
                ),
            )
        except Exception as e:
            if "429" in str(e):
                print("⏳ Rate Limit Hit. Waiting 30 seconds to cool down...")
                time.sleep(30)
                print("🔄 Retrying Audio Analysis...")
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[audio_file, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MovieExtraction
                    ),
                )
            else:
                raise e  # If it's not a rate limit, crash normally
        # --- RETRY LOGIC END ---

        return MovieExtraction(**json.loads(response.text))

    except Exception as e:
        print(f"❌ AI Audio Error: {e}")
        return None


def extract_movie_from_text(tiktok_text: str):
    """
    Sends text to Gemini and forces it to return JSON matching our schema.
    Includes a RETRY mechanism for Rate Limits (429).
    """
    prompt = f"""
    Analyze the following TikTok text and extract movie information.

    TEXT:
    {tiktok_text}
    """

    try:
        # --- RETRY LOGIC START ---
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MovieExtraction
                ),
            )
        except Exception as e:
            if "429" in str(e):
                print("⏳ Rate Limit Hit. Waiting 30 seconds to cool down...")
                time.sleep(30)
                print("🔄 Retrying Text Analysis...")
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MovieExtraction
                    ),
                )
            else:
                raise e
        # --- RETRY LOGIC END ---

        raw_json = json.loads(response.text)
        return MovieExtraction(**raw_json)

    except Exception as e:
        print(f"❌ AI Text Error: {e}")
        return None