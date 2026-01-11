import os
import warnings
from dotenv import load_dotenv

# Suppress deprecation warning - google.generativeai still works
# Use simplefilter to catch all FutureWarnings from this module
warnings.simplefilter("ignore", FutureWarning)

try:
    import google.generativeai as genai
except ImportError:
    try:
        # Try new package name
        import google.genai as genai
    except ImportError:
        raise ImportError("Neither google.generativeai nor google.genai is installed. Please install: pip install google-generativeai")

# Re-enable warnings for other modules (optional, but cleaner)
warnings.resetwarnings()
warnings.filterwarnings("ignore", message=".*google.generativeai.*", category=FutureWarning)

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in .env file or environment variable.")

genai.configure(api_key=api_key)

def stream_gemini(prompt, system, model, max_retries=3, fallback_on_quota=True):
    """Stream Gemini response with retry logic and automatic fallback to free tier models.
    
    Args:
        prompt: The prompt to send
        system: System instruction
        model: Initial model to use
        max_retries: Maximum retry attempts
        fallback_on_quota: If True, automatically fallback to free tier models on quota errors
    """
    from model_router import is_quota_error, get_fallback_model
    
    current_model = model
    models_tried = []
    
    for attempt in range(max_retries * 2):  # Allow more attempts for fallback
        try:
            # Keep 'models/' prefix if present (newer API versions require it)
            # If not present, add it for compatibility
            if not current_model.startswith('models/'):
                model_name = f"models/{current_model}"
            else:
                model_name = current_model
            
            # Silent model switch - no output needed
            pass
            
            genai_model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system
            )
            response = genai_model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return  # Success, exit retry loop
        except Exception as e:
            error_msg = str(e)
            models_tried.append(current_model)
            
            # Check if it's a quota error and we should fallback
            if fallback_on_quota and is_quota_error(error_msg):
                fallback_model = get_fallback_model(current_model)
                if fallback_model != current_model and fallback_model not in models_tried:
                    # Silent fallback
                    current_model = fallback_model
                    continue  # Try with fallback model
            
            # If model not found (404), also try fallback
            if fallback_on_quota and ("404" in error_msg or "not found" in error_msg.lower()):
                fallback_model = get_fallback_model(current_model)
                if fallback_model != current_model and fallback_model not in models_tried:
                    # Silent fallback - no message
                    current_model = fallback_model
                    continue  # Try with fallback model
            
            # If model not found and no fallback available
            if "404" in error_msg or "not found" in error_msg.lower():
                if attempt >= max_retries - 1:
                    yield f"\n[Error: Model '{current_model}' not found. Please check available models.]"
                    raise Exception(f"Model '{current_model}' not found: {error_msg}")
            
            # If we've exhausted all retries and fallbacks
            if attempt >= max_retries - 1:
                yield f"\n[Error: {error_msg} - Max retries reached]"
                raise
            
            yield f"\n[Retry {attempt + 1}/{max_retries}...]"

def call_gemini(prompt, system, model, max_retries=3, fallback_on_quota=True):
    """Non-streaming Gemini call with automatic fallback to free tier models.
    
    Args:
        prompt: The prompt to send
        system: System instruction
        model: Initial model to use
        max_retries: Maximum retry attempts
        fallback_on_quota: If True, automatically fallback to free tier models on quota errors
    """
    from model_router import is_quota_error, get_fallback_model
    
    current_model = model
    models_tried = []
    
    for attempt in range(max_retries * 2):  # Allow more attempts for fallback
        try:
            # Keep 'models/' prefix if present (newer API versions require it)
            # If not present, add it for compatibility
            if not current_model.startswith('models/'):
                model_name = f"models/{current_model}"
            else:
                model_name = current_model
            
            genai_model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system
            )
            response = genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            models_tried.append(current_model)
            
            # Check if it's a quota error and we should fallback
            if fallback_on_quota and is_quota_error(error_msg):
                fallback_model = get_fallback_model(current_model)
                if fallback_model != current_model and fallback_model not in models_tried:
                    # Silent fallback
                    current_model = fallback_model
                    continue  # Try with fallback model
            
            # If model not found (404), also try fallback
            if fallback_on_quota and ("404" in error_msg or "not found" in error_msg.lower()):
                fallback_model = get_fallback_model(current_model)
                if fallback_model != current_model and fallback_model not in models_tried:
                    # Silent fallback
                    current_model = fallback_model
                    continue  # Try with fallback model
            
            # If model not found and no fallback available
            if "404" in error_msg or "not found" in error_msg.lower():
                if attempt >= max_retries - 1:
                    raise Exception(f"Model '{current_model}' not found. Available models may have changed. Error: {error_msg}")
            
            # If we've exhausted all retries and fallbacks
            if attempt >= max_retries - 1:
                raise Exception(f"Gemini API error after {max_retries} attempts: {error_msg}")
            continue
