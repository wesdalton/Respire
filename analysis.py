import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from database import session, DailyMetrics
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import json
from datetime import datetime, timedelta

def compute_correlation():
    """
    Compute the Pearson correlation coefficient between recovery score and mood rating.
    
    Returns:
        tuple: (correlation, p-value) or (None, None) if insufficient data
    """
    records = session.query(DailyMetrics).all()
    data = [{
        "recovery_score": r.recovery_score,
        "mood_rating": r.mood_rating
    } for r in records if r.mood_rating is not None and r.recovery_score is not None]
    
    df = pd.DataFrame(data)
    
    if len(df) > 1:
        corr, p_value = pearsonr(df["recovery_score"], df["mood_rating"])
        return corr, p_value
    
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
        metrics_list: List of DailyMetrics objects
        
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
        
        if metrics.recovery_score is not None:
            available_count += 1
        if metrics.mood_rating is not None:
            available_count += 1
        if metrics.hrv is not None:
            available_count += 1
        if metrics.strain is not None:
            available_count += 1
            
        # Calculate completeness ratio
        completeness = available_count / total_count
        completeness_weights.append(completeness)
    
    # Normalize to ensure weights sum to available days (not 1.0)
    # This preserves the information about missing days
    return completeness_weights

def get_prior_metrics(metrics, session, days_back=7):
    """
    Retrieve metrics from previous days for temporal analysis.
    
    Args:
        metrics: Current day's DailyMetrics object
        session: Database session
        days_back: Number of days to look back
        
    Returns:
        List of DailyMetrics objects for previous days
    """
    if not metrics or not metrics.date:
        return []
    
    prior_metrics = []
    current_date = metrics.date
    
    for i in range(1, days_back + 1):
        prior_date = current_date - timedelta(days=i)
        prior_day = session.query(DailyMetrics).filter_by(date=prior_date).first()
        prior_metrics.append(prior_day)  # Will be None if day doesn't exist
    
    return prior_metrics

def compute_sleep_quality_score(metrics):
    """
    Compute a comprehensive sleep quality score from multiple sleep metrics.
    
    Args:
        metrics: DailyMetrics object
        
    Returns:
        Sleep quality score from 0-100
    """
    if not metrics:
        return None
        
    scores = []
    weights = []
    
    # Basic sleep quality (if available)
    if metrics.sleep_quality is not None:
        scores.append(metrics.sleep_quality)
        weights.append(0.4)
    
    # Sleep efficiency
    if metrics.sleep_efficiency is not None:
        scores.append(metrics.sleep_efficiency)
        weights.append(0.3)
    
    # Sleep consistency
    if metrics.sleep_consistency is not None:
        scores.append(metrics.sleep_consistency)
        weights.append(0.3)
    
    # Sleep stages (normalize deep and REM sleep)
    if metrics.total_sleep_time is not None and metrics.total_sleep_time > 0:
        # Calculate percentage of deep sleep (ideal: 15-25%)
        if metrics.deep_sleep_time is not None:
            deep_pct = (metrics.deep_sleep_time / metrics.total_sleep_time) * 100
            # Optimal deep sleep around 20%
            deep_score = 100 - min(100, abs(deep_pct - 20) * 5)
            scores.append(deep_score)
            weights.append(0.1)
            
        # Calculate percentage of REM sleep (ideal: 20-25%)
        if metrics.rem_sleep_time is not None:
            rem_pct = (metrics.rem_sleep_time / metrics.total_sleep_time) * 100
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
    return metrics.sleep_quality

