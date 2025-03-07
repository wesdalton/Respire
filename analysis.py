import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import json
import logging
from datetime import datetime, timedelta, date

# Set up logger
logger = logging.getLogger(__name__)

def compute_correlation(records=None):
    """
    Compute the Pearson correlation coefficient between recovery score and mood rating.
    
    Args:
        records: Optional list of dictionary records from Supabase
    
    Returns:
        tuple: (correlation, p-value) or (None, None) if insufficient data
    """
    # This function should now be called with data from app.py
    # The function signature is maintained for backward compatibility
    
    if not records:
        logger.warning("No records provided for correlation calculation")
        return None, None
    
    try:
        # Filter records with both recovery_score and mood_rating
        data = [{
            "recovery_score": r.get('recovery_score'),
            "mood_rating": r.get('mood_rating')
        } for r in records if r.get('mood_rating') is not None and r.get('recovery_score') is not None]
        
        df = pd.DataFrame(data)
        
        if len(df) > 1:
            corr, p_value = pearsonr(df["recovery_score"], df["mood_rating"])
            return corr, p_value
    except Exception as e:
        logger.error(f"Error computing correlation: {str(e)}")
    
    return None, None

def calculate_time_exponential_weights(days_back, decay_factor=0.8):
    """
    Calculate exponentially decaying weights for time series analysis.
    More recent days have higher weight with exponential decay.
    
    Args:
        days_back: Number of days to look back
        decay_factor: Controls decay rate (0.8 means 20% decay per day)
    
    Returns:
        List of weights summing to 1.0
    """
    # Generate raw weights with exponential decay
    raw_weights = [decay_factor ** i for i in range(days_back)]
    # Reverse so most recent day has highest weight
    raw_weights.reverse()
    # Normalize to sum to 1.0
    sum_weights = sum(raw_weights)
    return [w / sum_weights for w in raw_weights]

def calculate_missing_data_weights(metrics_list):
    """
    Adjust weights based on data completeness.
    Days with more complete data get higher relative weight.
    
    Args:
        metrics_list: List of dict objects (from Supabase) or DailyMetrics objects
        
    Returns:
        List of completeness weights from 0.0-1.0
    """
    completeness_weights = []
    
    for metrics in metrics_list:
        if metrics is None:
            completeness_weights.append(0.0)
            continue
            
        # Count available key metrics
        available_count = 0
        total_count = 4  # recovery, mood, hrv, strain
        
        # Support both dict objects and SQLAlchemy model objects
        if isinstance(metrics, dict):
            if metrics.get('recovery_score') is not None:
                available_count += 1
            if metrics.get('mood_rating') is not None:
                available_count += 1
            if metrics.get('hrv') is not None:
                available_count += 1
            if metrics.get('strain') is not None:
                available_count += 1
        else:
            # Assume it's a SQLAlchemy model or similar object
            if hasattr(metrics, 'recovery_score') and metrics.recovery_score is not None:
                available_count += 1
            if hasattr(metrics, 'mood_rating') and metrics.mood_rating is not None:
                available_count += 1
            if hasattr(metrics, 'hrv') and metrics.hrv is not None:
                available_count += 1
            if hasattr(metrics, 'strain') and metrics.strain is not None:
                available_count += 1
            
        # Calculate completeness ratio
        completeness = available_count / total_count
        completeness_weights.append(completeness)
    
    # Normalize to ensure weights sum to available days (not 1.0)
    # This preserves the information about missing days
    return completeness_weights

