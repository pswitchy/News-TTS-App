"""Sentiment analysis module for news articles."""

from typing import List, Dict, Any
import re
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from transformers import pipeline

from utils import clean_text, download_nltk_resources, log_error
import config

class SentimentAnalyzer:
    """Class for performing sentiment analysis on news articles."""
    
    def __init__(self):
        """Initialize the SentimentAnalyzer."""
        # Download required NLTK resources
        from utils import download_nltk_resources
        download_nltk_resources()
        
        # Initialize NLTK's SentimentIntensityAnalyzer
        self.sia = SentimentIntensityAnalyzer()
        
        # Initialize transformers pipeline for more advanced NLP tasks
        try:
            self.nlp_pipeline = pipeline("sentiment-analysis")
        except Exception as e:
            log_error(e, "Failed to initialize transformers pipeline")
            self.nlp_pipeline = None
    
    def analyze(self, text: str) -> str:
        """
        Analyze the sentiment of a text.
        
        Args:
            text: Text to analyze
        
        Returns:
            str: Sentiment category ("Positive", "Negative", or "Neutral")
        """
        # Clean the text
        cleaned_text = clean_text(text)
        
        # First try with transformers if available
        if self.nlp_pipeline:
            try:
                # Break text into chunks to avoid exceeding model's max length
                max_chunk_size = 512
                chunks = [cleaned_text[i:i+max_chunk_size] for i in range(0, len(cleaned_text), max_chunk_size)]
                
                # Get sentiment for each chunk
                sentiments = []
                for chunk in chunks:
                    if not chunk.strip():
                        continue
                    result = self.nlp_pipeline(chunk)
                    sentiments.append(result[0])
                
                # Calculate average sentiment
                if sentiments:
                    # Count positive and negative labels
                    positive_count = sum(1 for s in sentiments if s['label'] == 'POSITIVE')
                    negative_count = sum(1 for s in sentiments if s['label'] == 'NEGATIVE')
                    
                    if positive_count > negative_count:
                        return "Positive"
                    elif negative_count > positive_count:
                        return "Negative"
                    else:
                        return "Neutral"
            except Exception as e:
                log_error(e, "Transformers sentiment analysis")
                # Fall back to NLTK
        
        # Use NLTK's SentimentIntensityAnalyzer as fallback
        try:
            # Break text into sentences
            sentences = sent_tokenize(cleaned_text)
            
            # Analyze each sentence
            compound_scores = []
            for sentence in sentences:
                if not sentence.strip():
                    continue
                scores = self.sia.polarity_scores(sentence)
                compound_scores.append(scores['compound'])
            
            # Calculate average compound score
            if compound_scores:
                avg_compound = sum(compound_scores) / len(compound_scores)
                
                # Determine sentiment based on thresholds
                if avg_compound >= config.SENTIMENT_THRESHOLDS["positive"]:
                    return "Positive"
                elif avg_compound <= -config.SENTIMENT_THRESHOLDS["negative"]:
                    return "Negative"
                else:
                    return "Neutral"
            else:
                return "Neutral"
        except Exception as e:
            log_error(e, "NLTK sentiment analysis")
            return "Neutral"  # Default to neutral if both methods fail
    
    def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """
        Extract main topics from text.
        
        Args:
            text: Text to analyze
            max_topics: Maximum number of topics to extract
        
        Returns:
            List[str]: List of extracted topics
        """
        # Clean text
        cleaned_text = clean_text(text)
        
        # Download required NLTK resources if not already downloaded
        download_nltk_resources()
        
        try:
            # Tokenize text
            tokens = word_tokenize(cleaned_text.lower())
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
            
            # Get frequency distribution
            fdist = FreqDist(filtered_tokens)
            
            # Extract most common words as topics
            common_words = [word for word, _ in fdist.most_common(max_topics * 2)]
            
            # Use bigrams to identify multi-word topics
            bigrams = []
            for i in range(len(tokens) - 1):
                if tokens[i].isalpha() and tokens[i+1].isalpha():
                    if tokens[i] not in stop_words and tokens[i+1] not in stop_words:
                        bigrams.append(f"{tokens[i]} {tokens[i+1]}")
            
            # Get frequency distribution of bigrams
            fdist_bigrams = FreqDist(bigrams)
            common_bigrams = [bigram for bigram, _ in fdist_bigrams.most_common(max_topics)]
            
            # Combine unigrams and bigrams
            all_topics = common_words + common_bigrams
            
            # Normalize topic text (capitalize first letter)
            normalized_topics = [' '.join(word.capitalize() for word in topic.split()) for topic in all_topics]
            
            # Remove duplicates and limit to max_topics
            unique_topics = []
            for topic in normalized_topics:
                is_duplicate = False
                for existing_topic in unique_topics:
                    if topic in existing_topic or existing_topic in topic:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_topics.append(topic)
                    if len(unique_topics) >= max_topics:
                        break
            
            return unique_topics
        except Exception as e:
            log_error(e, "Topic extraction")
            return []  # Return empty list if extraction fails
    
    def analyze_sentiment_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate sentiment distribution across all articles.
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            Dict[str, int]: Count of each sentiment category
        """
        distribution = {
            "Positive": 0,
            "Negative": 0,
            "Neutral": 0
        }
        
        for article in articles:
            sentiment = article.get("sentiment", "Neutral")
            if sentiment in distribution:
                distribution[sentiment] += 1
        
        return distribution