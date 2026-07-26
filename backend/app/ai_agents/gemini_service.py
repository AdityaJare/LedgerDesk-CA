import logging
import asyncio
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger("uvicorn.error")

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set in backend/.env. AI agents will run in fallback production mode.")

# List of preferred models for CA practice AI co-pilot
GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

def _sync_generate(prompt: str, system_instruction: str = None) -> str:
    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = e
            logger.warning(f"Gemini model {model_name} failed: {str(e)}. Trying fallback model...")
    
    if last_error:
        raise last_error
    return ""

async def generate_response(prompt: str, system_instruction: str = None) -> str:
    if not settings.GEMINI_API_KEY:
        return (
            "[PRODUCTION DRAFT MODE — API KEY NOT SET]\n\n"
            "OFFICIAL LEGAL REPLY DRAFT\n"
            "Before: The Assistant Commissioner of Central Tax / Income Tax Assessing Officer\n\n"
            "Sub: Detailed Submissions in Response to Statutory Notice / SCN\n"
            "Ref: Notice Details provided in request\n\n"
            "Respected Sir/Madam,\n\n"
            "1. STATEMENT OF FACTS:\n"
            "The Assessee is a registered taxpayer complying with all statutory provisions. The subject notice alleging variance/non-compliance is based on preliminary portal data matching without accounting for timing differences and valid tax invoices available on record.\n\n"
            "2. STATUTORY LEGAL PROVISIONS & RELEVANT CITATIONS:\n"
            "- Section 16(2) of CGST Act, 2017: Input Tax Credit (ITC) eligibility based on tax invoice possession and actual receipt of goods/services.\n"
            "- Section 42/43A of CGST Act & CBIC Circular No. 183/15/2022-GST: Procedure for verification of ITC mismatch for FY 2017-18 & 2018-19.\n"
            "- Supreme Court Ruling in Union of India v. Bharti Airtel Ltd (2021): Form GSTR-2A is a self-generated read-only statement and cannot override valid books of accounts.\n\n"
            "3. PRAYER / RELIEF REQUESTED:\n"
            "In light of the above facts, statutory sections, and annexed reconciliation statements, it is respectfully prayed that the proposed demand/penalty be dropped in full.\n\n"
            "Yours faithfully,\n"
            "For & on behalf of the Assessee\n"
            "Authorized Representative (Chartered Accountant)"
        )
    
    try:
        # Non-blocking async execution using thread pool
        return await asyncio.to_thread(_sync_generate, prompt, system_instruction)
    except Exception as e:
        logger.error(f"All Gemini API model calls failed: {str(e)}")
        raise e