def get_prior_metrics(metrics, all_records=None, days_back=7):
    """
    Retrieve metrics from previous days for temporal analysis.
    
    Args:
        metrics: Current day's metrics dictionary
        all_records: List of all available metrics records (dictionaries)
        days_back: Number of days to look back
        
    Returns:
        List of metrics dictionaries for previous days
    """
    if not metrics or 'date' not in metrics:
        return []
    
    # Parse the current date
    try:
        if isinstance(metrics['date'], str):
            current_date = datetime.strptime(metrics['date'], "%Y-%m-%d").date()
        elif isinstance(metrics['date'], date):
            current_date = metrics['date']
        else:
            logger.error(f"Invalid date format: {metrics['date']}")
            return []
    except Exception as e:
        logger.error(f"Error parsing date: {str(e)}")
        return []
    
    # If no records provided, we can't find prior metrics
    if not all_records:
        logger.warning("No records provided to find prior metrics")
        return []
    
    # Create date-indexed dictionary of all records for fast lookup
    date_indexed_records = {}
    for record in all_records:
        if 'date' in record:
            try:
                if isinstance(record['date'], str):
                    record_date = datetime.strptime(record['date'], "%Y-%m-%d").date()
                elif isinstance(record['date'], date):
                    record_date = record['date']
                else:
                    continue
                
                date_indexed_records[record_date] = record
            except Exception as e:
                logger.debug(f"Skipping record with invalid date: {str(e)}")
    
    prior_metrics = []
    for i in range(1, days_back + 1):
        prior_date = current_date - timedelta(days=i)
        # Look up the record for this date
        prior_day = date_indexed_records.get(prior_date)
        prior_metrics.append(prior_day)  # Will be None if day doesn't exist
    
    return prior_metrics

def compute_sleep_quality_score(metrics):
    """
    Compute a comprehensive sleep quality score from multiple sleep metrics.
    
    Args:
        metrics: Dictionary of metrics from Supabase
        
    Returns:
        Sleep quality score from 0-100
    """
    if not metrics:
        return None
        
    scores = []
    weights = []
    
    # Basic sleep quality (if available)
    if metrics.get('sleep_quality') is not None:
        scores.append(metrics.get('sleep_quality'))
        weights.append(0.4)
    
    # Sleep efficiency
    if metrics.get('sleep_efficiency') is not None:
        scores.append(metrics.get('sleep_efficiency'))
        weights.append(0.3)
    
    # Sleep consistency
    if metrics.get('sleep_consistency') is not None:
        scores.append(metrics.get('sleep_consistency'))
        weights.append(0.3)
    
    # Sleep stages (normalize deep and REM sleep)
    if metrics.get('total_sleep_time') is not None and metrics.get('total_sleep_time') > 0:
        # Calculate percentage of deep sleep (ideal: 15-25%)
        if metrics.get('deep_sleep_time') is not None:
            deep_pct = (metrics.get('deep_sleep_time') / metrics.get('total_sleep_time')) * 100
            # Optimal deep sleep around 20%
            deep_score = 100 - min(100, abs(deep_pct - 20) * 5)
            scores.append(deep_score)
            weights.append(0.1)
            
        # Calculate percentage of REM sleep (ideal: 20-25%)
        if metrics.get('rem_sleep_time') is not None:
            rem_pct = (metrics.get('rem_sleep_time') / metrics.get('total_sleep_time')) * 100
            # Optimal REM sleep around 23%
            rem_score = 100 - min(100, abs(rem_pct - 23) * 5)
            scores.append(rem_score)
            weights.append(0.1)
    
    # Calculate weighted average
    if scores and weights:
        total_weight = sum(weights)
        if total_weight > 0:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            return max(0, min(100, weighted_score))
    
    # Fallback to base sleep quality
    return metrics.get('sleep_quality')

