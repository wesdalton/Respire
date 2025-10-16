"""
AI Insights Service
Generate personalized health insights using OpenAI GPT-4 with structured outputs
"""
import os
from typing import Dict, List, Any, Optional
from datetime import date, datetime
from enum import Enum
import json


class AIInsightsService:
    """Generate AI-powered health insights"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4"

        if not self.api_key or self.api_key == "PLACEHOLDER":
            print("⚠️  WARNING: OPENAI_API_KEY not set")
            print("   AI insights will not work until configured")
            self.enabled = False
        else:
            self.enabled = True

    async def generate_insight(
        self,
        insight_type: str,
        health_metrics: List[Dict[str, Any]],
        mood_ratings: List[Dict[str, Any]],
        burnout_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI insight based on user's health data

        Args:
            insight_type: Type of insight (weekly_summary, burnout_alert, trend_analysis)
            health_metrics: Recent health metrics
            mood_ratings: Recent mood ratings
            burnout_analysis: Burnout risk analysis from calculator

        Returns:
            Dictionary with title, content, recommendations
        """
        if not self.enabled:
            return self._generate_fallback_insight(
                insight_type,
                health_metrics,
                mood_ratings,
                burnout_analysis
            )

        try:
            import openai
            openai.api_key = self.api_key

            # Prepare data summary for GPT
            data_summary = self._prepare_data_summary(
                health_metrics,
                mood_ratings,
                burnout_analysis
            )

            # Create prompt based on insight type
            prompt = self._create_prompt(insight_type, data_summary)

            # Get structured schema for this insight type
            response_format = self._get_response_schema(insight_type)

            # Call OpenAI API with structured outputs
            response = openai.chat.completions.create(
                model="gpt-4o-2024-08-06",  # Model that supports structured outputs
                messages=[
                    {
                        "role": "system",
                        "content": "You are a health and wellness coach specializing in burnout prevention. Provide empathetic, actionable advice based on user's health data. Always respond with structured JSON data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=response_format,
                temperature=0.7
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Parse structured JSON response
            structured_data = json.loads(content)

            # Convert structured data to our format
            return self._format_structured_response(
                structured_data,
                insight_type,
                "gpt-4o-2024-08-06",
                tokens_used
            )

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_fallback_insight(
                insight_type,
                health_metrics,
                mood_ratings,
                burnout_analysis
            )

    def _prepare_data_summary(
        self,
        health_metrics: List[Dict[str, Any]],
        mood_ratings: List[Dict[str, Any]],
        burnout_analysis: Dict[str, Any]
    ) -> str:
        """Prepare concise data summary for GPT prompt"""
        summary = []

        # Burnout risk
        risk_score = burnout_analysis.get("overall_risk_score", 0)
        risk_level = burnout_analysis.get("risk_level", "unknown")
        summary.append(f"Burnout Risk: {risk_score:.1f}/100 ({risk_level})")

        # Recovery
        recovery_factor = burnout_analysis.get("risk_factors", {}).get("recovery", {})
        recovery_analysis = recovery_factor.get("analysis", {})
        if "average_recovery" in recovery_analysis:
            avg_recovery = recovery_analysis["average_recovery"]
            summary.append(f"Average Recovery: {avg_recovery}/100")

        # Mood
        mood_factor = burnout_analysis.get("risk_factors", {}).get("mood", {})
        mood_analysis = mood_factor.get("analysis", {})
        if "average_mood" in mood_analysis:
            avg_mood = mood_analysis["average_mood"]
            summary.append(f"Average Mood: {avg_mood}/10")

        # Sleep
        sleep_factor = burnout_analysis.get("risk_factors", {}).get("sleep", {})
        sleep_analysis = sleep_factor.get("analysis", {})
        if "average_duration_hours" in sleep_analysis:
            avg_sleep = sleep_analysis["average_duration_hours"]
            summary.append(f"Average Sleep: {avg_sleep} hours")

        # HRV
        hrv_factor = burnout_analysis.get("risk_factors", {}).get("hrv", {})
        hrv_analysis = hrv_factor.get("analysis", {})
        if "average_hrv" in hrv_analysis:
            avg_hrv = hrv_analysis["average_hrv"]
            summary.append(f"Average HRV: {avg_hrv} ms")

        # Strain balance
        strain_factor = burnout_analysis.get("risk_factors", {}).get("strain_balance", {})
        strain_analysis = strain_factor.get("analysis", {})
        if "average_strain" in strain_analysis:
            avg_strain = strain_analysis["average_strain"]
            summary.append(f"Average Strain: {avg_strain}/21")

        # Data period
        summary.append(f"Data points: {len(health_metrics)} days, {len(mood_ratings)} mood ratings")

        return "\n".join(summary)

    def _create_prompt(self, insight_type: str, data_summary: str) -> str:
        """Create GPT prompt based on insight type"""
        prompts = {
            "weekly_summary": f"""
Analyze this user's weekly health data and provide a brief summary with 3-5 actionable recommendations.

Data Summary:
{data_summary}

Format your response as:
1. A brief title (one line)
2. A 2-3 sentence summary of their overall health status
3. 3-5 specific, actionable recommendations

Keep the tone supportive and encouraging.
""",
            "burnout_alert": f"""
The user's burnout risk is elevated. Provide empathetic guidance and immediate actions they can take.

Data Summary:
{data_summary}

Format your response as:
1. A supportive title
2. A 2-3 sentence acknowledgment of their situation
3. 3-5 immediate, practical steps they can take today

Be empathetic and avoid being alarmist.
""",
            "trend_analysis": f"""
Analyze the user's health trends and provide insights into patterns and changes.

Data Summary:
{data_summary}

Format your response as:
1. A descriptive title about the trend
2. A 2-3 sentence analysis of what the data shows
3. 3-5 recommendations based on the trends

Focus on patterns, not individual data points.
""",
            "recovery_optimization": f"""
The user wants to improve their recovery. Provide targeted advice based on their data.

Data Summary:
{data_summary}

Format your response as:
1. A motivating title
2. A 2-3 sentence assessment of their current recovery
3. 3-5 specific strategies to improve recovery

Include both lifestyle and training adjustments.
"""
        }

        return prompts.get(insight_type, prompts["weekly_summary"])

    def _get_response_schema(self, insight_type: str) -> Dict[str, Any]:
        """Get JSON schema for structured output based on insight type"""

        if insight_type == "weekly_summary":
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": "weekly_summary_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "summary": {"type": "string"},
                            "key_metrics": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "value": {"type": "string"},
                                        "trend": {"type": "string", "enum": ["improving", "stable", "declining"]},
                                        "status": {"type": "string", "enum": ["good", "fair", "needs_attention"]}
                                    },
                                    "required": ["name", "value", "trend", "status"],
                                    "additionalProperties": False
                                }
                            },
                            "focus_areas": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "area": {"type": "string"},
                                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["area", "priority", "description"],
                                    "additionalProperties": False
                                }
                            },
                            "recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "category": {"type": "string"},
                                        "action": {"type": "string"},
                                        "impact": {"type": "string", "enum": ["high", "medium", "low"]}
                                    },
                                    "required": ["category", "action", "impact"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["title", "summary", "key_metrics", "focus_areas", "recommendations"],
                        "additionalProperties": False
                    }
                }
            }

        elif insight_type == "burnout_alert":
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": "burnout_alert_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "risk_level": {"type": "string", "enum": ["low", "moderate", "high", "critical"]},
                            "message": {"type": "string"},
                            "warning_signs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "sign": {"type": "string"},
                                        "severity": {"type": "string", "enum": ["high", "medium", "low"]}
                                    },
                                    "required": ["sign", "severity"],
                                    "additionalProperties": False
                                }
                            },
                            "immediate_actions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string"},
                                        "why": {"type": "string"},
                                        "timeframe": {"type": "string"}
                                    },
                                    "required": ["action", "why", "timeframe"],
                                    "additionalProperties": False
                                }
                            },
                            "support_resources": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["title", "risk_level", "message", "warning_signs", "immediate_actions", "support_resources"],
                        "additionalProperties": False
                    }
                }
            }

        elif insight_type == "trend_analysis":
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": "trend_analysis_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "overview": {"type": "string"},
                            "trends": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "metric": {"type": "string"},
                                        "direction": {"type": "string", "enum": ["increasing", "stable", "decreasing"]},
                                        "significance": {"type": "string", "enum": ["high", "medium", "low"]},
                                        "insight": {"type": "string"}
                                    },
                                    "required": ["metric", "direction", "significance", "insight"],
                                    "additionalProperties": False
                                }
                            },
                            "patterns": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "pattern": {"type": "string"},
                                        "observation": {"type": "string"}
                                    },
                                    "required": ["pattern", "observation"],
                                    "additionalProperties": False
                                }
                            },
                            "recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "based_on": {"type": "string"},
                                        "action": {"type": "string"}
                                    },
                                    "required": ["based_on", "action"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["title", "overview", "trends", "patterns", "recommendations"],
                        "additionalProperties": False
                    }
                }
            }

        # Default to weekly summary
        return self._get_response_schema("weekly_summary")

    def _format_structured_response(
        self,
        structured_data: Dict[str, Any],
        insight_type: str,
        model: str,
        tokens: int
    ) -> Dict[str, Any]:
        """Format structured data into our response format"""

        # Store the structured data for the frontend to use
        return {
            "title": structured_data.get("title", "Health Insight"),
            "content": structured_data.get("summary") or structured_data.get("message") or structured_data.get("overview", ""),
            "recommendations": self._extract_recommendations_from_structured(structured_data, insight_type),
            "structured_data": structured_data,  # Include full structured data
            "insight_type": insight_type,
            "model_used": model,
            "tokens_used": tokens
        }

    def _extract_recommendations_from_structured(
        self,
        structured_data: Dict[str, Any],
        insight_type: str
    ) -> List[str]:
        """Extract simple recommendation list from structured data for backward compatibility"""
        recommendations = []

        if insight_type == "weekly_summary":
            for rec in structured_data.get("recommendations", []):
                recommendations.append(rec.get("action", ""))
        elif insight_type == "burnout_alert":
            for action in structured_data.get("immediate_actions", []):
                recommendations.append(action.get("action", ""))
        elif insight_type == "trend_analysis":
            for rec in structured_data.get("recommendations", []):
                recommendations.append(rec.get("action", ""))

        return [r for r in recommendations if r]  # Filter empty strings

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendation items from content"""
        recommendations = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered lists
            if line.startswith(("- ", "• ", "* ")) or (len(line) > 0 and line[0].isdigit() and ". " in line):
                # Remove bullet/number prefix
                rec = line.lstrip("-•*0123456789. ").strip()
                if rec:
                    recommendations.append(rec)

        # If no clear recommendations found, return empty list
        if not recommendations:
            return []

        return recommendations[:5]  # Max 5 recommendations

    def _generate_fallback_insight(
        self,
        insight_type: str,
        health_metrics: List[Dict[str, Any]],
        mood_ratings: List[Dict[str, Any]],
        burnout_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic insight without OpenAI (fallback)"""
        from app.services.burnout_calculator import burnout_calculator

        risk_score = burnout_analysis.get("overall_risk_score", 50)
        risk_level = burnout_analysis.get("risk_level", "moderate")

        # Generate recommendations using calculator
        recommendations_list = burnout_calculator.get_recommendations(burnout_analysis)

        if insight_type == "weekly_summary":
            title = f"Weekly Health Summary - {risk_level.title()} Risk"
            content = f"""Based on your recent health data, your burnout risk is {risk_score:.1f}/100 ({risk_level}).

Over the past week, we've analyzed {len(health_metrics)} days of health metrics and {len(mood_ratings)} mood ratings.

Focus areas for this week:
{chr(10).join('• ' + rec for rec in recommendations_list[:5])}
"""
        elif insight_type == "burnout_alert":
            title = "Elevated Burnout Risk Detected"
            content = f"""Your current burnout risk is {risk_score:.1f}/100, which indicates {risk_level} risk.

This is based on patterns in your recovery, mood, sleep, and training data. It's important to take action now to prevent further decline.

Immediate steps:
{chr(10).join('• ' + rec for rec in recommendations_list[:5])}
"""
        else:
            title = "Health Trends Analysis"
            content = f"""Your overall health trend shows {risk_level} burnout risk at {risk_score:.1f}/100.

Key insights from your data:
{chr(10).join('• ' + rec for rec in recommendations_list[:5])}
"""

        return {
            "title": title,
            "content": content,
            "recommendations": recommendations_list[:5],
            "model_used": "fallback",
            "tokens_used": 0
        }


# Singleton instance
ai_insights_service = AIInsightsService()