"""
AI-powered insights module for burnout analysis.
Uses OpenAI API to provide personalized insights and recommendations based on user data.
"""

import os
import json
import logging
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class BurnoutInsightsEngine:
    """
    Advanced AI engine that analyzes user health metrics and provides personalized insights.
    Uses OpenAI GPT to generate context-aware recommendations and answer user queries.
    """
    
    def __init__(self, api_key=None):
        """Initialize the insights engine with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. AI insights will not be available.")
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def _prepare_metrics_context(self, metrics_data, days=7):
        """
        Create a structured context from user metrics data for the AI.
        
        Args:
            metrics_data: List of daily metrics records
            days: Number of recent days to include
        
        Returns:
            str: Formatted context string with recent metrics
        """
        # Sort data by date (newest first)
        sorted_data = sorted(
            metrics_data, 
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        
        # Take only the most recent days
        recent_data = sorted_data[:days]
        
        # Format the metrics as a structured text for the model
        context = "RECENT HEALTH METRICS (LAST 7 DAYS):\n\n"
        
        for record in recent_data:
            date_str = record.get("date", "")
            recovery = record.get("recovery_score")
            mood = record.get("mood_rating")
            hrv = record.get("hrv")
            strain = record.get("strain")
            sleep_quality = record.get("sleep_quality")
            burnout_risk = record.get("burnout_current")
            
            context += f"Date: {date_str}\n"
            context += f"Recovery Score: {recovery if recovery is not None else 'N/A'}/100\n"
            context += f"Mood Rating: {mood if mood is not None else 'N/A'}/10\n"
            if hrv is not None:
                context += f"HRV: {hrv:.1f} ms\n"
            else:
                context += "HRV: N/A\n"
                
            if strain is not None:
                context += f"Strain: {strain:.1f}/21\n"
            else:
                context += "Strain: N/A\n"
                
            if sleep_quality is not None:
                context += f"Sleep Quality: {sleep_quality:.1f}%\n"
            else:
                context += "Sleep Quality: N/A\n"
                
            if burnout_risk is not None:
                context += f"Burnout Risk: {burnout_risk:.1f}%\n"
            else:
                context += "Burnout Risk: N/A\n"
            
            # Include notes if available
            notes = record.get("notes")
            if notes:
                context += f"Notes: {notes}\n"
            
            context += "\n"
        
        return context
    
    def _prepare_trends_context(self, metrics_data):
        """
        Analyze trends in the data to provide additional context for the AI.
        
        Args:
            metrics_data: List of daily metrics records
            
        Returns:
            str: Formatted trend analysis
        """
        # Sort data by date (oldest first for trend analysis)
        sorted_data = sorted(
            metrics_data, 
            key=lambda x: x.get("date", "")
        )
        
        if len(sorted_data) < 3:
            return "TRENDS: Insufficient data for trend analysis.\n\n"
        
        # Extract key metrics for trend analysis
        recovery_scores = [r.get("recovery_score") for r in sorted_data if r.get("recovery_score") is not None]
        mood_ratings = [r.get("mood_rating") for r in sorted_data if r.get("mood_rating") is not None]
        burnout_risks = [r.get("burnout_current") for r in sorted_data if r.get("burnout_current") is not None]
        
        trends = "TRENDS ANALYSIS:\n\n"
        
        # Analyze recovery trends
        if len(recovery_scores) >= 3:
            recent_avg = sum(recovery_scores[-3:]) / 3
            overall_avg = sum(recovery_scores) / len(recovery_scores)
            trends += f"Recent Recovery (3-day avg): {recent_avg:.1f}, Overall: {overall_avg:.1f}\n"
            trends += f"Recovery Trend: {'Improving' if recent_avg > overall_avg else 'Declining'}\n\n"
        
        # Analyze mood trends
        if len(mood_ratings) >= 3:
            recent_avg = sum(mood_ratings[-3:]) / 3
            overall_avg = sum(mood_ratings) / len(mood_ratings)
            trends += f"Recent Mood (3-day avg): {recent_avg:.1f}, Overall: {overall_avg:.1f}\n"
            trends += f"Mood Trend: {'Improving' if recent_avg > overall_avg else 'Declining'}\n\n"
        
        # Analyze burnout risk trends
        if len(burnout_risks) >= 3:
            recent_avg = sum(burnout_risks[-3:]) / 3
            overall_avg = sum(burnout_risks) / len(burnout_risks)
            trends += f"Recent Burnout Risk (3-day avg): {recent_avg:.1f}%, Overall: {overall_avg:.1f}%\n"
            trends += f"Burnout Risk Trend: {'Increasing' if recent_avg > overall_avg else 'Decreasing'}\n\n"
        
        return trends
    
    def generate_insight(self, metrics_data, query=None):
        """
        Generate AI-powered insights based on user metrics and optional query.
        
        Args:
            metrics_data: List of daily metrics records
            query: Optional user question about their data
            
        Returns:
            dict: Response with insight text and metadata
        """
        if not self.api_key or not metrics_data:
            return {
                "error": "Missing API key or data",
                "insight": "AI insights unavailable. Please check your configuration."
            }
        
        try:
            # Prepare context from metrics data
            metrics_context = self._prepare_metrics_context(metrics_data)
            trends_context = self._prepare_trends_context(metrics_data)
            
            # Default prompt if no query
            if not query:
                query = "Based on my recent health metrics, provide insights about my burnout risk and specific, actionable recommendations to improve my well-being."
            
            # Create system prompt with instructions
            system_prompt = """