def get_burnout_risk_score(metrics, all_records=None):
    """
    Advanced burnout risk prediction model that incorporates:
    1. Comprehensive physiological metrics (WHOOP data)
    2. Subjective well-being assessment (mood)
    3. Temporal analysis (trends over time)
    4. Sleep quality assessment
    5. Strain-to-recovery balance
    
    This model is based on research into physiological markers of burnout,
    including HRV depression, sleep disruption, and subjective mood changes.
    
    Args:
        metrics: Current day's metrics dictionary containing WHOOP data
        all_records: List of all metrics records for temporal analysis
    
    Returns:
        float: Burnout risk score (0-100, higher means higher risk)
    """
    # Make sure we have valid metrics with recovery score
    if not metrics or metrics.get('recovery_score') is None:
        logger.warning("Cannot calculate burnout risk: missing recovery score")
        return None
    
    try:
        # Get metrics from previous days for temporal analysis
        prior_metrics = get_prior_metrics(metrics, all_records, days_back=7)
        all_metrics = [metrics] + prior_metrics
        
        # Calculate time weights - exponential decay
        time_weights = calculate_time_exponential_weights(len(all_metrics))
        
        # Calculate completeness weights
        completeness_weights = calculate_missing_data_weights(all_metrics)
        
        # Combine weights (multiply time by completeness)
        combined_weights = [t * c for t, c in zip(time_weights, completeness_weights)]
        
        # Normalize to sum to 1.0
        weight_sum = sum(combined_weights)
        if weight_sum > 0:
            normalized_weights = [w / weight_sum for w in combined_weights]
        else:
            # Fallback to just using current day
            normalized_weights = [1.0] + [0.0] * len(prior_metrics)
        
        # Component 1: Recovery Trend (25%)
        # Lower recovery scores increase burnout risk
        recovery_risk_values = []
        
        for i, m in enumerate(all_metrics):
            if m and m.get('recovery_score') is not None:
                # Invert recovery score (100 - recovery)
                recovery_risk = 100 - m.get('recovery_score')
                recovery_risk_values.append((recovery_risk, normalized_weights[i]))
        
        if recovery_risk_values:
            recovery_risk_score = sum(r * w for r, w in recovery_risk_values)
        else:
            recovery_risk_score = 50  # Neutral value
        
        # Component 2: HRV Analysis (15%)
        # Chronically depressed HRV is a key burnout marker
        hrv_risk_values = []
        hrv_trend = 0
        
        for i, m in enumerate(all_metrics):
            if m and m.get('hrv') is not None:
                # Normalize HRV to risk score (lower HRV = higher risk)
                # Typical range 20-100ms
                hrv_normalized = max(0, min(100, 100 - ((m.get('hrv') - 20) / 80 * 100)))
                hrv_risk_values.append((hrv_normalized, normalized_weights[i]))
        
        if hrv_risk_values:
            hrv_risk_score = sum(r * w for r, w in hrv_risk_values)
            
            # Calculate HRV trend if we have enough data points
            if len(hrv_risk_values) >= 3:
                recent_hrv = [m.get('hrv') for m in all_metrics[:3] if m and m.get('hrv') is not None]
                if len(recent_hrv) >= 2:
                    # Negative trend (decreasing HRV) increases risk
                    hrv_trend = -1 * (recent_hrv[0] - sum(recent_hrv[1:]) / len(recent_hrv[1:]))
                    hrv_trend = max(-20, min(20, hrv_trend))  # Limit extreme values
                    hrv_trend = hrv_trend * 2.5  # Scale to roughly 0-50
        else:
            hrv_risk_score = 50  # Neutral value
        
        # Add HRV trend factor to risk score (weight: 20% of HRV component)
        if hrv_trend > 0:  # Only consider negative trends (increasing risk)
            hrv_risk_score = hrv_risk_score * 0.8 + hrv_trend * 0.2
        
        # Component 3: Sleep Quality (15%)
        # Poor sleep quality is both a cause and symptom of burnout
        sleep_risk_values = []
        
        for i, m in enumerate(all_metrics):
            if m:
                # Calculate comprehensive sleep score
                sleep_score = compute_sleep_quality_score(m)
                if sleep_score is not None:
                    # Invert sleep score (100 - sleep_quality)
                    sleep_risk = 100 - sleep_score
                    sleep_risk_values.append((sleep_risk, normalized_weights[i]))
        
        if sleep_risk_values:
            sleep_risk_score = sum(r * w for r, w in sleep_risk_values)
        else:
            sleep_risk_score = 50  # Neutral value
        
        # Component 4: Strain-to-Recovery Balance (15%)
        # High strain with inadequate recovery increases burnout risk
        strain_recovery_values = []
        
        for i, m in enumerate(all_metrics):
            if m and m.get('strain') is not None and m.get('recovery_score') is not None:
                # Convert strain from 0-21 scale to 0-100
                strain_normalized = min(100, (m.get('strain') / 21) * 100)
                
                # Calculate strain-to-recovery ratio
                # Higher values indicate strain exceeding recovery capacity
                ratio = strain_normalized / m.get('recovery_score') if m.get('recovery_score') > 0 else 2.0
                
                # Convert to risk score (higher ratio = higher risk)
                # Healthy ratio is around 0.7-1.0
                if ratio < 0.7:
                    sr_risk = 20  # Undertraining - low risk
                elif ratio < 1.0:
                    sr_risk = 30 + (ratio - 0.7) * 100  # Optimal zone: 30-60
                elif ratio < 1.5:
                    sr_risk = 60 + (ratio - 1.0) * 80  # Increasing risk: 60-100
                else:
                    sr_risk = 100  # Maximum risk - significant overtraining
                
                strain_recovery_values.append((sr_risk, normalized_weights[i]))
        
        if strain_recovery_values:
            strain_recovery_risk = sum(r * w for r, w in strain_recovery_values)
        else:
            strain_recovery_risk = 50  # Neutral value
        
        # Component 5: Mood Assessment (30%)
        # Subjective mood is a key indicator of burnout state
        mood_risk_values = []
        mood_trend = 0
        
        for i, m in enumerate(all_metrics):
            if m and m.get('mood_rating') is not None:
                # Scale from 1-10 to 0-100 (invert so lower mood = higher risk)
                mood_risk = 100 - ((m.get('mood_rating') - 1) / 9 * 100)
                mood_risk_values.append((mood_risk, normalized_weights[i]))
        
        if mood_risk_values:
            mood_risk_score = sum(r * w for r, w in mood_risk_values)
            
            # Calculate mood trend if we have enough data points
            if len(mood_risk_values) >= 3:
                recent_mood = [m.get('mood_rating') for m in all_metrics[:3] if m and m.get('mood_rating') is not None]
                if len(recent_mood) >= 2:
                    # Negative trend (decreasing mood) increases risk
                    mood_trend = -1 * (recent_mood[0] - sum(recent_mood[1:]) / len(recent_mood[1:]))
                    mood_trend = max(-4, min(4, mood_trend))  # Limit extreme values
                    mood_trend = mood_trend * 12.5  # Scale to roughly 0-50
        else:
            mood_risk_score = 50  # Neutral value
        
        # Add mood trend factor to risk score (weight: 20% of mood component)
        if mood_trend > 0:  # Only consider negative trends (increasing risk)
            mood_risk_score = mood_risk_score * 0.8 + mood_trend * 0.2
        
        # Calculate total burnout risk score - weighted combination of all components
        component_weights = {
            'recovery': 0.25, 
            'hrv': 0.15, 
            'sleep': 0.15, 
            'strain_recovery': 0.15, 
            'mood': 0.30
        }
        
        # Calculate the final risk score
        burnout_risk = (
            recovery_risk_score * component_weights['recovery'] +
            hrv_risk_score * component_weights['hrv'] +
            sleep_risk_score * component_weights['sleep'] +
            strain_recovery_risk * component_weights['strain_recovery'] +
            mood_risk_score * component_weights['mood']
        )
        
        # Calculate the burnout trend (7-day)
        # Compare current day to average of previous 3-7 days
        burnout_trend = 0
        try:
            if len(all_metrics) >= 4 and all_metrics[0] and all_metrics[0].get('burnout_current') is not None:
                # Get previous burnout scores
                prev_burnout = [m.get('burnout_current') for m in all_metrics[1:] 
                              if m and m.get('burnout_current') is not None]
                
                if prev_burnout:
                    avg_prev_burnout = sum(prev_burnout) / len(prev_burnout)
                    burnout_trend = burnout_risk - avg_prev_burnout
        except Exception as e:
            logger.error(f"Error calculating burnout trend: {str(e)}")
        
        # Return the final risk score
        return min(100, max(0, burnout_risk))
        
    except Exception as e:
        logger.error(f"Error calculating burnout risk: {str(e)}")
        # Fallback to a simpler calculation if there's an error
        if metrics.get('recovery_score') is not None:
            recovery = metrics.get('recovery_score', 50)
            mood = metrics.get('mood_rating', 5)
            
            # Invert recovery (lower recovery = higher risk)
            recovery_factor = (100 - recovery) / 100
            
            # Invert mood (lower mood = higher risk)
            mood_factor = (10 - mood) / 10 if mood else 0.5
            
            # Calculate weighted risk (0-100)
            simple_risk = (recovery_factor * 0.7 + mood_factor * 0.3) * 100
            return min(100, max(0, simple_risk))
        
        return 50  # Neutral value

