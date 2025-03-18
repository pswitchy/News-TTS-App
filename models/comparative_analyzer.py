"""Comparative analysis module for analyzing multiple news articles."""

from typing import List, Dict, Any, Set
from collections import Counter

from utils import log_error

class ComparativeAnalyzer:
    """Class for comparing and analyzing multiple news articles."""
    
    def __init__(self):
        """Initialize the ComparativeAnalyzer."""
        pass
    
    def analyze(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comparative analysis across multiple articles.
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            Dict[str, Any]: Comparative analysis results
        """
        try:
            # Calculate sentiment distribution
            sentiment_distribution = self._calculate_sentiment_distribution(articles)
            
            # Analyze coverage differences
            coverage_differences = self._analyze_coverage_differences(articles)
            
            # Analyze topic overlap
            topic_overlap = self._analyze_topic_overlap(articles)
            
            return {
                "sentiment_distribution": sentiment_distribution,
                "coverage_differences": coverage_differences,
                "topic_overlap": topic_overlap
            }
        except Exception as e:
            log_error(e, "Comparative analysis")
            # Return empty analysis if it fails
            return {
                "sentiment_distribution": {"Positive": 0, "Negative": 0, "Neutral": 0},
                "coverage_differences": [],
                "topic_overlap": {"common_topics": [], "unique_topics_by_article": {}}
            }
    
    def _calculate_sentiment_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
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
    
    def _analyze_coverage_differences(self, articles: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Analyze differences in coverage between articles.
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            List[Dict[str, str]]: List of coverage comparisons
        """
        if len(articles) < 2:
            return []
        
        comparisons = []
        
        # Group articles by sentiment
        positive_articles = [a for a in articles if a.get("sentiment") == "Positive"]
        negative_articles = [a for a in articles if a.get("sentiment") == "Negative"]
        neutral_articles = [a for a in articles if a.get("sentiment") == "Neutral"]
        
        # Compare positive vs negative coverage
        if positive_articles and negative_articles:
            pos_topics = set()
            for article in positive_articles:
                pos_topics.update(article.get("topics", []))
            
            neg_topics = set()
            for article in negative_articles:
                neg_topics.update(article.get("topics", []))
            
            # Find unique topics in each sentiment group
            pos_unique = pos_topics - neg_topics
            neg_unique = neg_topics - pos_topics
            
            if pos_unique or neg_unique:
                comparison = {
                    "Comparison": f"Positive articles focus on {', '.join(list(pos_unique)[:3])} while negative articles focus on {', '.join(list(neg_unique)[:3])}.",
                    "Impact": "These differences in focus may significantly affect the overall perception of the company."
                }
                comparisons.append(comparison)
        
        # Find articles with contradictory information
        for i, article1 in enumerate(articles):
            for article2 in articles[i+1:]:
                # Skip if they have the same sentiment
                if article1.get("sentiment") == article2.get("sentiment"):
                    continue
                
                # Check for overlapping topics but different sentiments
                topics1 = set(article1.get("topics", []))
                topics2 = set(article2.get("topics", []))
                
                common_topics = topics1.intersection(topics2)
                
                if common_topics:
                    comparison = {
                        "Comparison": f"Article '{article1['title']}' ({article1['sentiment']}) and article '{article2['title']}' ({article2['sentiment']}) cover the same topics ({', '.join(list(common_topics))}) but have different sentiments.",
                        "Impact": "This contradiction may cause confusion among readers and investors about the company's actual performance or situation."
                    }
                    comparisons.append(comparison)
        
        # Limit to most significant comparisons
        return comparisons[:5]
    
    def _analyze_topic_overlap(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze topic overlap between articles.
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            Dict[str, Any]: Topic overlap analysis
        """
        if not articles:
            return {
                "common_topics": [],
                "unique_topics_by_article": {}
            }
        
        # Extract all topics
        all_topics = []
        for article in articles:
            all_topics.extend(article.get("topics", []))
        
        # Count topic frequency
        topic_counts = Counter(all_topics)
        
        # Find common topics (appear in multiple articles)
        common_topics = [topic for topic, count in topic_counts.items() if count > 1]
        
        # Find unique topics for each article
        unique_topics = {}
        for i, article in enumerate(articles):
            article_topics = set(article.get("topics", []))
            
            # Check if each topic is unique to this article
            unique_to_article = []
            for topic in article_topics:
                is_unique = True
                for j, other_article in enumerate(articles):
                    if i != j and topic in other_article.get("topics", []):
                        is_unique = False
                        break
                
                if is_unique:
                    unique_to_article.append(topic)
            
            if unique_to_article:
                article_title = article.get("title", f"Article {i+1}")
                unique_topics[article_title] = unique_to_article
        
        return {
            "common_topics": common_topics,
            "unique_topics_by_article": unique_topics
        }
    
    def generate_final_sentiment(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a final sentiment summary based on the analysis.
        
        Args:
            analysis: Comparative analysis results
        
        Returns:
            str: Final sentiment summary
        """
        try:
            # Get sentiment distribution
            distribution = analysis.get("sentiment_distribution", {})
            pos_count = distribution.get("Positive", 0)
            neg_count = distribution.get("Negative", 0)
            neu_count = distribution.get("Neutral", 0)
            
            total = pos_count + neg_count + neu_count
            if total == 0:
                return "No sentiment data available for this company."
            
            # Calculate percentages
            pos_pct = (pos_count / total) * 100 if total > 0 else 0
            neg_pct = (neg_count / total) * 100 if total > 0 else 0
            
            # Determine overall sentiment
            if pos_pct > 60:
                sentiment = "overwhelmingly positive"
            elif pos_pct > 50:
                sentiment = "generally positive"
            elif neg_pct > 60:
                sentiment = "overwhelmingly negative"
            elif neg_pct > 50:
                sentiment = "generally negative"
            else:
                sentiment = "mixed"
            
            # Get common topics
            topic_overlap = analysis.get("topic_overlap", {})
            common_topics = topic_overlap.get("common_topics", [])
            topic_mentions = ""
            if common_topics:
                topic_mentions = f" The most discussed topics are {', '.join(common_topics[:3])}."
            
            # Generate summary
            summary = f"The news coverage for this company is {sentiment}.{topic_mentions}"
            
            # Add additional insights based on sentiment distribution
            if pos_count > 0 and neg_count > 0:
                coverage_diffs = analysis.get("coverage_differences", [])
                if coverage_diffs:
                    first_diff = coverage_diffs[0]
                    summary += f" {first_diff.get('Comparison', '')}"
            
            return summary
        except Exception as e:
            log_error(e, "Final sentiment generation")
            return "Unable to generate a final sentiment analysis."