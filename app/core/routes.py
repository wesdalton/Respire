"""
Core routes for Burnout Predictor application
Includes dashboard, mood input, and data visualization
"""

import os
import logging
from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify

from . import core_bp
from app.auth.utils import get_user_id
from app.auth.routes import login_required
from app.database import USE_SUPABASE

# Logger setup
logger = logging.getLogger(__name__)

# Import database functions based on configuration
if USE_SUPABASE:
    from app.database.supabase import (
        get_daily_metrics, get_metrics_range, save_daily_metrics, delete_mood_data, 
        get_whoop_token
    )
else:
    from app.database.sqlite import (
        get_metrics_by_date, get_all_metrics, get_metrics_date_range, 
        add_or_update_daily_metrics, delete_mood, get_user_token
    )

# Import services
from app.services.analysis_service import (
    compute_correlation, generate_time_series_plot, 
    generate_correlation_plot, get_burnout_risk_score
)
from app.services.whoop_service import get_all_daily_metrics
from app.services.ai_service import get_burnout_insights

# Root route
@core_bp.route('/')
def index():
    """
    Main page - redirects to dashboard if logged in, login page if not
    Also handles OAuth callback for Whoop
    """
    # Check if this is a callback from OAuth authorization
    code = request.args.get('code')
    
    if code:
        # Process OAuth flow - redirected to dashboard
        from app.services.whoop_service import process_oauth_callback
        process_oauth_callback(code, get_user_id())
    
    # Check if user is authenticated
    from app.auth.utils import is_authenticated
    if is_authenticated():
        # Redirect to dashboard if logged in
        return redirect(url_for('core.dashboard'))
    else:
        # Redirect to login page if not logged in
        return redirect(url_for('auth.login'))

