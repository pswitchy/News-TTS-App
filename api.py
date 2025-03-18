# api.py
"""API for the News Summarization and Text-to-Speech application."""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
import os

from utils import setup_directories
from models.news_extractor import NewsExtractor
from models.sentiment_analyzer import SentimentAnalyzer
from models.comparative_analyzer import ComparativeAnalyzer
from models.text_to_speech import TextToSpeech
import config

# Create necessary directories
setup_directories()

app = FastAPI(
    title="News Summarization and TTS API",
    description="API for extracting, analyzing news articles and generating text-to-speech in Hindi",
    version="1.0.0",
    docs_url=config.API_DOCS_URL,
    redoc_url=config.API_REDOC_URL
)

class ArticleResponse(BaseModel):
    title: str
    summary: str
    sentiment: str
    topics: List[str]
    url: str

class ComparativeSentimentScore(BaseModel):
    sentiment_distribution: Dict[str, int]
    coverage_differences: List[Dict[str, str]]
    topic_overlap: Dict[str, Any]

class CompanyNewsResponse(BaseModel):
    company: str
    articles: List[ArticleResponse]
    comparative_sentiment_score: ComparativeSentimentScore
    final_sentiment_analysis: str
    audio_path: Optional[str] = None

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that returns API information."""
    return {
        "message": "News Summarization and TTS API",
        "version": "1.0.0",
        "endpoints": {
            "/news/{company}": "Get news summaries and analysis for a company",
            "/audio/{company}": "Generate Hindi TTS for company news summary"
        }
    }

@app.get("/news/{company}", response_model=CompanyNewsResponse, tags=["News"])
async def get_company_news(company: str, max_articles: int = Query(10, ge=1, le=20)):
    """
    Get news articles, summaries, sentiment analysis, and comparative analysis for a company.
    
    Args:
        company: Name of the company to get news for
        max_articles: Maximum number of articles to retrieve (default: 10)
    
    Returns:
        CompanyNewsResponse: Structured news summary and analysis
    """
    try:
        # Initialize components
        news_extractor = NewsExtractor()
        sentiment_analyzer = SentimentAnalyzer()
        comparative_analyzer = ComparativeAnalyzer()
        
        # Extract news articles
        articles = news_extractor.extract_news(company, max_articles=max_articles)
        
        if not articles:
            raise HTTPException(status_code=404, detail=f"No news articles found for {company}")
        
        # Process articles
        processed_articles = []
        for article in articles:
            # Analyze sentiment
            sentiment = sentiment_analyzer.analyze(article["content"])
            
            # Extract topics
            topics = sentiment_analyzer.extract_topics(article["content"])
            
            processed_article = {
                "title": article["title"],
                "summary": article["summary"],
                "sentiment": sentiment,
                "topics": topics,
                "url": article["url"]
            }
            processed_articles.append(processed_article)
        
        # Perform comparative analysis
        comparative_analysis = comparative_analyzer.analyze(processed_articles)
        
        # Generate final sentiment summary
        final_sentiment = comparative_analyzer.generate_final_sentiment(comparative_analysis)
        
        # Create response
        response = {
            "company": company,
            "articles": processed_articles,
            "comparative_sentiment_score": comparative_analysis,
            "final_sentiment_analysis": final_sentiment
        }
        
        return response
    
    except Exception as e:
        # Log the error
        print(f"Error processing request for {company}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/audio/{company}", tags=["Audio"])
async def generate_audio(company: str, max_articles: int = Query(5, ge=1, le=10)):
    """
    Generate Hindi TTS audio for company news summary.
    
    Args:
        company: Name of the company to generate audio for
        max_articles: Maximum number of articles to summarize in audio (default: 5)
    
    Returns:
        dict: Path to the generated audio file
    """
    try:
        # Get news and analysis data
        news_data = await get_company_news(company, max_articles)
        
        # Initialize TTS engine
        tts_engine = TextToSpeech()
        
        # Generate text for TTS
        text_for_tts = f"{company} के बारे में समाचार विश्लेषण। "
        text_for_tts += f"कुल {len(news_data['articles'])} समाचार लेख मिले। "
        
        # Add sentiment summary
        text_for_tts += f"{news_data['final_sentiment_analysis']} "
        
        # Add brief summary of top articles
        for i, article in enumerate(news_data['articles'][:3]):
            text_for_tts += f"समाचार {i+1}: {article['title']}. {article['summary']} "
        
        # Generate audio
        audio_path = tts_engine.generate(text_for_tts, company)
        
        return {"company": company, "audio_path": audio_path}
    
    except Exception as e:
        # Log the error
        print(f"Error generating audio for {company}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

@app.get("/companies", tags=["Companies"])
async def get_sample_companies():
    """Get a list of sample companies that can be used for testing."""
    return {"companies": config.SAMPLE_COMPANIES}

def start_api():
    """Start the FastAPI server using uvicorn."""
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

if __name__ == "__main__":
    start_api()