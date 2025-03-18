# config.py
"""Configuration settings for the application."""

# API configuration
API_HOST = "localhost"
API_PORT = 8000
API_DOCS_URL = "/docs"
API_REDOC_URL = "/redoc"
NEWSAPI_KEY = "9dc22142fbcf4da7ac4c8afc7c9045df"

# Web scraping configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 10  # seconds
MAX_ARTICLES = 10

# Sentiment analysis configuration
SENTIMENT_THRESHOLDS = {
    "positive": 0.6,
    "negative": 0.4,
}

# Text-to-Speech configuration
TTS_DEFAULT_VOICE = "female"
TTS_DEFAULT_SPEED = 1.0
TTS_OUTPUT_DIR = "output/audio"

# Streamlit configuration
STREAMLIT_TITLE = "News Summarization and TTS App"
STREAMLIT_DESCRIPTION = """
    Enter a company name to get summaries and sentiment analysis of recent news articles.
    The tool will also generate Hindi audio for the summarized content.
"""

# Sample companies for dropdown
SAMPLE_COMPANIES = [
    "Tesla",
    "Apple",
    "Microsoft",
    "Google",
    "Amazon",
    "Meta",
    "Netflix",
    "Nvidia",
    "Reliance Industries",
    "Tata Motors"
]

# Cache settings
CACHE_EXPIRY = 3600  # 1 hour

# Demo mode (limits API calls)
DEMO_MODE = False