You are a professional health analytics AI assistant specializing in burnout prevention. Your expertise includes analyzing biometric data (HRV, recovery, sleep), mood fluctuations, and their correlation with burnout risk. You communicate in a supportive, constructive manner, offering personalized insights while avoiding generic advice.

Your primary objectives are to:
1. Analyze the user's health data to identify patterns and risk factors
2. Provide specific, data-driven insights about their burnout risk level
3. Offer 2-3 highly specific and personalized recommendations relevant to their situation
4. Respond directly to any questions they ask about their data
5. Format your response to be easy to read with concise sections

Format your response with markdown headers for each section and bullet points for recommendations.
Keep your entire response under 350 words, prioritizing specificity and relevance over length.
"""

            # Prepare the messages for the API call
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here's my health data:\n\n{metrics_context}\n{trends_context}\n\nMy question: {query}"}
            ]
            
            # Call the OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "gpt-4-turbo-preview",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=30  # Add timeout to prevent hanging requests
                )
                
                # Check if the request was successful
                response.raise_for_status()
                response_data = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"API request error: {str(e)}")
                return {
                    "success": False,
                    "error": "OpenAI API key missing or invalid",
                    "insight": "AI insights require a valid OpenAI API key. Please add your API key to the .env file."
                }
            
            # Extract the AI's reply
            if "choices" in response_data and len(response_data["choices"]) > 0:
                insight_text = response_data["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "insight": insight_text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"API Error: {response_data}")
                return {
                    "error": "Failed to generate insights",
                    "insight": "Sorry, I couldn't analyze your data at this time."
                }
        
        except Exception as e:
            logger.error(f"Error generating insight: {str(e)}")
            return {
                "error": str(e),
                "insight": "An error occurred while generating insights."
            }
    
    def ask_about_data(self, metrics_data, question):
        """
        Answer specific questions about the user's health data.
        
        Args:
            metrics_data: List of daily metrics records
            question: User's specific question
            
        Returns:
            dict: Response with answer and metadata
        """
        return self.generate_insight(metrics_data, query=question)


# Create a singleton instance
insights_engine = BurnoutInsightsEngine()

def get_burnout_insights(metrics_data, query=None):
    """
    Public function to get burnout insights.
    
    Args:
        metrics_data: List of daily metrics records
        query: Optional question from user
        
    Returns:
        dict: AI insights response
    """
    global insights_engine
    
    # Set the API key if it's in the environment
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and not insights_engine.api_key:
        insights_engine = BurnoutInsightsEngine(api_key)
    
    return insights_engine.generate_insight(metrics_data, query)


if __name__ == "__main__":
    # Test the module
    print("Testing AI Insights module...")
    
    # Sample data
    test_data = [
        {
            "date": "2025-03-06",
            "recovery_score": 70,
            "mood_rating": 6,
            "hrv": 52,
            "strain": 10.5,
            "sleep_quality": 85,
            "burnout_current": 40,
            "notes": "Feeling okay, but a bit tired."
        },
        {
            "date": "2025-03-05",
            "recovery_score": 65,
            "mood_rating": 5,
            "hrv": 48,
            "strain": 12.2,
            "sleep_quality": 75,
            "burnout_current": 45,
            "notes": "Work was stressful today."
        }
    ]
    
    # Test with API key from env var
    response = get_burnout_insights(test_data)
    print(json.dumps(response, indent=2))