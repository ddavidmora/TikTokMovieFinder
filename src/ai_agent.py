import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Native Client
client = genai.Client(api_key=api_key)


# 1. Define the Schema using Pydantic (Standard Industry Practice)
class MovieExtraction(BaseModel):
    found_movie: bool = Field(description="True if a specific movie is mentioned.")
    movie_title: str | None = Field(description="The exact title of the movie, if found.")
    confidence_score: int = Field(description="A score 1-10 of confidence.")
    reasoning: str = Field(description="Brief explanation of why you picked this title.")


def extract_movie_from_text(tiktok_text: str):
    """
    Sends text to Gemini and forces it to return JSON matching our schema.
    """
    prompt = f"""
    Analyze the following TikTok text and extract movie information.

    TEXT:
    {tiktok_text}
    """

    try:
        # 2. Call Gemini with "response_mime_type" set to JSON
        # We pass the Pydantic class directly to response_schema!
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Or 'gemini-1.5-flash'
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MovieExtraction
            ),
        )

        # 3. Parse the JSON result back into our Python Object
        # The AI returns a string, we turn it into a real object
        raw_json = json.loads(response.text)
        return MovieExtraction(**raw_json)

    except Exception as e:
        print(f"❌ AI Error: {e}")
        return None