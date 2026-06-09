import json
import requests
import config

SYSTEM_PROMPT = """You are CineMatch AI Companion, a premium movie discovery assistant. 
Your goal is to suggest personalized movie recommendations based on user prompts.

You must respond ONLY with a raw, valid JSON object. Do not wrap the JSON output in markdown formatting like ```json ... ```.

The JSON object must have exactly the following structure:
{
  "message": "A friendly, helpful conversational message (1-2 sentences) explaining how you selected these movies.",
  "recommendations": [
    {
      "title": "Exact Movie Title",
      "explanation": "A concise 1-2 sentence explanation of why this movie matches their criteria.",
      "mood_tags": ["tag1", "tag2"]
    }
  ]
}

Recommend up to 6 movies. Ensure the movie titles are well-known and standard (e.g., "Interstellar", "Inception", "The Dark Knight")."""

def get_mock_ai_response(prompt):
    """Provides a realistic mock recommendation list for testing without API keys."""
    prompt_lower = prompt.lower()
    
    mock_data = {
        "message": "Welcome to CineMatch! Here are some curated recommendations matching your theme. Add your API keys to the .env file to enable live AI recommendations.",
        "recommendations": []
    }
    
    # Check for keywords to make recommendations feel smart
    if "interstellar" in prompt_lower or "sci-fi" in prompt_lower or "science fiction" in prompt_lower:
        mock_data["recommendations"] = [
            {
                "title": "Inception",
                "explanation": "A mind-bending sci-fi heist film from Christopher Nolan, sharing the same grand scale and intellectual depth as Interstellar.",
                "mood_tags": ["mind-bending", "thrilling"]
            },
            {
                "title": "The Martian",
                "explanation": "An optimistic and scientifically accurate survival story in space, sharing themes of human ingenuity and exploration.",
                "mood_tags": ["inspiring", "science-heavy"]
            },
            {
                "title": "Arrival",
                "explanation": "A thoughtful sci-fi drama focused on linguistics and first contact, echoing the emotional core and mystery of Interstellar.",
                "mood_tags": ["philosophical", "mystery"]
            },
            {
                "title": "Contact",
                "explanation": "A classic space exploration film dealing with the search for extraterrestrial life and the emotional bond between a daughter and father.",
                "mood_tags": ["emotional", "awe-inspiring"]
            }
        ]
    elif "thriller" in prompt_lower or "plot twist" in prompt_lower or "twist" in prompt_lower:
        mock_data["recommendations"] = [
            {
                "title": "Shutter Island",
                "explanation": "A brilliant psychological thriller directed by Martin Scorsese with one of the most famous plot twists in cinema history.",
                "mood_tags": ["suspenseful", "dark"]
            },
            {
                "title": "The Prestige",
                "explanation": "Two rival magicians engage in competitive obsession, leading to a shocking twist that recontextualizes the entire movie.",
                "mood_tags": ["mysterious", "intellectual"]
            },
            {
                "title": "Se7en",
                "explanation": "A dark, atmospheric detective thriller tracking a serial killer, culminating in a legendary and devastating twist ending.",
                "mood_tags": ["gritty", "tense"]
            },
            {
                "title": "Gone Girl",
                "explanation": "A suspenseful thriller analyzing marriage, media, and deception, filled with unpredictable narrative shifts.",
                "mood_tags": ["cynical", "shocking"]
            }
        ]
    elif "feel-good" in prompt_lower or "happy" in prompt_lower or "weekend" in prompt_lower or "comedy" in prompt_lower:
        mock_data["recommendations"] = [
            {
                "title": "The Intouchables",
                "explanation": "An incredibly heartwarming French comedy-drama about an unlikely friendship, filled with laughter and positive energy.",
                "mood_tags": ["uplifting", "heartwarming"]
            },
            {
                "title": "Forrest Gump",
                "explanation": "The life story of a simple man who witnesses history, reminding viewers of the kindness of the human spirit.",
                "mood_tags": ["emotional", "wholesome"]
            },
            {
                "title": "Chef",
                "explanation": "A charming and delightful film about a chef restarting his career in a food truck while bonding with his young son.",
                "mood_tags": ["feel-good", "mouth-watering"]
            },
            {
                "title": "Little Miss Sunshine",
                "explanation": "A quirky family comedy-drama about a road trip that proves dysfunctional families can be the most supportive.",
                "mood_tags": ["witty", "eccentric"]
            }
        ]
    else:
        # Default fallback list
        mock_data["recommendations"] = [
            {
                "title": "Avatar",
                "explanation": "An epic sci-fi adventure demonstrating boundary-pushing visual effects and worldbuilding.",
                "mood_tags": ["visual-spectacle", "adventure"]
            },
            {
                "title": "The Dark Knight",
                "explanation": "The definitive modern superhero movie, offering a gritty, realistic crime thriller with legendary performances.",
                "mood_tags": ["dark", "action-packed"]
            },
            {
                "title": "Pulp Fiction",
                "explanation": "Quentin Tarantino's iconic crime comedy with non-linear storytelling and unforgettable dialogue.",
                "mood_tags": ["stylized", "dark-comedy"]
            },
            {
                "title": "Fight Club",
                "explanation": "A satirical thriller analyzing modern consumerism, featuring a mind-blowing twist and stylistic direction.",
                "mood_tags": ["rebellious", "mind-bending"]
            }
        ]
        
    return mock_data

def query_groq(prompt):
    """Sends recommendation request to Groq API."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",  # Standard, fast active Groq model
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def query_gemini(prompt):
    """Sends recommendation request to Google Gemini API."""
    # Using Gemini's developer API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={config.GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # We combine the system prompt and user query in one content block
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser request: {prompt}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    
    # Parse Gemini's candidate output text
    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]

def query_openai(prompt):
    """Sends recommendation request to OpenAI API."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def get_ai_movie_recommendations(prompt):
    """
    Main entry point for fetching AI recommendations.
    Queries the active provider (Groq, Gemini, or OpenAI) and returns parsed JSON.
    Falls back to mock data if no keys are set or errors occur.
    """
    active_llm = config.get_active_llm()
    
    if not active_llm:
        return get_mock_ai_response(prompt)
        
    try:
        if active_llm == "groq":
            raw_response = query_groq(prompt)
        elif active_llm == "gemini":
            raw_response = query_gemini(prompt)
        elif active_llm == "openai":
            raw_response = query_openai(prompt)
        else:
            return get_mock_ai_response(prompt)
            
        # Parse output JSON string
        # Clean potential markdown wrapping just in case
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.split("```json")[1]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response.rsplit("```", 1)[0]
            
        parsed_json = json.loads(cleaned_response.strip())
        
        # Ensure recommendations array is present
        if "recommendations" not in parsed_json:
            parsed_json["recommendations"] = []
            
        return parsed_json
        
    except Exception as e:
        print(f"Error querying active LLM provider ({active_llm}): {e}")
        # Return fallback with error details
        fallback = get_mock_ai_response(prompt)
        fallback["message"] = f"[API Error: {e}]. Displaying fallback recommendations:"
        return fallback