# Dashboard route
@core_bp.route('/dashboard')
@core_bp.route('/dashboard/<string:selected_date>')
@login_required
def dashboard(selected_date=None):
    try:
        user_id = get_user_id()
        
        # Load latest 30 days of data from database
        try:
            if USE_SUPABASE:
                records_data = get_daily_metrics(user_id)
            else:
                records_data = get_all_metrics(user_id)
                
            # Sort by date (most recent first)
            records = sorted(
                records_data[:30] if records_data else [], 
                key=lambda x: x.get('date', ''), 
                reverse=True
            )
        except Exception as e:
            logger.error(f"Error fetching records: {str(e)}")
            records = []
        
        # Calculate correlation if enough data points
        all_records = records_data if 'records_data' in locals() else []
        logger.info(f"Retrieved {len(all_records)} records from database")
        if len(all_records) > 0:
            logger.info(f"Sample record: {all_records[0]}")
        corr_text = None
        
        # Compute correlation between recovery score and mood rating
        try:
            corr, p_value = compute_correlation(all_records)
            if corr is not None and p_value is not None:
                significance = "significant" if p_value < 0.05 else "not significant"
                corr_text = f"Correlation between recovery and mood: {corr:.2f} (p-value: {p_value:.3f}, {significance})"
        except Exception as e:
            logger.error(f"Error calculating correlation: {str(e)}")
        
        # Generate visualizations
        try:
            # Pass all records to visualization functions
            logger.info(f"Generating visualizations with {len(all_records)} records")
            time_series = generate_time_series_plot(db_records=all_records)
            correlation_plot = generate_correlation_plot(db_records=all_records)
            logger.info(f"Visualization generation successful: time_series={time_series is not None}, correlation_plot={correlation_plot is not None}")
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            time_series = None
            correlation_plot = None
        
        # Determine the date to display
        if selected_date:
            try:
                # Parse the provided date
                display_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            except ValueError:
                # If invalid date format, default to today
                display_date = date.today()
        else:
            # Default to today if no date provided
            display_date = date.today()
        
        # Get record for the selected date
        selected_record = None
        burnout_risk = None
        
        try:
            # Get from database
            date_str = display_date.strftime("%Y-%m-%d") if isinstance(display_date, date) else display_date
            if USE_SUPABASE:
                selected_records = get_daily_metrics(user_id, date_str)
                if selected_records and len(selected_records) > 0:
                    selected_record = selected_records[0]  # Keep as dictionary
            else:
                selected_record = get_metrics_by_date(user_id, date_str)
                
            # Get burnout risk from the record
            if selected_record:
                burnout_risk = selected_record.get('burnout_current')
                
                # If burnout risk is not available, calculate it
                if burnout_risk is None and (
                    (isinstance(selected_record, dict) and selected_record.get('recovery_score') is not None) or
                    (not isinstance(selected_record, dict) and selected_record.recovery_score is not None)
                ):
                    # Get historical data for accurate burnout calculation
                    burnout_risk = get_burnout_risk_score(selected_record, all_records)
                    
                    # Update record with calculated burnout risk
                    if isinstance(selected_record, dict):
                        selected_record['burnout_current'] = burnout_risk
                    else:
                        selected_record.burnout_current = burnout_risk
                        
                    # Save the updated record
                    if USE_SUPABASE:
                        save_daily_metrics(user_id, selected_record)
                    else:
                        add_or_update_daily_metrics(selected_record)
        except Exception as e:
            logger.error(f"Error getting selected record: {str(e)}")
            
        # Calculate next and previous dates
        if isinstance(display_date, date):
            next_date = (display_date + timedelta(days=1)).strftime("%Y-%m-%d")
            prev_date = (display_date - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            # Handle string date
            try:
                date_obj = datetime.strptime(display_date, "%Y-%m-%d").date()
                next_date = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
                prev_date = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                # Fallback to today if we can't parse the date
                today = date.today()
                next_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
                prev_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Make previous day always available and next day available up to today
        if isinstance(display_date, date):
            has_next = display_date < date.today()
        else:
            # For string dates, compare with today's string
            today_str = date.today().strftime("%Y-%m-%d")
            has_next = display_date < today_str
            
        has_prev = True  # Always allow going back to previous days
        
        # Check if authenticated with Whoop
        try:
            if USE_SUPABASE:
                token_info = get_whoop_token(user_id)
            else:
                token_info = get_user_token(user_id)
                
            # Consider authenticated if we have any token data, even if expired
            whoop_authenticated = token_info and token_info.get("access_token") is not None
            logger.debug(f"Token info retrieved for user: {user_id}")
        except Exception as e:
            logger.error(f"Error checking Whoop token: {str(e)}")
            whoop_authenticated = False
            
        logger.info(f"Authentication status: {whoop_authenticated}")
        logger.info(f"Preparing dashboard for date: {display_date}")
        
        # Log key template variables
        logger.info(f"Rendering dashboard with time_series={time_series is not None}")
        logger.info(f"Rendering dashboard with correlation_plot={correlation_plot is not None}")
        logger.info(f"Rendering dashboard with correlation_text={corr_text is not None}")
        
        return render_template(
            'dashboard.html',
            time_series=time_series,
            correlation_plot=correlation_plot,
            correlation_text=corr_text,
            selected_record=selected_record,
            selected_date=display_date,
            burnout_risk=burnout_risk,
            records=records,
            get_burnout_risk_score=get_burnout_risk_score,
            now=datetime.now(),
            whoop_authenticated=whoop_authenticated,
            next_date=next_date,
            prev_date=prev_date,
            has_next=has_next,
            has_prev=has_prev,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error loading dashboard: {str(e)}"

@core_bp.route('/input', methods=['GET', 'POST'])
@core_bp.route('/input/<string:input_date>', methods=['GET', 'POST'])
@login_required
def input_mood(input_date=None):
    """Input mood rating for a specific date"""
    from datetime import datetime, date, timedelta
    user_id = get_user_id()
    
    # Determine the date we're entering mood for
    if input_date:
        try:
            mood_date = datetime.strptime(input_date, "%Y-%m-%d").date()
        except ValueError:
            # If invalid date format, default to today
            mood_date = date.today()
            flash("Invalid date format, defaulting to today.")
    else:
        # Default to today if no date provided
        mood_date = date.today()
    
    if request.method == 'POST':
        try:
            mood = int(request.form.get("mood_rating"))
            notes = request.form.get("notes", "")
            selected_date = request.form.get("date", mood_date.strftime("%Y-%m-%d"))
            
            # Parse the date from the form
            try:
                entry_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            except ValueError:
                entry_date = mood_date
            
            # Validate mood rating
            if mood < 1 or mood > 10:
                flash("Mood rating must be between 1 and 10.")
                return redirect(url_for('core.input_mood', input_date=entry_date.strftime("%Y-%m-%d")))
            
            # Create mood data dictionary
            mood_data = {
                "mood_rating": mood,
                "notes": notes
            }
            
            # Format date for API
            date_str = entry_date.strftime("%Y-%m-%d")
            
            # Fetch Whoop data for the selected date
            username = user_id if isinstance(user_id, str) else "default"
            whoop_data = get_all_daily_metrics(date_str, username)
            
            # Create data object with just the date if no Whoop data
            date_data = {"date": date_str}
            
            # Add or update record - If whoop_data is None or empty, only pass the date
            # This ensures we don't overwrite existing WHOOP data
            metrics_data = whoop_data if whoop_data and any(v is not None for k,v in whoop_data.items() if k != "date") else date_data
            
            if USE_SUPABASE:
                # Save to Supabase
                save_daily_metrics(user_id, metrics_data, mood_data)
                
                # Recalculate burnout risk for the current day
                try:
                    # Get the updated record and all historical records
                    updated_record = get_daily_metrics(user_id, date_str)
                    all_records = get_daily_metrics(user_id)
                    
                    if updated_record and len(updated_record) > 0:
                        # Calculate new burnout risk
                        new_risk = get_burnout_risk_score(updated_record[0], all_records)
                        
                        if new_risk is not None:
                            # Update the record with the new burnout risk
                            updated_record[0]['burnout_current'] = new_risk
                            save_daily_metrics(user_id, updated_record[0])
                            logger.info(f"Recalculated burnout risk for {date_str}: {new_risk}")
                            
                            # Recalculate future days that may be affected by this change
                            # (typically only a few days after this date would be affected by the trend analysis)
                            entry_date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                            
                            # Check next 7 days for records that need updating
                            for i in range(1, 8):
                                future_date = entry_date_obj + timedelta(days=i)
                                future_date_str = future_date.strftime("%Y-%m-%d")
                                future_records = get_daily_metrics(user_id, future_date_str)
                                
                                if future_records and len(future_records) > 0:
                                    # Recalculate with updated historical data
                                    future_risk = get_burnout_risk_score(future_records[0], all_records)
                                    if future_risk is not None:
                                        future_records[0]['burnout_current'] = future_risk
                                        save_daily_metrics(user_id, future_records[0])
                                        logger.info(f"Updated future day burnout risk for {future_date_str}: {future_risk}")
                            
                except Exception as e:
                    logger.error(f"Error recalculating burnout risk: {str(e)}")
            else:
                # Save to SQLite
                add_or_update_daily_metrics(metrics_data, mood_data)
            
            flash("Mood rating saved successfully!")
            return redirect(url_for('core.dashboard', selected_date=date_str))
            
        except ValueError:
            flash("Please enter a valid mood rating (1-10).")
            return redirect(url_for('core.input_mood', input_date=mood_date.strftime("%Y-%m-%d")))
    
    # For GET request, show the form
    date_str = mood_date.strftime("%Y-%m-%d")
    
    # Get record for the selected date
    if USE_SUPABASE:
        # Get from Supabase
        selected_records = get_daily_metrics(user_id, date_str)
        record = selected_records[0] if selected_records else None
    else:
        # Get from SQLite
        record = get_metrics_by_date(user_id, date_str)
    
    return render_template('input.html', mood_date=mood_date, date_str=date_str, record=record)

@core_bp.route('/delete_mood/<string:selected_date>')
@login_required
def delete_mood(selected_date):
    """
    Delete a mood entry for a specific date
    """
    user_id = get_user_id()
    
    try:
        # Parse the date
        try:
            entry_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            date_str = selected_date
        except ValueError:
            flash("Invalid date format.")
            return redirect(url_for('core.dashboard'))
        
        # Delete mood data
        if USE_SUPABASE:
            success = delete_mood_data(user_id, date_str)
        else:
            success = delete_mood(user_id, date_str)
            
        if success:
            flash("Mood rating deleted successfully.")
        else:
            flash("No mood data found for this date.")
    except Exception as e:
        logger.error(f"Error deleting mood: {str(e)}")
        flash(f"Error deleting mood: {str(e)}")
    
    return redirect(url_for('core.dashboard', selected_date=date_str))

@core_bp.route('/fetch_whoop_data', methods=['POST'])
@login_required
def manual_fetch_data():
    """
    Manually fetch Whoop data for a specific date or date range.
    """
    date_str = request.form.get("date")
    user_id = get_user_id()
    
    if not date_str:
        date_str = date.today().strftime("%Y-%m-%d")
    
    try:
        # Convert to date object to validate format
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Fetch data using the user's Whoop token
        logger.info(f"Fetching Whoop data for user {user_id} on {date_str}")
        metrics = get_all_daily_metrics(date_str, user_id)
        
        if metrics and any(v is not None for k, v in metrics.items() if k != 'date'):
            # Store in database
            if USE_SUPABASE:
                save_daily_metrics(user_id, metrics)
            else:
                add_or_update_daily_metrics(metrics)
                
            flash(f"Successfully fetched Whoop data for {date_str}")
            logger.info(f"Successfully stored metrics for {date_str}")
        else:
            flash(f"No Whoop data available for {date_str}")
            logger.warning(f"No data available for {date_str}")
        
        # Redirect back to the same date's dashboard
        return redirect(url_for('core.dashboard', selected_date=date_str))
        
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        flash("Please enter a valid date in YYYY-MM-DD format.")
        return redirect(url_for('core.dashboard'))
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        flash(f"Error fetching data: {str(e)}")
        return redirect(url_for('core.dashboard'))

@core_bp.route('/ai-insights', methods=['GET', 'POST'])
@login_required
def ai_insights():
    """
    Get AI-powered insights about the user's burnout risk and metrics.
    Loads the page immediately and fetches insights asynchronously.
    """
    user_id = get_user_id()
    query = None
    
    if request.method == 'POST':
        # Get user query if provided
        query = request.form.get('query')
        
        # For POST requests with AJAX, generate and return insights
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Get user data
                if USE_SUPABASE:
                    records_data = get_daily_metrics(user_id)
                else:
                    records_data = get_all_metrics(user_id)
                
                if not records_data:
                    return jsonify({
                        "success": False,
                        "error": "No data available for analysis",
                        "insight": "Please add some health data before requesting insights."
                    })
                
                # Generate insights
                insights_response = get_burnout_insights(records_data, query)
                return jsonify(insights_response)
                
            except Exception as e:
                logger.error(f"Error in AI insights API: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "insight": "An error occurred while generating AI insights."
                })
    
    try:
        # Get user data from the database
        if USE_SUPABASE:
            records_data = get_daily_metrics(user_id)
        else:
            records_data = get_all_metrics(user_id)
        
        # Sort records by date for better analysis
        records = sorted(
            records_data if records_data else [], 
            key=lambda x: x.get('date', ''), 
            reverse=True
        )
        
        if not records:
            flash("No data available for AI analysis.")
            return redirect(url_for('core.dashboard'))
        
        # Render the page immediately with loading state
        # The insights will be fetched via AJAX after the page loads
        return render_template(
            'ai_insights.html',
            insights=None,  # Set to None to show loading animation
            records=records[:7],  # Show last 7 days of data
            query=query
        )
            
    except Exception as e:
        logger.error(f"Error in AI insights route: {str(e)}")
        flash(f"Error accessing your data: {str(e)}")
        return redirect(url_for('core.dashboard'))

@core_bp.route('/auth')
@login_required
def auth():
    """
    Start the OAuth flow to authorize the app with WHOOP.
    """
    # Get the auth URL with the main page as the redirect
    from app.services.whoop_service import get_auth_url
    authorization_url, state = get_auth_url()
    
    # Store the state in the session for later validation
    flask_session['oauth_state'] = state
    
    # Print the URL for debugging
    print(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)

@core_bp.route('/settings')
@login_required
def settings():
    """
    Settings page for managing user preferences, integrations, and app settings
    """
    user_id = get_user_id()
    
    # Check if the user is connected to WHOOP
    try:
        if USE_SUPABASE:
            token_info = get_whoop_token(user_id)
        else:
            token_info = get_user_token(user_id)
            
        whoop_authenticated = token_info and token_info.get("access_token") is not None
    except Exception as e:
        logger.error(f"Error checking WHOOP token: {str(e)}")
        whoop_authenticated = False
    
    # Get the OpenAI API key from environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        # Mask the key for display
        key_start = openai_key[:4]
        key_end = openai_key[-4:] if len(openai_key) > 8 else ""
        masked_key = f"{key_start}...{key_end}"
    else:
        masked_key = None
    
    # Get AI model preference
    ai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Get notification preferences (placeholder for future implementation)
    notification_settings = {
        "email_notifications": False,
        "high_risk_alerts": False,
        "weekly_summary": False
    }
    
    # Get appearance settings (placeholder for future implementation)
    appearance_settings = {
        "theme": "system",
        "chart_type": "time_series"
    }
    
    return render_template(
        'settings.html',
        whoop_authenticated=whoop_authenticated,
        openai_key=masked_key,
        ai_model=ai_model,
        notification_settings=notification_settings,
        appearance_settings=appearance_settings
    )

@core_bp.route('/update_openai_key', methods=['POST'])
@login_required
def update_openai_key():
    """
    Update the OpenAI API key in the .env file
    """
    api_key = request.form.get('openai_api_key', '').strip()
    ai_model = request.form.get('ai_model', 'gpt-4o-mini')
    
    # Only update if a key is provided
    if api_key:
        try:
            # Read the current .env file
            env_path = os.path.join(os.getcwd(), '.env')
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
            
            # Update or add the OPENAI_API_KEY
            key_found = False
            model_found = False
            new_lines = []
            
            for line in env_lines:
                if line.startswith('OPENAI_API_KEY='):
                    # Update the key (without quotes to avoid double-quoting)
                    new_lines.append(f'OPENAI_API_KEY={api_key}\n')
                    key_found = True
                elif line.startswith('OPENAI_MODEL='):
                    # Update the model
                    new_lines.append(f'OPENAI_MODEL={ai_model}\n')
                    model_found = True
                else:
                    new_lines.append(line)
            
            # Add the key if not found
            if not key_found:
                new_lines.append(f'OPENAI_API_KEY={api_key}\n')
            
            # Add the model if not found
            if not model_found:
                new_lines.append(f'OPENAI_MODEL={ai_model}\n')
            
            # Write back to the .env file
            with open(env_path, 'w') as f:
                f.writelines(new_lines)
            
            # Update the environment variables in the current process
            os.environ['OPENAI_API_KEY'] = api_key
            os.environ['OPENAI_MODEL'] = ai_model
            
            flash("OpenAI API key and model saved successfully")
        except Exception as e:
            logger.error(f"Error updating OpenAI API key: {str(e)}")
            flash(f"Error saving OpenAI API key: {str(e)}")
    else:
        # If no key provided, just update the model
        try:
            # Read the current .env file
            env_path = os.path.join(os.getcwd(), '.env')
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
            
            # Update or add the OPENAI_MODEL
            model_found = False
            new_lines = []
            
            for line in env_lines:
                if line.startswith('OPENAI_MODEL='):
                    # Update the model
                    new_lines.append(f'OPENAI_MODEL={ai_model}\n')
                    model_found = True
                else:
                    new_lines.append(line)
            
            # Add the model if not found
            if not model_found:
                new_lines.append(f'OPENAI_MODEL={ai_model}\n')
            
            # Write back to the .env file
            with open(env_path, 'w') as f:
                f.writelines(new_lines)
            
            # Update the environment variable in the current process
            os.environ['OPENAI_MODEL'] = ai_model
            
            flash("AI model preference saved")
        except Exception as e:
            logger.error(f"Error updating AI model: {str(e)}")
            flash(f"Error saving AI model preference: {str(e)}")
    
    return redirect(url_for('core.settings'))

@core_bp.route('/disconnect_whoop', methods=['POST'])
@login_required
def disconnect_whoop():
    """
    Disconnect the user's WHOOP account
    """
    user_id = get_user_id()
    
    try:
        # Remove the token from the database
        # TODO: Implement token deletion
        flash("WHOOP account disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting WHOOP: {str(e)}")
        flash(f"Error disconnecting WHOOP: {str(e)}")
    
    return redirect(url_for('core.settings'))

@core_bp.route('/update_notifications', methods=['POST'])
@login_required
def update_notifications():
    """Update notification settings"""
    # Placeholder for future implementation
    flash("Notification settings updated")
    return redirect(url_for('core.settings'))

@core_bp.route('/update_appearance', methods=['POST'])
@login_required
def update_appearance():
    """Update appearance settings"""
    # Placeholder for future implementation
    flash("Appearance settings updated")
    return redirect(url_for('core.settings'))

@core_bp.route('/update_account', methods=['POST'])
@login_required
def update_account():
    """Update account settings (password)"""
    # Placeholder for future implementation
    flash("Account settings updated")
    return redirect(url_for('core.settings'))