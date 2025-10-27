"""
Data Transformation Service
Transform WHOOP API v2 data into internal HealthMetric format
"""
from datetime import date, datetime, timedelta
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

        # Group recovery by date (use sleep end date - when you wake up)
        for recovery_data in recovery:
            sleep_id = recovery_data.get("sleep_id")
            if not sleep_id:
                continue

            # Find matching sleep to get wake-up date
            matching_sleep = next(
                (s for s in sleep if s.get("id") == sleep_id),
                None
            )
            if matching_sleep and matching_sleep.get("end"):
                # Parse end time and apply timezone offset
                end_time_str = matching_sleep["end"]
                timezone_offset = matching_sleep.get("timezone_offset", "+00:00")

                # WHOOP times are in UTC, apply timezone_offset to get local date
                end_dt_utc = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))

                # Parse timezone offset (e.g., "-05:00" -> timedelta)
                sign = 1 if timezone_offset[0] == '+' else -1
                hours, minutes = map(int, timezone_offset[1:].split(':'))
                tz_offset = timedelta(hours=sign * hours, minutes=sign * minutes)

                # Apply offset to get local time, then extract date
                local_dt = end_dt_utc + tz_offset
                recovery_date = local_dt.date()

                # Debug logging
                print(f"DEBUG Recovery: sleep_id={sleep_id}, end_utc={end_time_str}, tz_offset={timezone_offset}, local_date={recovery_date}")

                if recovery_date not in grouped:
                    grouped[recovery_date] = {}
                grouped[recovery_date]["recovery"] = recovery_data

        # Group sleep by date
        for sleep_data in sleep:
            if not sleep_data.get("end"):
                continue

            # Parse end time and apply timezone offset
            end_time_str = sleep_data["end"]
            timezone_offset = sleep_data.get("timezone_offset", "+00:00")

            # WHOOP times are in UTC, but we need to apply timezone_offset to get local date
            # timezone_offset format: "-05:00" or "+00:00"
            end_dt_utc = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))

            # Parse timezone offset (e.g., "-05:00" -> timedelta)
            sign = 1 if timezone_offset[0] == '+' else -1
            hours, minutes = map(int, timezone_offset[1:].split(':'))
            tz_offset = timedelta(hours=sign * hours, minutes=sign * minutes)

            # Apply offset to get local time, then extract date
            local_dt = end_dt_utc + tz_offset
            sleep_date = local_dt.date()

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


# Singleton instance
whoop_transformer = WHOOPDataTransformer()