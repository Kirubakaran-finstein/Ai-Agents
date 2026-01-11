# Cache for available models
_available_models = None

def get_available_models():
    """Get list of available models from API."""
    global _available_models
    if _available_models is None:
        try:
            import google.generativeai as genai
            models = genai.list_models()
            _available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        except Exception as e:
            # Fallback to best available models (with models/ prefix)
            _available_models = [
                "models/gemini-3-pro-preview",
                "models/gemini-3-flash-preview",
                "models/gemini-2.5-pro",
                "models/gemini-2.5-flash",
                "models/gemini-pro-latest",
                "models/gemini-flash-latest"
            ]
    return _available_models

def find_best_model(patterns, priority_order=None):
    """Find the best model matching patterns in priority order."""
    available = get_available_models()
    
    if priority_order:
        # Search in specified priority order
        for pattern in priority_order:
            for model in available:
                if pattern.lower() in model.lower():
                    return model
    
    # Search in order of patterns provided
    for pattern in patterns:
        for model in available:
            if pattern.lower() in model.lower():
                return model
    
    return None

def choose_model(task_complexity):
    """Choose the BEST available model - always uses maximum quality models.
    
    Uses the most advanced Pro models available regardless of task complexity.
    Priority: Gemini 3 Pro > Gemini 2.5 Pro > Gemini Pro Latest
    Returns full model path with 'models/' prefix.
    """
    # Always use the BEST Pro models - no simple/flash models
    # Priority: Gemini 3 Pro > Gemini 2.5 Pro > Gemini Pro Latest
    model = find_best_model(
        ["pro"],
        priority_order=[
            "gemini-3-pro",
            "gemini-2.5-pro",
            "gemini-pro-latest"
        ]
    )
    if model:
        return model
    
    # Fallback to best available pro model
    return "models/gemini-3-pro-preview"

def get_free_tier_models():
    """Get free tier models that don't require paid quota."""
    available = get_available_models()
    
    # Free tier models (typically have free quotas) - using models that actually exist
    free_models_priority = [
        "models/gemini-flash-latest",      # Free tier, always available
        "models/gemini-pro-latest",        # Free tier, always available
        "models/gemini-2.5-flash",        # May have free tier
        "models/gemini-2.5-pro",          # May have free tier
        "models/gemini-2.0-flash",        # Alternative free tier
    ]
    
    # Find available free tier models from the actual list
    found_free = []
    for free_model in free_models_priority:
        # Check if model exists in available models (exact match or contains)
        for avail_model in available:
            if free_model.lower() == avail_model.lower() or free_model.lower() in avail_model.lower():
                if free_model not in found_free:
                    found_free.append(free_model)
                break
    
    # If no matches, use models that are likely to be free tier
    if not found_free:
        # Try to find any flash or pro-latest models
        for avail_model in available:
            if "flash-latest" in avail_model.lower() or "pro-latest" in avail_model.lower():
                found_free.append(avail_model)
                break
        # Last resort - use first available flash model
        if not found_free:
            for avail_model in available:
                if "flash" in avail_model.lower() and "preview" not in avail_model.lower():
                    found_free.append(avail_model)
                    break
    
    return found_free if found_free else ["models/gemini-flash-latest", "models/gemini-pro-latest"]

def get_fallback_model(current_model):
    """Get next model in fallback chain when quota is exceeded.
    
    Fallback order: Gemini 3 Pro → Gemini 2.5 Pro → Gemini Pro Latest → Gemini Flash Latest
    Uses only models that actually exist in the API.
    """
    available = get_available_models()
    
    # Fallback chain preferences (will be filtered to only existing models)
    fallback_preferences = [
        "gemini-3-pro-preview",
        "gemini-2.5-pro",
        "gemini-pro-latest",
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-lite-latest"
    ]
    
    # Build valid chain from available models, in preference order
    valid_chain = []
    for pref in fallback_preferences:
        for avail_model in available:
            # Match if preference is in the available model name
            if pref.lower() in avail_model.lower():
                if avail_model not in valid_chain:
                    valid_chain.append(avail_model)
                break
    
    # If we have a valid chain, use it
    if valid_chain:
        try:
            # Find current model in chain (handle variations)
            current_index = -1
            for i, model in enumerate(valid_chain):
                # Extract model name without "models/" for comparison
                current_short = current_model.replace("models/", "").lower()
                model_short = model.replace("models/", "").lower()
                if current_short in model_short or model_short in current_short:
                    current_index = i
                    break
            
            if current_index >= 0 and current_index < len(valid_chain) - 1:
                return valid_chain[current_index + 1]
            elif current_index < 0:
                # Current model not in chain, return first free tier model from chain
                return valid_chain[0] if len(valid_chain) > 0 else get_free_tier_models()[0]
        except (ValueError, IndexError):
            pass
    
    # If current model not in chain, return first free tier model
    free_models = get_free_tier_models()
    if free_models:
        return free_models[0]
    
    # Last resort - return a model that definitely exists
    if available:
        # Prefer flash-latest or pro-latest
        for model in available:
            if "flash-latest" in model.lower() or "pro-latest" in model.lower():
                return model
        # Otherwise return first available flash model
        for model in available:
            if "flash" in model.lower():
                return model
        # Otherwise return first available
        return available[0]
    
    return "models/gemini-flash-latest"

def is_quota_error(error_msg):
    """Check if error is a quota/rate limit error."""
    quota_keywords = [
        "quota",
        "rate limit",
        "429",
        "exceeded",
        "free_tier",
        "billing"
    ]
    error_lower = error_msg.lower()
    return any(keyword in error_lower for keyword in quota_keywords)
