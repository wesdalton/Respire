"""
Data Transformation Service
Transform WHOOP API v2 data into internal HealthMetric format
"""
from datetime import date, datetime
from typing import Dict, List, Any, Optional
from uuid import UUID


class WHOOPDataTransformer:
    """Transform WHOOP API data to HealthMetric models"""

    @staticmethod
    def extract_recovery_data(recovery: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract recovery metrics from WHOOP recovery response

        Args:
            recovery: WHOOP recovery response

        Returns:
            Dictionary with recovery metrics
        """
        score_state = recovery.get("score_state")
        score = recovery.get("score", {})

        # Only extract if score is present and state is SCORED
        if score_state == "SCORED" and score:
            return {
                "recovery_score": score.get("recovery_score"),
                "resting_hr": score.get("resting_heart_rate"),
                "hrv": score.get("hrv_rmssd_milli"),
            }

        return {
            "recovery_score": None,
            "resting_hr": None,
            "hrv": None,
        }

    @staticmethod
    def extract_sleep_data(sleep: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sleep metrics from WHOOP sleep response

        Args:
            sleep: WHOOP sleep response

        Returns:
            Dictionary with sleep metrics
        """
        score = sleep.get("score", {})

        # Calculate duration from start and end timestamps
        start = sleep.get("start")
        end = sleep.get("end")
        duration_minutes = None

        if start and end:
            try:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                duration_seconds = (end_dt - start_dt).total_seconds()
                duration_minutes = int(duration_seconds / 60)
            except Exception:
                pass

        # Get sleep performance from score
        sleep_performance = score.get("sleep_performance_percentage") if score else None

        return {
            "sleep_duration_minutes": duration_minutes,
            "sleep_quality_score": sleep_performance,
            "sleep_latency_minutes": None,  # Not directly available in v2
            "time_in_bed_minutes": duration_minutes,  # Use same as duration for now
            "sleep_consistency_score": score.get("sleep_consistency_percentage") if score else None,
        }

    @staticmethod
    def extract_strain_data(cycle: Dict[str, Any], workouts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract strain metrics from WHOOP cycle and workouts

        Args:
            cycle: WHOOP cycle response
            workouts: List of workout responses for this day

        Returns:
            Dictionary with strain metrics
        """
        score = cycle.get("score", {})

        # Count workouts for this cycle
        workout_count = len(workouts)

        strain = score.get("strain") if score else None
        avg_hr = score.get("average_heart_rate") if score else None
        max_hr = score.get("max_heart_rate") if score else None

        return {
            "day_strain": strain,
            "workout_count": workout_count,
            "average_hr": avg_hr,
            "max_hr": max_hr,
        }

    @staticmethod
    def merge_daily_data(
        user_id: UUID,
        date_val: date,
        recovery: Optional[Dict[str, Any]] = None,
        sleep: Optional[Dict[str, Any]] = None,
        cycle: Optional[Dict[str, Any]] = None,
        workouts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Merge all WHOOP data for a specific date into HealthMetric format

        Args:
            user_id: User UUID
            date_val: Date for this data
            recovery: WHOOP recovery data
            sleep: WHOOP sleep data
            cycle: WHOOP cycle data
            workouts: List of workouts for this day

        Returns:
            Dictionary ready for HealthMetric creation
        """
        health_metric = {
            "user_id": user_id,
            "date": date_val,
            "raw_data": {
                "recovery": recovery,
                "sleep": sleep,
                "cycle": cycle,
                "workouts": workouts or []
            }
        }

        # Extract and merge recovery data
        if recovery:
            recovery_metrics = WHOOPDataTransformer.extract_recovery_data(recovery)
            health_metric.update(recovery_metrics)

        # Extract and merge sleep data
        if sleep:
            sleep_metrics = WHOOPDataTransformer.extract_sleep_data(sleep)
            health_metric.update(sleep_metrics)

        # Extract and merge strain data
        if cycle:
            strain_metrics = WHOOPDataTransformer.extract_strain_data(
                cycle,
                workouts or []
            )
            health_metric.update(strain_metrics)

        return health_metric

    @staticmethod
    def group_by_date(
        cycles: List[Dict[str, Any]],
        recovery: List[Dict[str, Any]],
        sleep: List[Dict[str, Any]],
        workouts: List[Dict[str, Any]]
    ) -> Dict[date, Dict[str, Any]]:
        """
        Group WHOOP data by date

        Args:
            cycles: List of cycle responses
            recovery: List of recovery responses
            sleep: List of sleep responses
            workouts: List of workout responses

        Returns:
            Dictionary mapping date to grouped data
        """
        grouped: Dict[date, Dict[str, Any]] = {}

        # Group cycles by date
        for cycle_data in cycles:
            if not cycle_data.get("start"):
                continue

            cycle_date = datetime.fromisoformat(
                cycle_data["start"].replace("Z", "+00:00")
            ).date()

            if cycle_date not in grouped:
                grouped[cycle_date] = {}
            grouped[cycle_date]["cycle"] = cycle_data

        # Group recovery by date (use cycle's date)
        for recovery_data in recovery:
            cycle_id = recovery_data.get("cycle_id")
            if not cycle_id:
                continue

            # Find matching cycle to get date
            matching_cycle = next(
                (c for c in cycles if c.get("id") == cycle_id),
                None
            )
            if matching_cycle:
                cycle_date = datetime.fromisoformat(
                    matching_cycle["start"].replace("Z", "+00:00")
                ).date()

                if cycle_date not in grouped:
                    grouped[cycle_date] = {}
                grouped[cycle_date]["recovery"] = recovery_data

        # Group sleep by date
        for sleep_data in sleep:
            if not sleep_data.get("end"):
                continue

            # Use end date for sleep (when you woke up)
            sleep_date = datetime.fromisoformat(
                sleep_data["end"].replace("Z", "+00:00")
            ).date()

            if sleep_date not in grouped:
                grouped[sleep_date] = {}

            # Keep main sleep (not naps)
            if not sleep_data.get("nap", False):
                grouped[sleep_date]["sleep"] = sleep_data

        # Group workouts by date
        for workout_data in workouts:
            if not workout_data.get("start"):
                continue

            workout_date = datetime.fromisoformat(
                workout_data["start"].replace("Z", "+00:00")
            ).date()

            if workout_date not in grouped:
                grouped[workout_date] = {}
            if "workouts" not in grouped[workout_date]:
                grouped[workout_date]["workouts"] = []
            grouped[workout_date]["workouts"].append(workout_data)

        return grouped

    @staticmethod
    def transform_sync_data(
        user_id: UUID,
        whoop_data: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Transform complete WHOOP sync data into list of HealthMetrics

        Args:
            user_id: User UUID
            whoop_data: Dictionary with cycles, recovery, sleep, workouts lists

        Returns:
            List of HealthMetric dictionaries ready for database insertion
        """
        # Group all data by date
        grouped_data = WHOOPDataTransformer.group_by_date(
            cycles=whoop_data.get("cycles", []),
            recovery=whoop_data.get("recovery", []),
            sleep=whoop_data.get("sleep", []),
            workouts=whoop_data.get("workouts", [])
        )

        # Create HealthMetric for each date
        health_metrics = []
        for date_val, day_data in grouped_data.items():
            health_metric = WHOOPDataTransformer.merge_daily_data(
                user_id=user_id,
                date_val=date_val,
                recovery=day_data.get("recovery"),
                sleep=day_data.get("sleep"),
                cycle=day_data.get("cycle"),
                workouts=day_data.get("workouts")
            )
            health_metrics.append(health_metric)

        return health_metrics


class OuraDataTransformer:
    """Transform Oura API data to HealthMetric models"""

    @staticmethod
    def transform_to_health_metrics(
        daily_sleep: List[Dict[str, Any]],
        daily_activity: List[Dict[str, Any]],
        daily_readiness: List[Dict[str, Any]],
        heart_rate_data: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Transform Oura data into HealthMetric format

        Args:
            daily_sleep: Daily sleep summaries
            daily_activity: Daily activity summaries
            daily_readiness: Daily readiness scores
            heart_rate_data: Heart rate time series (optional)

        Returns:
            List of health metric dictionaries
        """
        # Index data by date for efficient lookup
        sleep_by_date = {s["day"]: s for s in daily_sleep if s.get("day")}
        activity_by_date = {a["day"]: a for a in daily_activity if a.get("day")}
        readiness_by_date = {r["day"]: r for r in daily_readiness if r.get("day")}

        # Get all unique dates
        all_dates = set(sleep_by_date.keys()) | set(activity_by_date.keys()) | set(readiness_by_date.keys())

        health_metrics = []

        for date_str in sorted(all_dates):
            daily_sleep_data = sleep_by_date.get(date_str, {})
            daily_activity_data = activity_by_date.get(date_str, {})
            daily_readiness_data = readiness_by_date.get(date_str, {})

            health_metric = {
                "date": datetime.fromisoformat(date_str).date(),
            }

            # Sleep metrics
            if daily_sleep_data:
                contributors = daily_sleep_data.get("contributors", {})

                # Sleep duration (in seconds, convert to minutes)
                total_sleep = daily_sleep_data.get("total_sleep_duration")
                if total_sleep:
                    health_metric["sleep_duration_minutes"] = int(total_sleep / 60)

                # Sleep quality score (0-100)
                sleep_score = daily_sleep_data.get("score")
                if sleep_score:
                    health_metric["sleep_quality_score"] = sleep_score

                # Sleep latency (in seconds, convert to minutes)
                latency = contributors.get("latency")
                if latency:
                    health_metric["sleep_latency_minutes"] = int(latency / 60)

                # Time in bed (in seconds, convert to minutes)
                time_in_bed = daily_sleep_data.get("time_in_bed")
                if time_in_bed:
                    health_metric["time_in_bed_minutes"] = int(time_in_bed / 60)

                # Resting heart rate - use lowest heart rate as proxy
                lowest_hr = daily_sleep_data.get("lowest_heart_rate")
                if lowest_hr:
                    health_metric["resting_hr"] = lowest_hr

            # Activity metrics
            if daily_activity_data:
                # Day Strain - Direct mapping of activity score (0-100)
                activity_score = daily_activity_data.get("score")
                if activity_score:
                    health_metric["day_strain"] = float(activity_score)

                # Average heart rate
                avg_hr = daily_activity_data.get("average_heart_rate")
                if avg_hr:
                    health_metric["average_hr"] = avg_hr

                # Max heart rate
                max_hr = daily_activity_data.get("max_heart_rate")
                if max_hr:
                    health_metric["max_hr"] = max_hr

            # Readiness metrics
            if daily_readiness_data:
                # Recovery score from readiness
                readiness_score = daily_readiness_data.get("score")
                if readiness_score:
                    health_metric["recovery_score"] = readiness_score

                # HRV from readiness contributors
                contributors = daily_readiness_data.get("contributors", {})
                hrv_balance = contributors.get("hrv_balance")
                if hrv_balance:
                    # HRV balance is a score, not actual HRV
                    # Try to get actual HRV from temperature data or use balance as proxy
                    health_metric["hrv"] = float(hrv_balance)

            # Store raw data for reference
            health_metric["raw_data"] = {
                "sleep": daily_sleep_data,
                "activity": daily_activity_data,
                "readiness": daily_readiness_data
            }

            health_metrics.append(health_metric)

        return health_metrics


# Singleton instances
whoop_transformer = WHOOPDataTransformer()
oura_transformer = OuraDataTransformer()