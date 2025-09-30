"""
Burnout Risk Calculator
Calculates burnout risk scores based on health metrics and mood data
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from statistics import mean, stdev
import math


class BurnoutCalculator:
    """Calculate burnout risk from health and mood data"""

    # Weight factors for different metrics
    WEIGHTS = {
        "recovery": 0.25,      # Recovery scores
        "mood": 0.30,          # Mood ratings (highest weight)
        "hrv": 0.15,           # Heart rate variability
        "sleep": 0.15,         # Sleep quality
        "strain_balance": 0.15  # Strain vs recovery balance
    }

    # Thresholds for risk levels
    RISK_LEVELS = {
        "low": (0, 30),
        "moderate": (30, 60),
        "high": (60, 80),
        "critical": (80, 100)
    }

    @staticmethod
    def calculate_recovery_risk(health_metrics: List[Dict[str, Any]]) -> tuple[float, Dict[str, Any]]:
        """
        Calculate risk from recovery scores
        Low recovery = high risk

        Args:
            health_metrics: List of health metric records

        Returns:
            Tuple of (risk_score_0_100, analysis_details)
        """
        recovery_scores = [
            m["recovery_score"]
            for m in health_metrics
            if m.get("recovery_score") is not None
        ]

        if not recovery_scores:
            return 50.0, {"reason": "no_data", "count": 0}

        avg_recovery = mean(recovery_scores)
        trend = "declining" if len(recovery_scores) > 3 and recovery_scores[-1] < recovery_scores[0] else "stable"

        # Convert recovery (0-100, higher is better) to risk (0-100, higher is worse)
        risk = 100 - avg_recovery

        # Adjust for declining trend
        if trend == "declining":
            risk = min(100, risk * 1.2)

        return risk, {
            "average_recovery": round(avg_recovery, 1),
            "trend": trend,
            "data_points": len(recovery_scores),
            "recent_recovery": recovery_scores[-1] if recovery_scores else None
        }

    @staticmethod
    def calculate_mood_risk(mood_ratings: List[Dict[str, Any]]) -> tuple[float, Dict[str, Any]]:
        """
        Calculate risk from mood ratings
        Low mood = high risk

        Args:
            mood_ratings: List of mood rating records

        Returns:
            Tuple of (risk_score_0_100, analysis_details)
        """
        if not mood_ratings:
            return 50.0, {"reason": "no_data", "count": 0}

        ratings = [m["rating"] for m in mood_ratings]
        avg_mood = mean(ratings)

        # Calculate variance (unstable mood = higher risk)
        variance = stdev(ratings) if len(ratings) > 1 else 0

        # Count low mood days (rating <= 4)
        low_mood_days = sum(1 for r in ratings if r <= 4)
        low_mood_ratio = low_mood_days / len(ratings)

        # Convert mood (1-10, higher is better) to risk (0-100, higher is worse)
        # Normalize from 1-10 scale to 0-100 scale
        base_risk = ((10 - avg_mood) / 9) * 100

        # Adjust for variance (volatile mood increases risk)
        variance_penalty = min(20, variance * 5)
        base_risk = min(100, base_risk + variance_penalty)

        # Adjust for low mood frequency
        if low_mood_ratio > 0.5:  # More than half are low mood
            base_risk = min(100, base_risk * 1.3)

        return base_risk, {
            "average_mood": round(avg_mood, 1),
            "variance": round(variance, 2),
            "low_mood_days": low_mood_days,
            "low_mood_ratio": round(low_mood_ratio, 2),
            "data_points": len(ratings)
        }

    @staticmethod
    def calculate_hrv_risk(health_metrics: List[Dict[str, Any]]) -> tuple[float, Dict[str, Any]]:
        """
        Calculate risk from HRV (heart rate variability)
        Low HRV = high stress = high risk

        Args:
            health_metrics: List of health metric records

        Returns:
            Tuple of (risk_score_0_100, analysis_details)
        """
        hrv_values = [
            m["hrv"]
            for m in health_metrics
            if m.get("hrv") is not None
        ]

        if not hrv_values:
            return 50.0, {"reason": "no_data", "count": 0}

        avg_hrv = mean(hrv_values)

        # HRV baseline varies by person, but general guidelines:
        # Excellent: 70+, Good: 50-70, Fair: 30-50, Poor: <30
        if avg_hrv >= 70:
            risk = 10  # Very low risk
        elif avg_hrv >= 50:
            risk = 30  # Low risk
        elif avg_hrv >= 30:
            risk = 60  # Moderate risk
        else:
            risk = 85  # High risk

        # Check for declining trend
        if len(hrv_values) > 3:
            recent_avg = mean(hrv_values[-3:])
            earlier_avg = mean(hrv_values[:3])
            if recent_avg < earlier_avg * 0.9:  # >10% decline
                risk = min(100, risk * 1.2)

        return risk, {
            "average_hrv": round(avg_hrv, 1),
            "trend": "declining" if len(hrv_values) > 3 and hrv_values[-1] < hrv_values[0] else "stable",
            "data_points": len(hrv_values)
        }

    @staticmethod
    def calculate_sleep_risk(health_metrics: List[Dict[str, Any]]) -> tuple[float, Dict[str, Any]]:
        """
        Calculate risk from sleep quality and duration
        Poor sleep = high risk

        Args:
            health_metrics: List of health metric records

        Returns:
            Tuple of (risk_score_0_100, analysis_details)
        """
        sleep_scores = [
            m["sleep_quality_score"]
            for m in health_metrics
            if m.get("sleep_quality_score") is not None
        ]

        sleep_durations = [
            m["sleep_duration_minutes"]
            for m in health_metrics
            if m.get("sleep_duration_minutes") is not None
        ]

        if not sleep_scores and not sleep_durations:
            return 50.0, {"reason": "no_data", "count": 0}

        risk = 50.0
        analysis = {}

        # Factor 1: Sleep quality
        if sleep_scores:
            avg_quality = mean(sleep_scores)
            quality_risk = 100 - avg_quality
            risk = quality_risk
            analysis["average_quality"] = round(avg_quality, 1)

        # Factor 2: Sleep duration
        if sleep_durations:
            avg_duration_hours = mean(sleep_durations) / 60

            # Optimal sleep: 7-9 hours
            if 7 <= avg_duration_hours <= 9:
                duration_risk = 20
            elif 6 <= avg_duration_hours < 7 or 9 < avg_duration_hours <= 10:
                duration_risk = 40
            else:
                duration_risk = 70

            # Combine quality and duration risk
            if sleep_scores:
                risk = (risk + duration_risk) / 2
            else:
                risk = duration_risk

            analysis["average_duration_hours"] = round(avg_duration_hours, 1)

        # Count insufficient sleep days (<6 hours)
        insufficient_days = sum(1 for d in sleep_durations if d < 360)
        if insufficient_days > len(sleep_durations) * 0.3:  # >30% are insufficient
            risk = min(100, risk * 1.2)

        analysis.update({
            "insufficient_sleep_days": insufficient_days,
            "data_points": max(len(sleep_scores), len(sleep_durations))
        })

        return risk, analysis

    @staticmethod
    def calculate_strain_balance_risk(health_metrics: List[Dict[str, Any]]) -> tuple[float, Dict[str, Any]]:
        """
        Calculate risk from strain vs recovery balance
        High strain + low recovery = high risk

        Args:
            health_metrics: List of health metric records

        Returns:
            Tuple of (risk_score_0_100, analysis_details)
        """
        # Get records with both strain and recovery
        paired_data = [
            (m["day_strain"], m["recovery_score"])
            for m in health_metrics
            if m.get("day_strain") is not None and m.get("recovery_score") is not None
        ]

        if not paired_data:
            return 50.0, {"reason": "no_data", "count": 0}

        strains, recoveries = zip(*paired_data)
        avg_strain = mean(strains)
        avg_recovery = mean(recoveries)

        # Calculate strain/recovery ratio
        # Ideal: High recovery supports high strain
        # Risk: High strain with low recovery

        # Normalize strain (0-21 scale) and recovery (0-100 scale)
        normalized_strain = (avg_strain / 21) * 100

        # Risk increases when strain is high and recovery is low
        imbalance = normalized_strain - avg_recovery

        if imbalance > 30:  # Strain much higher than recovery
            risk = 80
        elif imbalance > 15:
            risk = 60
        elif imbalance > 0:
            risk = 40
        else:  # Recovery >= Strain (good balance)
            risk = 20

        # Count days with high strain (>15) and low recovery (<50)
        high_risk_days = sum(
            1 for s, r in paired_data
            if s > 15 and r < 50
        )

        return risk, {
            "average_strain": round(avg_strain, 1),
            "average_recovery": round(avg_recovery, 1),
            "imbalance": round(imbalance, 1),
            "high_risk_days": high_risk_days,
            "data_points": len(paired_data)
        }

    @classmethod
    def calculate_overall_risk(
        cls,
        health_metrics: List[Dict[str, Any]],
        mood_ratings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate overall burnout risk score

        Args:
            health_metrics: List of health metric records (last 7-30 days)
            mood_ratings: List of mood rating records

        Returns:
            Dictionary with overall risk score and detailed breakdown
        """
        # Calculate component risks
        recovery_risk, recovery_analysis = cls.calculate_recovery_risk(health_metrics)
        mood_risk, mood_analysis = cls.calculate_mood_risk(mood_ratings)
        hrv_risk, hrv_analysis = cls.calculate_hrv_risk(health_metrics)
        sleep_risk, sleep_analysis = cls.calculate_sleep_risk(health_metrics)
        strain_risk, strain_analysis = cls.calculate_strain_balance_risk(health_metrics)

        # Calculate weighted overall score
        overall_risk = (
            recovery_risk * cls.WEIGHTS["recovery"] +
            mood_risk * cls.WEIGHTS["mood"] +
            hrv_risk * cls.WEIGHTS["hrv"] +
            sleep_risk * cls.WEIGHTS["sleep"] +
            strain_risk * cls.WEIGHTS["strain_balance"]
        )

        # Determine risk level
        risk_level = "low"
        for level, (min_val, max_val) in cls.RISK_LEVELS.items():
            if min_val <= overall_risk < max_val:
                risk_level = level
                break

        # Calculate confidence score (based on data availability)
        data_points = sum([
            recovery_analysis.get("data_points", 0),
            mood_analysis.get("data_points", 0),
            hrv_analysis.get("data_points", 0),
            sleep_analysis.get("data_points", 0),
            strain_analysis.get("data_points", 0)
        ])

        # Confidence increases with more data (max at 30+ total points)
        confidence = min(100, (data_points / 30) * 100)

        return {
            "overall_risk_score": round(overall_risk, 1),
            "risk_level": risk_level,
            "confidence_score": round(confidence, 1),
            "data_points_used": data_points,
            "risk_factors": {
                "recovery": {
                    "risk_score": round(recovery_risk, 1),
                    "weight": cls.WEIGHTS["recovery"],
                    "analysis": recovery_analysis
                },
                "mood": {
                    "risk_score": round(mood_risk, 1),
                    "weight": cls.WEIGHTS["mood"],
                    "analysis": mood_analysis
                },
                "hrv": {
                    "risk_score": round(hrv_risk, 1),
                    "weight": cls.WEIGHTS["hrv"],
                    "analysis": hrv_analysis
                },
                "sleep": {
                    "risk_score": round(sleep_risk, 1),
                    "weight": cls.WEIGHTS["sleep"],
                    "analysis": sleep_analysis
                },
                "strain_balance": {
                    "risk_score": round(strain_risk, 1),
                    "weight": cls.WEIGHTS["strain_balance"],
                    "analysis": strain_analysis
                }
            }
        }

    @staticmethod
    def get_recommendations(risk_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on risk analysis

        Args:
            risk_analysis: Output from calculate_overall_risk()

        Returns:
            List of recommendation strings
        """
        recommendations = []
        risk_factors = risk_analysis["risk_factors"]

        # Recovery recommendations
        if risk_factors["recovery"]["risk_score"] > 60:
            recommendations.append("📉 Your recovery scores are low. Consider reducing training intensity and prioritizing rest.")

        # Mood recommendations
        if risk_factors["mood"]["risk_score"] > 60:
            recommendations.append("😔 Your mood has been low recently. Consider stress management techniques or talking to someone.")

        mood_variance = risk_factors["mood"]["analysis"].get("variance", 0)
        if mood_variance > 2:
            recommendations.append("📊 Your mood is fluctuating significantly. Try to identify and address sources of stress.")

        # HRV recommendations
        if risk_factors["hrv"]["risk_score"] > 60:
            recommendations.append("❤️ Your HRV is low, indicating high stress. Try meditation, breathing exercises, or gentle yoga.")

        # Sleep recommendations
        sleep_analysis = risk_factors["sleep"]["analysis"]
        avg_duration = sleep_analysis.get("average_duration_hours", 7)
        if avg_duration < 7:
            recommendations.append("😴 You're not getting enough sleep. Aim for 7-9 hours per night.")
        elif avg_duration > 9:
            recommendations.append("⏰ You're sleeping more than usual. This could indicate overtraining or other health issues.")

        if risk_factors["sleep"]["risk_score"] > 60:
            recommendations.append("🛏️ Your sleep quality is poor. Improve sleep hygiene: dark room, cool temperature, no screens before bed.")

        # Strain balance recommendations
        if risk_factors["strain_balance"]["risk_score"] > 60:
            recommendations.append("⚖️ Your training strain is exceeding your recovery capacity. Take a rest day or reduce intensity.")

        # Overall recommendations
        if risk_analysis["overall_risk_score"] > 70:
            recommendations.append("🚨 High burnout risk detected. Consider taking time off and consulting a healthcare professional.")
        elif risk_analysis["overall_risk_score"] > 50:
            recommendations.append("⚠️ Moderate burnout risk. Focus on recovery, sleep, and stress management this week.")

        # Add positive feedback if low risk
        if risk_analysis["overall_risk_score"] < 30:
            recommendations.append("✅ Great job! Your health metrics look excellent. Keep up the balanced routine.")

        return recommendations


# Singleton instance
burnout_calculator = BurnoutCalculator()