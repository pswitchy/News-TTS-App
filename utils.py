"""Utility functions for the News Summarization and TTS application."""

import os
import json
import requests
import re
import nltk
from typing import Dict, List, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import config

# Download NLTK resources if not already downloaded
def download_nltk_resources():
    """Download required NLTK resources."""
    resources = [
        'punkt',
        'stopwords',
        'vader_lexicon'  # Add this line
    ]
    
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(resource)

# Create necessary directories
def setup_directories():
    """Create necessary directories for the application."""
    directories = [
        config.TTS_OUTPUT_DIR,
        "cache",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Cache management
def get_cache_path(key: str) -> str:
    """
    Get the cache file path for a given key.
    
    Args:
        key: Cache key
    
    Returns:
        str: Path to the cache file
    """
    # Create a safe filename from the key
    safe_key = re.sub(r'[^\w]', '_', key)
    return os.path.join("cache", f"{safe_key}.json")

def save_to_cache(key: str, data: Any) -> None:
    """
    Save data to cache.
    
    Args:
        key: Cache key
        data: Data to cache
    """
    cache_path = get_cache_path(key)
    
    # Add timestamp for cache expiry
    cache_data = {
        "timestamp": datetime.now().timestamp(),
        "data": data
    }
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def load_from_cache(key: str) -> Optional[Any]:
    """
    Load data from cache if it exists and is not expired.
    
    Args:
        key: Cache key
    
    Returns:
        Optional[Any]: Cached data or None if not found or expired
    """
    cache_path = get_cache_path(key)
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check if cache is expired
        timestamp = cache_data.get("timestamp", 0)
        if (datetime.now().timestamp() - timestamp) > config.CACHE_EXPIRY:
            # Cache expired
            return None
        
        return cache_data.get("data")
    except Exception as e:
        print(f"Error loading cache: {str(e)}")
        return None

# Text processing utilities
def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Input text
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    return text

def extract_keywords(text: str, n: int = 5) -> List[str]:
    """
    Extract keywords from text using NLTK.
    
    Args:
        text: Input text
        n: Number of keywords to extract
    
    Returns:
        List[str]: List of keywords
    """
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    
    # Make sure NLTK resources are downloaded
    download_nltk_resources()
    
    # Tokenize and convert to lowercase
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    
    # Create frequency distribution
    from nltk.probability import FreqDist
    fdist = FreqDist(filtered_tokens)
    
    # Return top n keywords
    return [word for word, _ in fdist.most_common(n)]

# Visualization utilities
def generate_sentiment_chart(sentiment_data: Dict[str, int]) -> str:
    """
    Generate a base64-encoded sentiment distribution chart.
    
    Args:
        sentiment_data: Dictionary with sentiment counts
    
    Returns:
        str: Base64-encoded image
    """
    # Create figure
    plt.figure(figsize=(8, 5))
    
    # Create bar chart
    sentiments = list(sentiment_data.keys())
    counts = list(sentiment_data.values())
    colors = ['green', 'red', 'gray']
    
    plt.bar(sentiments, counts, color=colors[:len(sentiments)])
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    
    # Convert plot to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def translate_to_hindi(text: str) -> str:
    """
    Translate text from English to Hindi using Hugging Face Transformers.
    
    Args:
        text: English text
    
    Returns:
        str: Hindi text
    """
    try:
        from transformers import pipeline
        import torch  # Add this import
        
        # Use a faster model for translation
        translator = pipeline(
            "translation_en_to_hi", 
            model="Helsinki-NLP/opus-mt-en-hi",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Split into sentences for better translation
        sentences = nltk.sent_tokenize(text)
        translated = []
        
        for sent in sentences:
            if len(sent) > 512:
                # Split long sentences into chunks
                chunks = [sent[i:i+500] for i in range(0, len(sent), 500)]
                for chunk in chunks:
                    result = translator(chunk)
                    translated.append(result[0]['translation_text'])
            else:
                result = translator(sent)
                translated.append(result[0]['translation_text'])
        
        return ' '.join(translated)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

# Error handling utilities
def log_error(error: Exception, context: str = "") -> None:
    """
    Log an error to the error log file.
    
    Args:
        error: The exception object
        context: Additional context about where the error occurred
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = f"{timestamp} - {context}: {str(error)}\n"
    
    with open(os.path.join("logs", "error.log"), "a") as f:
        f.write(error_message)

# Request utilities
def make_request(url: str, headers: Dict = None) -> Optional[str]:
    """
    Make an HTTP request with proper error handling.
    
    Args:
        url: URL to request
        headers: Optional headers
    
    Returns:
        Optional[str]: Response text or None if request failed
    """
    if headers is None:
        headers = {
            "User-Agent": config.USER_AGENT
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        log_error(e, f"Request to {url}")
        return None

# Data formatting utilities
def format_final_output(company: str, articles: List[Dict], 
                        comparative_analysis: Dict, 
                        final_sentiment: str,
                        audio_path: Optional[str] = None) -> Dict:
    """
    Format the final output in the required structure.
    
    Args:
        company: Company name
        articles: List of processed articles
        comparative_analysis: Comparative analysis results
        final_sentiment: Final sentiment analysis text
        audio_path: Path to the generated audio file
    
    Returns:
        Dict: Formatted output
    """
    output = {
        "Company": company,
        "Articles": [
            {
                "Title": article["title"],
                "Summary": article["summary"],
                "Sentiment": article["sentiment"],
                "Topics": article["topics"]
            } for article in articles
        ],
        "Comparative Sentiment Score": {
            "Sentiment Distribution": comparative_analysis["sentiment_distribution"],
            "Coverage Differences": comparative_analysis["coverage_differences"],
            "Topic Overlap": comparative_analysis["topic_overlap"]
        },
        "Final Sentiment Analysis": final_sentiment
    }
    
    if audio_path:
        output["Audio"] = audio_path
    
    return output