def generate_time_series_plot(days=30, db_records=None):
    """
    Generate a time series plot of recovery scores, mood ratings, and burnout risk.
    
    Args:
        days: Number of days to include in the plot
        db_records: List of dictionary records from Supabase
    
    Returns:
        str: JSON string of the plotly figure
    """
    # Handle missing records
    if not db_records:
        logger.warning("No records provided for time series plot")
        return json.dumps({})
    
    logger.info(f"Generating time series plot with {len(db_records)} records")
    
    try:
        # Sort records oldest to newest
        sorted_records = []
        for record in db_records:
            if 'date' in record:
                sorted_records.append(record)
                
        if sorted_records:
            logger.info(f"Found {len(sorted_records)} records with date field")
            sorted_records = sorted(
                sorted_records, 
                key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d").date() 
                    if isinstance(x['date'], str) 
                    else x['date']
            )
        
        # Limit to specified number of days
        records = sorted_records[-days:] if len(sorted_records) > days else sorted_records
        
        # Prepare data for plotting
        data = []
        for r in records:
            # Convert date string to date object if needed
            record_date = r.get('date')
            if isinstance(record_date, str):
                try:
                    record_date = datetime.strptime(record_date, "%Y-%m-%d").date()
                except ValueError:
                    pass
                    
            record_data = {
                "date": record_date,
                "recovery_score": r.get('recovery_score'),
                "mood_rating": r.get('mood_rating'),
                "strain": r.get('strain'),
                "hrv": r.get('hrv'),
                "burnout_risk": r.get('burnout_current')
            }
            data.append(record_data)
        
        # Create dataframe for plotting
        df = pd.DataFrame(data)
        
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Check if there's data before creating the plot
        if not df.empty:
            # Add burnout risk as a filled area in the background
            fig.add_trace(go.Scatter(
                x=df["date"], 
                y=df["burnout_risk"],
                name="Burnout Risk",
                fill='tozeroy',
                line=dict(color="rgba(255, 0, 0, 0.7)", width=1),
                fillcolor="rgba(255, 0, 0, 0.2)"
            ))
            
            # Add strain line (using secondary y-axis)
            fig.add_trace(go.Scatter(
                x=df["date"], 
                y=df["strain"],
                name="Strain (0-21)",
                line=dict(color="rgba(128, 0, 128, 0.8)", width=2, dash='dot'),
                yaxis="y2"
            ))
            
            # Add recovery score line
            fig.add_trace(go.Scatter(
                x=df["date"], 
                y=df["recovery_score"],
                name="Recovery Score",
                line=dict(color="green", width=2.5)
            ))
            
            # Add mood rating line with scaling to match recovery scale better
            # Scale mood from 1-10 to equivalent percentage for better visualization
            scaled_mood = df["mood_rating"].apply(lambda x: ((x - 1) / 9) * 100 if x is not None else None)
            
            fig.add_trace(go.Scatter(
                x=df["date"], 
                y=scaled_mood,
                name="Mood Rating",
                line=dict(color="blue", width=2.5)
            ))
            
            # Add HRV line
            if "hrv" in df.columns and not df["hrv"].isna().all():
                fig.add_trace(go.Scatter(
                    x=df["date"], 
                    y=df["hrv"],
                    name="HRV (ms)",
                    line=dict(color="orange", width=1.5, dash='dash'),
                    visible=True  # Make visible by default
                ))
        else:
            # Add an empty trace to prevent errors
            fig.add_trace(go.Scatter(
                x=[],
                y=[],
                name="No Data Available"
            ))
            
            # Add risk zones as horizontal areas
            fig.add_shape(
                type="rect",
                x0=df["date"].min() if not df.empty else 0,
                x1=df["date"].max() if not df.empty else 1,
                y0=0, y1=33,
                fillcolor="rgba(0, 255, 0, 0.1)",
                line=dict(width=0),
                layer="below"
            )
            
            fig.add_shape(
                type="rect",
                x0=df["date"].min() if not df.empty else 0,
                x1=df["date"].max() if not df.empty else 1,
                y0=33, y1=66,
                fillcolor="rgba(255, 255, 0, 0.1)",
                line=dict(width=0),
                layer="below"
            )
            
            fig.add_shape(
                type="rect",
                x0=df["date"].min() if not df.empty else 0,
                x1=df["date"].max() if not df.empty else 1,
                y0=66, y1=100,
                fillcolor="rgba(255, 0, 0, 0.1)",
                line=dict(width=0),
                layer="below"
            )
            
            # Update layout with second y-axis
            fig.update_layout(
                title="Recovery, Mood, and Burnout Risk Over Time",
                title_font=dict(size=18, family="Arial, sans-serif"),
                xaxis_title="Date",
                xaxis_title_font=dict(size=14),
                yaxis=dict(
                    title="Score (0-100)",
                    range=[0, 105],
                    gridcolor="rgba(0,0,0,0.1)",
                    side="left",  # Ensure main axis is on the left
                    titlefont=dict(size=14, family="Arial, sans-serif"),
                    tickfont=dict(size=12)
                ),
                yaxis2=dict(
                    title="Strain (0-21)",
                    titlefont=dict(size=14, family="Arial, sans-serif", color="rgba(128,0,128,0.8)"),
                    tickfont=dict(size=12, color="rgba(128,0,128,0.8)"),
                    range=[0, 21],
                    overlaying="y",
                    side="right",
                    gridcolor="rgba(128,0,128,0.1)",
                    showgrid=False
                ),
                legend=dict(
                    x=0.01, 
                    y=1.15, 
                    orientation="h", 
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.2)",
                    borderwidth=1,
                    font=dict(size=12)
                ),
                hovermode="x unified",
                margin=dict(t=80, b=50, l=70, r=70),
                height=500,
                paper_bgcolor='rgba(255,255,255,0.8)',
                plot_bgcolor='rgba(250,250,250,0.8)'
            )
        
        # Format data and layout for proper parsing in JavaScript
        data_json = {
            "data": fig.data,
            "layout": fig.layout
        }
        json_data = json.dumps(data_json, cls=plotly.utils.PlotlyJSONEncoder)
        logger.info(f"Generated time series JSON data of length: {len(json_data)}")
        return json_data
    except Exception as e:
        logger.error(f"Error generating time series plot: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return json.dumps({})

def generate_correlation_plot(db_records=None):
    """
    Generate advanced correlation plots showing relationships between
    recovery, mood, strain, and burnout risk.
    
    Args:
        db_records: List of dictionary records from Supabase
    
    Returns:
        str: JSON string of the plotly figure
    """
    if not db_records:
        logger.warning("No records provided for correlation plot")
        return json.dumps({})
        
    try:
        # Records from Supabase should already have burnout risk calculated
        
        # Create data dictionary for records with required fields
        data = []
        for r in db_records:
            if r.get('mood_rating') is not None and r.get('recovery_score') is not None:
                # Parse date to ensure consistent format
                if isinstance(r.get('date'), str):
                    date_obj = datetime.strptime(r.get('date'), "%Y-%m-%d").date()
                else:
                    date_obj = r.get('date')
                
                record_data = {
                    "date": date_obj,
                    "recovery_score": r.get('recovery_score'),
                    "mood_rating": r.get('mood_rating'),
                    "day_of_week": date_obj.strftime("%a"),  # Add day of week for coloring
                    "date_str": date_obj.strftime("%Y-%m-%d"),
                    "burnout_risk": r.get('burnout_current')
                }
                
                # Add other metrics if available
                if r.get('hrv') is not None:
                    record_data["hrv"] = r.get('hrv')
                if r.get('strain') is not None:
                    record_data["strain"] = r.get('strain')
                if r.get('sleep_quality') is not None:
                    record_data["sleep_quality"] = r.get('sleep_quality')
                
                data.append(record_data)
        
        df = pd.DataFrame(data)
        
        if len(df) > 1:
            # Create a more sophisticated figure with multiple correlation plots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    "Recovery vs. Mood", 
                    "Strain vs. Mood",
                    "Recovery vs. Burnout Risk",
                    "HRV vs. Burnout Risk"
                ),
                vertical_spacing=0.12
            )
            
            # 1. Recovery vs Mood (with trendline)
            # Calculate trend line
            z = np.polyfit(df["recovery_score"], df["mood_rating"], 1)
            y_fit = np.poly1d(z)(df["recovery_score"])
            
            fig.add_trace(
                go.Scatter(
                    x=df["recovery_score"], 
                    y=df["mood_rating"],
                mode="markers",
                name="Recovery vs Mood",
                marker=dict(
                    size=10,
                    color=df["burnout_risk"].fillna(50) if "burnout_risk" in df.columns else [50] * len(df),
                    colorscale="RdYlGn_r",
                    colorbar=dict(title="Burnout Risk"),
                    showscale=True,
                    cmin=0,
                    cmax=100
                ),
                text=df["date_str"],
                hovertemplate="<b>Date:</b> %{text}<br><b>Recovery:</b> %{x:.1f}<br><b>Mood:</b> %{y:.1f}<br>",
            ),
            row=1, col=1
        )
        
        # Add trendline
        fig.add_trace(
            go.Scatter(
                x=df["recovery_score"],
                y=y_fit,
                mode="lines",
                line=dict(color="rgba(0,0,0,0.5)", dash="dash"),
                name="Trend",
                hoverinfo="skip"
            ),
            row=1, col=1
        )
        
        # 2. Strain vs Mood (if strain data available)
        if "strain" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["strain"], 
                    y=df["mood_rating"],
                    mode="markers",
                    name="Strain vs Mood",
                    marker=dict(
                        size=10,
                        color=df["day_of_week"].astype("category").cat.codes.fillna(0),
                        colorscale="Viridis",
                        showscale=False
                    ),
                    text=df["date_str"],
                    hovertemplate="<b>Date:</b> %{text}<br><b>Strain:</b> %{x:.1f}<br><b>Mood:</b> %{y:.1f}<br>",
                ),
                row=1, col=2
            )
        
        # 3. Recovery vs Burnout Risk
        if "burnout_risk" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["recovery_score"], 
                    y=df["burnout_risk"],
                    mode="markers",
                    name="Recovery vs Burnout",
                    marker=dict(
                        size=10,
                        color=df["mood_rating"].fillna(5),
                        colorscale="Bluered_r",
                        showscale=False
                    ),
                    text=df["date_str"],
                    hovertemplate="<b>Date:</b> %{text}<br><b>Recovery:</b> %{x:.1f}<br><b>Burnout Risk:</b> %{y:.1f}%<br>",
                ),
                row=2, col=1
            )
        
        # 4. HRV vs Burnout Risk (if HRV data available)
        if "hrv" in df.columns and "burnout_risk" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["hrv"], 
                    y=df["burnout_risk"],
                    mode="markers",
                    name="HRV vs Burnout",
                    marker=dict(
                        size=10,
                        color=df["recovery_score"].fillna(50),
                        colorscale="RdYlGn",
                        showscale=False
                    ),
                    text=df["date_str"],
                    hovertemplate="<b>Date:</b> %{text}<br><b>HRV:</b> %{x:.1f} ms<br><b>Burnout Risk:</b> %{y:.1f}%<br>",
                ),
                row=2, col=2
            )
        
            # Update layout and axis titles
            fig.update_layout(
                height=700,
                title_text="Multi-dimensional Correlation Analysis",
                title_font=dict(size=18),
                showlegend=False,
                hovermode="closest",
                margin=dict(t=60, b=60, l=60, r=60),
                paper_bgcolor='rgba(255,255,255,0.8)',
                plot_bgcolor='rgba(250,250,250,0.8)'
            )
            
            # Format for all axes
            axis_title_font = dict(size=12, family="Arial, sans-serif")
            axis_tick_font = dict(size=10)
            grid_color = "rgba(0,0,0,0.1)"
            
            # Update all four subplots with consistent formatting
            fig.update_xaxes(title_text="Recovery Score", range=[0, 100], 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=1, col=1)
            fig.update_yaxes(title_text="Mood Rating", range=[0, 10], 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=1, col=1)
            
            fig.update_xaxes(title_text="Strain", range=[0, 21], 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=1, col=2)
            fig.update_yaxes(title_text="Mood Rating", range=[0, 10], 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=1, col=2)
            
            fig.update_xaxes(title_text="Recovery Score", range=[0, 100], 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=2, col=1)
            fig.update_yaxes(title_text="Burnout Risk %", range=[0, 100], 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=2, col=1)
            
            fig.update_xaxes(title_text="HRV (ms)", 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=2, col=2)
            fig.update_yaxes(title_text="Burnout Risk %", range=[0, 100], 
                            title_font=axis_title_font, tickfont=axis_tick_font, 
                            gridcolor=grid_color, row=2, col=2)
            
            # Format data and layout for proper parsing in JavaScript
            data_json = {
                "data": fig.data,
                "layout": fig.layout
            }
            json_data = json.dumps(data_json, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info(f"Generated correlation JSON data of length: {len(json_data)}")
            return json_data
        else:
            # Create an empty figure with a message
            fig = go.Figure()
            fig.add_annotation(
                text="Not enough data for correlation analysis<br>Enter mood ratings for multiple days to see correlations",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title="Correlation Analysis",
                xaxis_title="Recovery Score",
                yaxis_title="Mood Rating (1-10)",
                height=400
            )
            
            # Format data and layout for proper parsing in JavaScript
            data_json = {
                "data": fig.data,
                "layout": fig.layout
            }
            json_data = json.dumps(data_json, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info(f"Generated empty correlation JSON data of length: {len(json_data)}")
            return json_data
    except Exception as e:
        logger.error(f"Error generating correlation plot: {str(e)}")
        return json.dumps({})

if __name__ == "__main__":
    # Test the analysis functions
    corr, p_value = compute_correlation()
    print(f"Correlation: {corr}, p-value: {p_value}")