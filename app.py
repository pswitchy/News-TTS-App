# app.py
"""
Main Streamlit application for News Summarization and Text-to-Speech.
"""

import streamlit as st
import pandas as pd
import json
import os
import time
import requests
import base64
from io import BytesIO

from utils import setup_directories, generate_sentiment_chart
import config

# Create necessary directories
setup_directories()

# Set page configuration
st.set_page_config(
    page_title=config.STREAMLIT_TITLE,
    page_icon="📰",
    layout="wide"
)

# API endpoint (change to deployed endpoint when available)
API_BASE_URL = "http://localhost:8000"

def load_css():
    """Load custom CSS styles."""
    st.markdown("""
    <style>
    .news-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #f9f9f9;
    }
    .positive {
        border-left: 5px solid #28a745;
    }
    .negative {
        border-left: 5px solid #dc3545;
    }
    .neutral {
        border-left: 5px solid #6c757d;
    }
    .sentiment-tag {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        color: white;
        display: inline-block;
        margin-right: 5px;
    }
    .positive-tag {
        background-color: #28a745;
    }
    .negative-tag {
        background-color: #dc3545;
    }
    .neutral-tag {
        background-color: #6c757d;
    }
    .topic-tag {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        background-color: #f0f0f0;
        color: #333;
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .audio-player {
        margin-top: 20px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

def fetch_company_news(company, max_articles=10):
    """
    Fetch news for a company from the API.
    
    Args:
        company: Company name
        max_articles: Maximum number of articles to fetch
    
    Returns:
        dict: News data or None if request failed
    """
    try:
        url = f"{API_BASE_URL}/news/{company}?max_articles={max_articles}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return None

def generate_audio(company, max_articles=5):
    """
    Generate audio for company news from the API.
    
    Args:
        company: Company name
        max_articles: Maximum number of articles to include
    
    Returns:
        str: Audio file path or None if request failed
    """
    try:
        url = f"{API_BASE_URL}/audio/{company}?max_articles={max_articles}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("audio_path")
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

def display_sentiment_tag(sentiment):
    """Display a sentiment tag."""
    tag_class = f"{sentiment.lower()}-tag"
    return f'<span class="sentiment-tag {tag_class}">{sentiment}</span>'

def display_topic_tag(topic):
    """Display a topic tag."""
    return f'<span class="topic-tag">{topic}</span>'

def display_news_card(article):
    """Display a news article card."""
    sentiment_class = article["sentiment"].lower()
    
    # Create HTML for sentiment tag
    sentiment_html = display_sentiment_tag(article["sentiment"])
    
    # Create HTML for topic tags
    topics_html = " ".join(display_topic_tag(topic) for topic in article["topics"])
    
    # Create HTML for news card
    html = f"""
    <div class="news-card {sentiment_class}">
        <h3>{article["title"]}</h3>
        <p>{article["summary"]}</p>
        <div>
            {sentiment_html}
            {topics_html}
        </div>
    </div>
    """
    
    return html

def main():
    """Main application function."""
    # Load custom CSS
    load_css()
    
    # App title and description
    st.title("News Summarization and Text-to-Speech App")
    st.markdown(config.STREAMLIT_DESCRIPTION)
    
    # Sidebar
    st.sidebar.title("Configure Analysis")
    
    # Option to select from predefined companies or enter custom company
    company_option = st.sidebar.radio(
        "Select company input method",
        ["Choose from list", "Enter custom company"]
    )
    
    if company_option == "Choose from list":
        company = st.sidebar.selectbox("Select a company", config.SAMPLE_COMPANIES)
    else:
        company = st.sidebar.text_input("Enter company name", "")
    
    # Number of articles to analyze
    num_articles = st.sidebar.slider("Number of articles to analyze", 3, 20, 10)
    
    # Action buttons
    col1, col2 = st.sidebar.columns(2)
    analyze_button = col1.button("Analyze News")
    tts_button = col2.button("Generate Audio")
    
    # Start API server if it's not running
    if not company:
        st.info("Please select or enter a company name to get started.")
        return
    
    if analyze_button:
        with st.spinner(f"Analyzing news for {company}..."):
            # Fetch news data from API
            news_data = fetch_company_news(company, num_articles)
            
            if news_data:
                # Store the result in session state
                st.session_state.news_data = news_data
                st.session_state.company = company
    
    if tts_button:
        if not hasattr(st.session_state, 'news_data'):
            st.warning("Please analyze the news first before generating audio.")
        else:
            with st.spinner("Generating Hindi audio..."):
                audio_path = generate_audio(st.session_state.company, min(5, num_articles))
                if audio_path:
                    st.session_state.audio_path = audio_path
    
    # Display results if available
    if hasattr(st.session_state, 'news_data'):
        news_data = st.session_state.news_data
        
        # Display company name and article count
        st.header(f"News Analysis for {news_data['company']}")
        st.subheader(f"Found {len(news_data['articles'])} articles")
        
        # Display overall sentiment analysis
        st.markdown("### Overall Sentiment Analysis")
        
        # Create columns for sentiment distribution and final analysis
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display sentiment distribution chart
            sentiment_dist = news_data['comparative_sentiment_score']['sentiment_distribution']
            
            # Create DataFrame for chart
            df = pd.DataFrame({
                'Sentiment': list(sentiment_dist.keys()),
                'Count': list(sentiment_dist.values())
            })
            
            # Display chart
            st.bar_chart(df.set_index('Sentiment'))
        
        with col2:
            # Display final sentiment analysis
            st.markdown(f"**Summary**: {news_data['final_sentiment_analysis']}")
            
            # Display topic overlap information
            topic_overlap = news_data['comparative_sentiment_score']['topic_overlap']
            if topic_overlap.get('common_topics'):
                st.markdown("**Common Topics Across Articles:**")
                for topic in topic_overlap['common_topics']:
                    st.markdown(f"- {topic}")
        
        # Display coverage differences
        st.markdown("### Coverage Differences")
        coverage_diffs = news_data['comparative_sentiment_score']['coverage_differences']
        if coverage_diffs:
            for diff in coverage_diffs:
                st.markdown(f"- **Comparison**: {diff['Comparison']}")
                st.markdown(f"  **Impact**: {diff['Impact']}")
        else:
            st.info("No significant coverage differences found.")
        
        # Display news articles
        st.markdown("### News Articles")
        for article in news_data['articles']:
            st.markdown(display_news_card(article), unsafe_allow_html=True)
            
            # Add a button to visit the original article if URL is available
            if 'url' in article:
                st.markdown(f"[Read full article]({article['url']})")
            
            st.markdown("---")
        
        # Display audio player if available
        if hasattr(st.session_state, 'audio_path'):
            st.markdown("### Hindi Audio Summary")
            
            # Display the audio player
            try:
                audio_file = open(st.session_state.audio_path, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
                
                # Add a download button for the audio
                st.download_button(
                    label="Download Audio",
                    data=audio_bytes,
                    file_name=os.path.basename(st.session_state.audio_path),
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"Error playing audio: {str(e)}")

if __name__ == "__main__":
    main()