def get_burnout_risk_score(metrics):
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
        metrics: Current day's DailyMetrics object containing WHOOP data
    
    Returns:
        float: Burnout risk score (0-100, higher means higher risk)
        Dictionary of component scores for explanation
    """
    if not metrics or not metrics.recovery_score:
        return None
    
    from database import session
    
    # Get metrics from previous days for temporal analysis
    prior_metrics = get_prior_metrics(metrics, session, days_back=7)
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
        if m and m.recovery_score is not None:
            # Invert recovery score (100 - recovery)
            recovery_risk = 100 - m.recovery_score
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
        if m and m.hrv is not None:
            # Normalize HRV to risk score (lower HRV = higher risk)
            # Typical range 20-100ms
            hrv_normalized = max(0, min(100, 100 - ((m.hrv - 20) / 80 * 100)))
            hrv_risk_values.append((hrv_normalized, normalized_weights[i]))
    
    if hrv_risk_values:
        hrv_risk_score = sum(r * w for r, w in hrv_risk_values)
        
        # Calculate HRV trend if we have enough data points
        if len(hrv_risk_values) >= 3:
            recent_hrv = [m.hrv for m in all_metrics[:3] if m and m.hrv is not None]
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
        if m and m.strain is not None and m.recovery_score is not None:
            # Convert strain from 0-21 scale to 0-100
            strain_normalized = min(100, (m.strain / 21) * 100)
            
            # Calculate strain-to-recovery ratio
            # Higher values indicate strain exceeding recovery capacity
            ratio = strain_normalized / m.recovery_score if m.recovery_score > 0 else 2.0
            
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
        if m and m.mood_rating is not None:
            # Scale from 1-10 to 0-100 (invert so lower mood = higher risk)
            mood_risk = 100 - ((m.mood_rating - 1) / 9 * 100)
            mood_risk_values.append((mood_risk, normalized_weights[i]))
    
    if mood_risk_values:
        mood_risk_score = sum(r * w for r, w in mood_risk_values)
        
        # Calculate mood trend if we have enough data points
        if len(mood_risk_values) >= 3:
            recent_mood = [m.mood_rating for m in all_metrics[:3] if m and m.mood_rating is not None]
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
    if len(all_metrics) >= 4 and all_metrics[0] and all_metrics[0].burnout_current is not None:
        # Get previous burnout scores
        prev_burnout = [m.burnout_current for m in all_metrics[1:] if m and m.burnout_current is not None]
        
        if prev_burnout:
            avg_prev_burnout = sum(prev_burnout) / len(prev_burnout)
            burnout_trend = burnout_risk - avg_prev_burnout
        else:
            burnout_trend = 0
    else:
        burnout_trend = 0
    
    # Store the calculated values in the database for future trend analysis
    metrics.burnout_current = burnout_risk
    metrics.burnout_trend = burnout_trend
    session.commit()
    
    # Create component breakdown for explanation
    components = {
        'recovery_risk': recovery_risk_score,
        'hrv_risk': hrv_risk_score,
        'sleep_risk': sleep_risk_score,
        'strain_recovery_risk': strain_recovery_risk,
        'mood_risk': mood_risk_score,
        'trend': burnout_trend
    }
    
    return min(100, max(0, burnout_risk))

def generate_time_series_plot(days=30):
    """
    Generate a time series plot of recovery scores, mood ratings, and burnout risk.
    This function calculates burnout risk using the advanced model that accounts
    for time series patterns.
    
    Args:
        days: Number of days to include in the plot
    
    Returns:
        str: JSON string of the plotly figure
    """
    records = session.query(DailyMetrics).order_by(DailyMetrics.date.desc()).limit(days).all()
    records.reverse()  # Show oldest to newest
    
    # Process records and calculate burnout risk if not already stored
    for r in records:
        if r.burnout_current is None:
            # This will calculate and store the burnout risk in the database
            get_burnout_risk_score(r)
    
    # Prepare data for plotting
    data = [{
        "date": r.date,
        "recovery_score": r.recovery_score,
        "mood_rating": r.mood_rating,
        "strain": r.strain,
        "hrv": r.hrv,
        "burnout_risk": r.burnout_current
    } for r in records]
    
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
                visible="legendonly"  # Hidden by default, can be toggled
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
        xaxis_title="Date",
        yaxis=dict(
            title="Score (0-100)",
            range=[0, 105],
            gridcolor="rgba(0,0,0,0.1)"
        ),
        yaxis2=dict(
            title="Strain (0-21)",
            range=[0, 21],
            overlaying="y",
            side="right",
            gridcolor="rgba(128,0,128,0.1)"
        ),
        legend=dict(x=0, y=1.1, orientation="h"),
        hovermode="x unified",
        margin=dict(t=50, b=50),
        height=500
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_correlation_plot():
    """
    Generate advanced correlation plots showing relationships between
    recovery, mood, strain, and burnout risk.
    
    Returns:
        str: JSON string of the plotly figure
    """
    # Query all records with required fields
    records = session.query(DailyMetrics).all()
    
    # Process burnout risk for all records first
    for r in records:
        if r.burnout_current is None and r.recovery_score is not None:
            get_burnout_risk_score(r)
    
    # Create data dictionary for records with required fields
    data = []
    for r in records:
        if r.mood_rating is not None and r.recovery_score is not None:
            record_data = {
                "date": r.date,
                "recovery_score": r.recovery_score,
                "mood_rating": r.mood_rating,
                "day_of_week": r.date.strftime("%a"),  # Add day of week for coloring
                "date_str": r.date.strftime("%Y-%m-%d"),
                "burnout_risk": r.burnout_current
            }
            
            # Add other metrics if available
            if r.hrv is not None:
                record_data["hrv"] = r.hrv
            if r.strain is not None:
                record_data["strain"] = r.strain
            if r.sleep_quality is not None:
                record_data["sleep_quality"] = r.sleep_quality
                
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
                    color=df["burnout_risk"] if "burnout_risk" in df.columns else None,
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
                        color=df["day_of_week"].astype("category").cat.codes,
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
                        color=df["mood_rating"],
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
                        color=df["recovery_score"],
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
            showlegend=False,
            hovermode="closest"
        )
        
        fig.update_xaxes(title_text="Recovery Score", range=[0, 100], row=1, col=1)
        fig.update_yaxes(title_text="Mood Rating", range=[0, 10], row=1, col=1)
        
        fig.update_xaxes(title_text="Strain", range=[0, 21], row=1, col=2)
        fig.update_yaxes(title_text="Mood Rating", range=[0, 10], row=1, col=2)
        
        fig.update_xaxes(title_text="Recovery Score", range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="Burnout Risk %", range=[0, 100], row=2, col=1)
        
        fig.update_xaxes(title_text="HRV (ms)", row=2, col=2)
        fig.update_yaxes(title_text="Burnout Risk %", range=[0, 100], row=2, col=2)
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
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
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

if __name__ == "__main__":
    # Test the analysis functions
    corr, p_value = compute_correlation()
    print(f"Correlation: {corr}, p-value: {p_value}")