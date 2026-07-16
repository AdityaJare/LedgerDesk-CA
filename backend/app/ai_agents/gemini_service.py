import logging
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger("uvicorn.error")

# Configure Gemini if key is provided
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. AI agents will run in mock fallback mode.")

async def generate_response(prompt: str, system_instruction: str = None) -> str:
    if not settings.GEMINI_API_KEY:
        return "MOCK FALLBACK RESPONSE: Gemini API key is not configured in .env. Please configure GEMINI_API_KEY to enable live Indian law citation and drafting support."
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        # Running standard sync SDK generate call.
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API generation failed: {str(e)}")
        raise e
