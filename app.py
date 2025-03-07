from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session as flask_session
from datetime import date, datetime, timedelta
from whoop_api import (
    get_all_daily_metrics, get_auth_url, get_client_credentials_token, 
    get_valid_access_token, REDIRECT_URI
)
from analysis import compute_correlation, generate_time_series_plot, generate_correlation_plot, get_burnout_risk_score
from ai_insights import get_burnout_insights
import os
import requests
import uuid
import logging
from functools import wraps
from dotenv import load_dotenv

# Always load environment variables at the very start of the application
load_dotenv(override=True)
from apscheduler.schedulers.background import BackgroundScheduler

# Import Supabase client
from supabase_client import (
    sign_up, sign_in, sign_out, get_current_user, 
    save_daily_metrics, get_daily_metrics, get_metrics_range,
    save_whoop_token, get_whoop_token
)

# We're using Supabase exclusively now
USE_SUPABASE = True

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))  # For flash messages and sessions
app.config['SESSION_TYPE'] = 'filesystem'

# Authentication helpers
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flask_session['next_url'] = request.url
            flash("Please log in to access this page")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    
    # Mark this function as having login required
    decorated_function._login_required = True
    return decorated_function

def is_authenticated():
    """Check if the user is authenticated"""
    # Check Supabase session
    try:
        current_user = get_current_user()
        return current_user is not None
    except Exception as e:
        logger.error(f"Error checking authentication: {str(e)}")
        return False

def get_user_id():
    """Get the current user ID"""
    # First check Flask session in any case
    user_id = flask_session.get('user_id')
    if user_id:
        logger.debug(f"Found user_id in Flask session: {user_id}")
        return user_id
        
    # Try to get from Supabase auth
    try:
        current_user = get_current_user()
        if current_user and current_user.user:
            logger.debug(f"Found user from Supabase auth: {current_user.user.id}")
            return current_user.user.id
    except Exception as e:
        logger.error(f"Error getting user from Supabase: {str(e)}")
            
    # Fall back to admin user
    admin_id = os.getenv("SUPABASE_USER_ID")
    if admin_id:
        logger.debug(f"Using admin ID from env: {admin_id}")
        return admin_id
            
    # Last resort - this should not happen in production
    logger.warning("No user ID found, using default")
    return "default"

# Scheduler to fetch data daily
scheduler = BackgroundScheduler()

def fetch_and_store_whoop_data():
    """
    Background task to fetch Whoop data and store it in the database.
    """
    today_str = datetime.today().strftime("%Y-%m-%d")
    
    # For demo purposes, use admin user from env
    # In a production multi-user environment, this would need to iterate through all users
    user_id = os.getenv("SUPABASE_USER_ID")
    if not user_id:
        logger.error("No admin user ID set, cannot fetch data")
        return
    
    try:
        # Get metrics using Whoop API
        metrics = get_all_daily_metrics(today_str, user_id)
        
        if metrics and any(v is not None for k, v in metrics.items() if k != 'date'):
            # Store in Supabase
            save_daily_metrics(user_id, metrics)
            logger.info(f"Successfully updated metrics for {today_str}")
        else:
            logger.warning(f"No metrics data available for {today_str}")
    except Exception as e:
        logger.error(f"Error fetching/storing Whoop data: {str(e)}")

# Schedule job to run daily at midnight
scheduler.add_job(func=fetch_and_store_whoop_data, trigger="cron", hour=0, minute=5)
scheduler.start()

# Authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Register a new user"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please provide both email and password")
            return render_template('signup.html', now=datetime.now())
        
        try:
            response = sign_up(email, password)
            
            # Check if email confirmation is required
            if response.user.confirmation_sent_at:
                flash("Please check your email to confirm your account")
            else:
                # Store user in session
                flask_session['user_id'] = response.user.id
                flask_session['user_email'] = email
                flash("Account created successfully")
                
                # Redirect to original destination if available
                next_url = flask_session.pop('next_url', None)
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            flash(f"Error creating account: {str(e)}")
    
    return render_template('signup.html', now=datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please provide both email and password")
            return render_template('login.html', now=datetime.now())
        
        try:
            response = sign_in(email, password)
            
            # Store user in session
            flask_session['user_id'] = response.user.id
            flask_session['user_email'] = email
            flash("Logged in successfully")
            
            # Redirect to original destination if available
            next_url = flask_session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Error logging in: {str(e)}")
            flash(f"Error logging in: {str(e)}")
            
            return render_template('login.html', now=datetime.now())
    
    return render_template('login.html', now=datetime.now())

@app.route('/logout')
def logout():
    """Log out the current user"""
    try:
        sign_out(flask_session)
    except Exception as e:
        logger.error(f"Error signing out from Supabase: {str(e)}")
    
    # Clear Flask session
    flask_session.clear()
    
    flash("Logged out successfully")
    return redirect(url_for('login'))

# Note: The '/' route is now handled by the index function below

@app.route('/dashboard')
@app.route('/dashboard/<string:selected_date>')
@login_required
def dashboard(selected_date=None):
    try:
        user_id = get_user_id()
        
        # Load latest 30 days of data from Supabase
        try:
            records_data = get_daily_metrics(user_id)
            
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
        
        try:
            # Create temporary data frame from records for correlation
            data_for_corr = [
                {"recovery_score": r.get("recovery_score"), "mood_rating": r.get("mood_rating")}
                for r in all_records
                if r.get("recovery_score") is not None and r.get("mood_rating") is not None
            ]
            
            if len(data_for_corr) > 1:
                import pandas as pd
                from scipy.stats import pearsonr
                
                df = pd.DataFrame(data_for_corr)
                corr, p_value = pearsonr(df["recovery_score"], df["mood_rating"])
                significance = "significant" if p_value < 0.05 else "not significant"
                corr_text = f"Correlation between recovery and mood: {corr:.2f} (p-value: {p_value:.3f}, {significance})"
        except Exception as e:
            logger.error(f"Error calculating correlation: {str(e)}")
        
        # Generate visualizations with Supabase data
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
            # Get from Supabase as dictionary
            date_str = display_date.strftime("%Y-%m-%d") if isinstance(display_date, date) else display_date
            selected_records = get_daily_metrics(user_id, date_str)
            if selected_records and len(selected_records) > 0:
                selected_record = selected_records[0]  # Keep as dictionary
                # Get burnout risk from the record
                burnout_risk = selected_record.get('burnout_current')
                
                # If burnout risk is not available, calculate it
                if burnout_risk is None and selected_record.get('recovery_score') is not None:
                    # Get historical data for accurate burnout calculation
                    burnout_risk = get_burnout_risk_score(selected_record, all_records)
                    
                    # Update record with calculated burnout risk
                    selected_record['burnout_current'] = burnout_risk
                    save_daily_metrics(user_id, selected_record)
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
            token_info = get_whoop_token(user_id)
            # Consider authenticated if we have any token data, even if expired
            # This ensures "connected" status shows even if token needs refresh
            whoop_authenticated = token_info.get("access_token") is not None
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
        print(f"Error in dashboard route: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error loading dashboard: {str(e)}"

@app.route('/input', methods=['GET', 'POST'])
@app.route('/input/<string:input_date>', methods=['GET', 'POST'])
@login_required
def input_mood(input_date=None):
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
                return redirect(url_for('input_mood', input_date=entry_date.strftime("%Y-%m-%d")))
            
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
            else:
                # Save to SQLite
                add_or_update_daily_metrics(metrics_data, mood_data)
            
            flash("Mood rating saved successfully!")
            return redirect(url_for('dashboard', selected_date=date_str))
            
        except ValueError:
            flash("Please enter a valid mood rating (1-10).")
            return redirect(url_for('input_mood', input_date=mood_date.strftime("%Y-%m-%d")))
    
    # For GET request, show the form
    date_str = mood_date.strftime("%Y-%m-%d")
    
    # Get record for the selected date
    if USE_SUPABASE:
        # Get from Supabase
        selected_records = get_daily_metrics(user_id, date_str)
        record = selected_records[0] if selected_records else None
        
        # Convert Supabase record for template compatibility
        if record:
            # Create a compatible object with the same attributes as SQLite model
            class SupabaseRecord:
                def __init__(self, data):
                    # Set default attributes to None
                    # Recovery metrics
                    self.recovery_score = None
                    self.hrv = None
                    self.resting_hr = None
                    self.spo2_percentage = None
                    self.skin_temp_celsius = None
                    
                    # Strain metrics
                    self.strain = None
                    self.max_hr = None
                    self.avg_hr = None
                    self.kilojoules = None
                    
                    # Sleep metrics
                    self.sleep_quality = None
                    self.sleep_consistency = None
                    self.sleep_efficiency = None
                    self.total_sleep_time = None
                    self.deep_sleep_time = None
                    self.rem_sleep_time = None
                    self.respiratory_rate = None
                    
                    # Workout metrics
                    self.workout_count = None
                    self.workout_strain = None
                    
                    # Subjective metrics
                    self.mood_rating = None
                    self.energy_level = None
                    self.stress_level = None
                    self.notes = None
                    
                    # Derived metrics
                    self.burnout_current = None
                    self.burnout_trend = None
                    
                    # Set actual data
                    for key, value in data.items():
                        # Convert date string to date object if needed
                        if key == 'date' and isinstance(value, str):
                            try:
                                setattr(self, key, datetime.strptime(value, "%Y-%m-%d").date())
                            except ValueError:
                                setattr(self, key, value)
                        else:
                            setattr(self, key, value)
            
            record = SupabaseRecord(record)
    else:
        # Get from SQLite
        record = session.query(DailyMetrics).filter_by(date=mood_date).first()
    
    return render_template('input.html', now=datetime.now(), mood_date=mood_date, date_str=date_str, record=record)

@app.route('/delete_mood/<string:selected_date>')
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
            return redirect(url_for('dashboard'))
        
        # Get existing data for the date
        if USE_SUPABASE:
            selected_records = get_daily_metrics(user_id, date_str)
            
            if selected_records and len(selected_records) > 0:
                record = selected_records[0]
                
                # Create updated record without mood data by making a direct PATCH call to Supabase
                # This ensures the mood_rating is set to NULL in the database
                from supabase_client import supabase_client
                
                try:
                    # Direct PATCH request to set mood_rating to null
                    response = supabase_client.table("daily_metrics").update({
                        "mood_rating": None,
                        "notes": None,
                        "updated_at": datetime.now().isoformat()
                    }).eq("user_id", user_id).eq("date", date_str).execute()
                    
                    logger.info(f"Delete mood response: {response}")
                    
                    if len(response.data) == 0:
                        raise Exception("No records were updated")
                        
                except Exception as e:
                    logger.error(f"Error in direct Supabase update: {str(e)}")
                    raise e
                flash("Mood rating deleted successfully.")
            else:
                flash("No mood data found for this date.")
        else:
            # SQLite implementation would go here
            pass
    
    except Exception as e:
        logger.error(f"Error deleting mood: {str(e)}")
        flash(f"Error deleting mood: {str(e)}")
    
    return redirect(url_for('dashboard', selected_date=date_str))

@app.route('/fetch_whoop_data', methods=['POST'])
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
            # Store in Supabase
            save_daily_metrics(user_id, metrics)
            flash(f"Successfully fetched Whoop data for {date_str}")
            logger.info(f"Successfully stored metrics for {date_str}")
        else:
            flash(f"No Whoop data available for {date_str}")
            logger.warning(f"No data available for {date_str}")
        
        # Redirect back to the same date's dashboard
        return redirect(url_for('dashboard', selected_date=date_str))
        
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        flash("Please enter a valid date in YYYY-MM-DD format.")
        return redirect(url_for('dashboard'))
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        flash(f"Error fetching data: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/data')
@login_required
def get_data():
    """
    API endpoint to get all metrics as JSON.
    """
    user_id = get_user_id()
    
    try:
        # Get all metrics from Supabase
        records = get_daily_metrics(user_id)
        
        # Convert dates to strings for JSON serialization
        for r in records:
            if isinstance(r.get('date'), date):
                r['date'] = r['date'].strftime("%Y-%m-%d")
        
        # Return as JSON
        return jsonify(records)
    except Exception as e:
        logger.error(f"Error getting data: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/calendar_data/<string:year>/<string:month>')
@login_required
def calendar_data(year, month):
    """
    API endpoint to get calendar data for a specific month.
    Returns dates with burnout risk data for calendar visualization.
    """
    user_id = get_user_id()
    
    try:
        # Convert to integers
        year = int(year)
        month = int(month)
        
        # Calculate start and end dates for the month
        start_date = date(year, month, 1)
        
        # Calculate the end date (first day of next month)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
            
        # Format dates for Supabase query
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get metrics for date range
        records = get_metrics_range(user_id, start_str, end_str)
        
        # Create calendar data
        calendar_data = []
        for r in records:
            # Determine risk level
            risk_level = None
            burnout_risk = r.get('burnout_current')
            
            if burnout_risk is not None:
                if burnout_risk < 33:
                    risk_level = "low"
                elif burnout_risk < 66:
                    risk_level = "medium"
                else:
                    risk_level = "high"
            
            # Ensure date is in string format
            date_str = r.get('date')
            if isinstance(date_str, date):
                date_str = date_str.strftime("%Y-%m-%d")
            
            # Compile data for this date
            day_data = {
                "date": date_str,
                "has_data": True,
                "risk_level": risk_level,
                "recovery_score": r.get('recovery_score'),
                "mood_rating": r.get('mood_rating'),
                "strain": r.get('strain'),
                "burnout_risk": burnout_risk
            }
            
            calendar_data.append(day_data)
        
        # Return as JSON
        return jsonify(calendar_data)
        
    except Exception as e:
        logger.error(f"Error getting calendar data: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/settings')
@login_required
def settings():
    """
    Settings page for managing user preferences, integrations, and app settings
    """
    user_id = get_user_id()
    
    # Check if the user is connected to WHOOP
    try:
        token_info = get_whoop_token(user_id)
        whoop_authenticated = token_info.get("access_token") is not None
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
    
    # Get AI model preference (default to gpt-4-turbo-preview)
    ai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
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
        appearance_settings=appearance_settings,
        now=datetime.now()
    )

@app.route('/update_openai_key', methods=['POST'])
@login_required
def update_openai_key():
    """
    Update the OpenAI API key in the .env file
    """
    api_key = request.form.get('openai_api_key', '').strip()
    ai_model = request.form.get('ai_model', 'gpt-4-turbo-preview')
    
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
            
            # Also update the insights engine
            from ai_insights import insights_engine
            insights_engine.api_key = api_key
            
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
    
    return redirect(url_for('settings'))

@app.route('/disconnect_whoop', methods=['POST'])
@login_required
def disconnect_whoop():
    """
    Disconnect the user's WHOOP account
    """
    user_id = get_user_id()
    
    try:
        # Remove the token from the database
        # Placeholder: Implement token deletion
        flash("WHOOP account disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting WHOOP: {str(e)}")
        flash(f"Error disconnecting WHOOP: {str(e)}")
    
    return redirect(url_for('settings'))

@app.route('/update_notifications', methods=['POST'])
@login_required
def update_notifications():
    """
    Update notification settings
    """
    # Placeholder for future implementation
    flash("Notification settings updated")
    return redirect(url_for('settings'))

@app.route('/update_appearance', methods=['POST'])
@login_required
def update_appearance():
    """
    Update appearance settings
    """
    # Placeholder for future implementation
    flash("Appearance settings updated")
    return redirect(url_for('settings'))

@app.route('/update_account', methods=['POST'])
@login_required
def update_account():
    """
    Update account settings (password)
    """
    # Placeholder for future implementation
    flash("Account settings updated")
    return redirect(url_for('settings'))

@app.route('/auth')
@login_required
def auth():
    """
    Start the OAuth flow to authorize the app with Whoop.
    """
    # Get the auth URL with the main page as the redirect
    authorization_url, state = get_auth_url()
    # Store the state in the session for later validation
    flask_session['oauth_state'] = state
    # Print the URL for debugging
    print(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)

@app.route('/', methods=['GET'])
def index():
    """
    Main page - redirects to dashboard if logged in, login page if not
    Also handles OAuth callback for Whoop
    """
    # Check if this is a callback from OAuth authorization
    code = request.args.get('code')
    
    if code:
        try:
            # Construct token request payload
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': os.getenv("WHOOP_CLIENT_ID"),
                'client_secret': os.getenv("WHOOP_CLIENT_SECRET")
            }
            
            # Exchange code for token
            response = requests.post(
                "https://api.prod.whoop.com/oauth/oauth2/token", 
                data=token_data
            )
            
            if response.status_code == 200:
                token = response.json()
                
                # Store the token based on storage system
                if USE_SUPABASE:
                    user_id = get_user_id()
                    print(f"Saving Whoop token to Supabase for user: {user_id}")
                    if user_id is not None:
                        save_whoop_token(user_id, token)
                    else:
                        # Fall back to admin user if current user not found
                        admin_id = os.getenv("SUPABASE_USER_ID")
                        print(f"User ID not found, using admin ID: {admin_id}")
                        if admin_id:
                            save_whoop_token(admin_id, token)
                        else:
                            flash("Error: Could not save Whoop token, no valid user ID found")
                else:
                    username = get_user_id() or "default"
                    save_token_to_env(token, username)
                    
                flash("Successfully connected to Whoop!")
            else:
                error_msg = f"Error acquiring token: {response.text}"
                print(error_msg)
                flash(error_msg)
        except Exception as e:
            print(f"Error processing authentication: {str(e)}")
            flash(f"Error processing authentication: {str(e)}")
    
    # Handle error parameters if they exist
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description', '')
        error_msg = f"Authentication error: {error}"
        if error_description:
            error_msg += f" - {error_description}"
        flash(error_msg)
    
    # Check if user is logged in
    if is_authenticated():
        # Redirect to dashboard if logged in
        return redirect(url_for('dashboard'))
    else:
        # Redirect to login page if not logged in
        return redirect(url_for('login'))

# Keep the old callback route for compatibility
@app.route('/callback')
@login_required
def callback():
    """
    Legacy callback handler - redirects to main page with the same parameters
    """
    # Process OAuth callback directly here to avoid extra redirects
    code = request.args.get('code')
    user_id = get_user_id()
    
    if code:
        try:
            # Construct token request payload
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': os.getenv("WHOOP_CLIENT_ID"),
                'client_secret': os.getenv("WHOOP_CLIENT_SECRET")
            }
            
            # Exchange code for token
            response = requests.post(
                "https://api.prod.whoop.com/oauth/oauth2/token", 
                data=token_data
            )
            
            if response.status_code == 200:
                token = response.json()
                # Store the token based on storage system
                if USE_SUPABASE:
                    # Store in Supabase
                    print(f"Saving Whoop token to Supabase for user: {user_id}")
                    if user_id is not None:
                        save_whoop_token(user_id, token)
                    else:
                        # Fall back to admin user if current user not found
                        admin_id = os.getenv("SUPABASE_USER_ID")
                        print(f"User ID not found, using admin ID: {admin_id}")
                        if admin_id:
                            save_whoop_token(admin_id, token)
                        else:
                            flash("Error: Could not save Whoop token, no valid user ID found")
                else:
                    # Store in SQLite
                    username = user_id if isinstance(user_id, str) else "default"
                    save_token_to_env(token, username)
                
                flash("Successfully connected to Whoop!")
            else:
                error_msg = f"Error acquiring token: {response.text}"
                print(error_msg)
                flash(error_msg)
        except Exception as e:
            print(f"Error processing authentication: {str(e)}")
            flash(f"Error processing authentication: {str(e)}")
    
    # Handle error parameters if they exist
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description', '')
        error_msg = f"Authentication error: {error}"
        if error_description:
            error_msg += f" - {error_description}"
        flash(error_msg)
        
    return redirect(url_for('dashboard'))

@app.route('/test')
def test():
    """
    Simple test route to verify Flask is working
    """
    return "Flask is working! The Burnout Predictor app is running."

@app.route('/test_whoop_api')
def test_whoop_api():
    """
    Test the Whoop API connection and display information about the token
    """
    username = "default"
    token_info = get_user_token(username)
    
    html = "<h1>WHOOP API Test</h1>"
    
    # Token information
    html += "<h2>Token Information</h2>"
    html += f"<p>Access Token: {token_info.get('access_token')[:10]}... (truncated)</p>"
    html += f"<p>Refresh Token: {token_info.get('refresh_token')[:10]}... (truncated) if available</p>"
    html += f"<p>Is Valid: {token_info.get('is_valid')}</p>"
    
    # Test API call
    current_date = date.today().strftime("%Y-%m-%d")
    html += f"<h2>Testing API for date: {current_date}</h2>"
    
    # Test Recovery API
    try:
        recovery_data = get_daily_recovery(current_date, username)
        html += "<h3>Recovery API Test:</h3>"
        if recovery_data:
            html += f"<p>Recovery Score: {recovery_data.get('recovery_score')}</p>"
            html += f"<p>HRV: {recovery_data.get('hrv')}</p>"
            html += f"<p>Resting HR: {recovery_data.get('resting_hr')}</p>"
        else:
            html += "<p>No recovery data found.</p>"
    except Exception as e:
        html += f"<p>Error testing recovery API: {str(e)}</p>"
    
    # Test Strain API
    try:
        strain_data = get_daily_strain(current_date, username)
        html += "<h3>Strain API Test:</h3>"
        if strain_data:
            html += f"<p>Strain: {strain_data.get('strain')}</p>"
        else:
            html += "<p>No strain data found.</p>"
    except Exception as e:
        html += f"<p>Error testing strain API: {str(e)}</p>"
    
    # Test Sleep API
    try:
        sleep_data = get_daily_sleep(current_date, username)
        html += "<h3>Sleep API Test:</h3>"
        if sleep_data:
            html += f"<p>Sleep Quality: {sleep_data.get('sleep_quality')}</p>"
        else:
            html += "<p>No sleep data found.</p>"
    except Exception as e:
        html += f"<p>Error testing sleep API: {str(e)}</p>"
    
    # Show available dates in database
    html += "<h2>Data Available in Database</h2>"
    try:
        records = session.query(DailyMetrics).order_by(DailyMetrics.date.desc()).all()
        if records:
            html += "<ul>"
            for record in records[:10]:  # Show last 10 records
                html += f"<li>{record.date.strftime('%Y-%m-%d')}: Recovery={record.recovery_score}, Mood={record.mood_rating}</li>"
            html += "</ul>"
        else:
            html += "<p>No records found in database.</p>"
    except Exception as e:
        html += f"<p>Error getting database records: {str(e)}</p>"
    
    # Add reconnect button
    html += "<h2>Actions</h2>"
    html += f"<p><a href='{url_for('auth')}' class='btn btn-primary'>Re-authenticate with Whoop</a></p>"
    
    return html

@app.route('/ai-insights', methods=['GET', 'POST'])
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
                records_data = get_daily_metrics(user_id)
                
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
        # Get user data from the database (last 30 days)
        records_data = get_daily_metrics(user_id)
        
        # Sort records by date for better analysis
        records = sorted(
            records_data if records_data else [], 
            key=lambda x: x.get('date', ''), 
            reverse=True
        )
        
        if not records:
            flash("No data available for AI analysis.")
            return redirect(url_for('dashboard'))
        
        # Render the page immediately with loading state
        # The insights will be fetched via AJAX after the page loads
        return render_template(
            'ai_insights.html',
            insights=None,  # Set to None to show loading animation
            records=records[:7],  # Show last 7 days of data
            query=query,
            now=datetime.now()
        )
            
    except Exception as e:
        logger.error(f"Error in AI insights route: {str(e)}")
        flash(f"Error accessing your data: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/api/insights', methods=['POST'])
@login_required
def api_insights():
    """
    API endpoint for getting AI insights.
    """
    user_id = get_user_id()
    
    try:
        # Get request data
        data = request.get_json()
        query = data.get('query') if data else None
        
        # Log request
        logger.info(f"Insights API request received with query: {query}")
        
        # Get user data from the database (last 30 days)
        records_data = get_daily_metrics(user_id)
        
        if not records_data:
            logger.warning(f"No data available for user {user_id}")
            
            # Ensure response has success=false flag
            response = {
                "success": False,
                "error": "No data available for analysis",
                "insight": "Please add some health data before requesting insights."
            }
            logger.info(f"Sending API response to frontend: {response}")
            return jsonify(response)
        
        logger.info(f"Retrieved {len(records_data)} records for AI analysis")
        
        # Get insights
        try:
            insights_response = get_burnout_insights(records_data, query)
            
            # Validate response structure - ensure it has the success flag
            if 'success' not in insights_response:
                logger.warning("Missing success flag in insights response, adding...")
                if 'error' in insights_response:
                    insights_response['success'] = False
                else:
                    insights_response['success'] = True
                    
            # Ensure there's always an insight field, even if empty
            if 'insight' not in insights_response:
                insights_response['insight'] = ""
            
            # Log success or failure
            if insights_response.get('success'):
                logger.info(f"Successfully generated insights for user {user_id}")
                insight_preview = insights_response.get('insight', '')[:50] + '...' if insights_response.get('insight') else ''
                logger.debug(f"Insight preview: {insight_preview}")
            else:
                logger.warning(f"Failed to generate insights: {insights_response.get('error')}")
            
            # Debug the response going to the frontend
            logger.info(f"Sending API response to frontend: {insights_response}")
            
            return jsonify(insights_response)
        except Exception as e:
            logger.error(f"Error in get_burnout_insights: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            error_response = {
                "success": False,
                "error": f"Error generating insights: {str(e)}",
                "insight": "An error occurred while generating AI insights. Please try again later."
            }
            logger.info(f"Sending error response to frontend: {error_response}")
            return jsonify(error_response)
        
    except Exception as e:
        logger.error(f"Error in API insights route: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        error_response = {
            "success": False,  # Ensure this has the success flag
            "error": "Internal server error",
            "insight": "Something went wrong while analyzing your data. Please try again later."
        }
        logger.info(f"Sending error response to frontend: {error_response}")
        return jsonify(error_response)

@app.route('/client-auth')
@login_required
def client_auth():
    """
    Get an access token using client credentials (if supported by Whoop).
    """
    try:
        token = get_client_credentials_token()
        username = "default"  # You can use a real username if you have user accounts
        access_token = save_token_to_env(token, username)
        flash("Successfully acquired access token using client credentials!")
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error getting client credentials token: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/generate_test_data')
@app.route('/generate_test_data/<string:start_date>/<string:end_date>')
@login_required
def generate_test_data(start_date=None, end_date=None):
    """
    Generate test data for a range of dates.
    This is ONLY for testing purposes!
    
    Usage:
    - /generate_test_data - Generate data for the last 30 days
    - /generate_test_data/2025-02-01/2025-02-28 - Generate data for specific date range
    """
    try:
        # Handle default date range if not provided
        if not start_date or not end_date:
            end = date.today()
            start = end - timedelta(days=30)
        else:
            # Convert string dates to date objects
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        if start > end:
            return "Error: Start date must be before end date"
        
        # Generate data for each date in the range
        current = start
        results = []
        
        import random
        
        while current <= end:
            # Generate random metrics following WHOOP scales
            recovery = random.randint(30, 95)  # Recovery score (0-100%)
            strain = random.uniform(5.0, 18.0)  # Strain score (0-21 Borg scale)
            hrv = random.uniform(30.0, 120.0)  # Heart Rate Variability (ms)
            rhr = random.uniform(45.0, 70.0)    # Resting Heart Rate (bpm)
            sleep = random.uniform(40.0, 95.0)  # Sleep quality (%)
            
            # Create realistic correlations between metrics
            # Lower recovery scores tend to have lower HRV
            if recovery < 50:
                hrv = random.uniform(25.0, 60.0)
            elif recovery < 70:
                hrv = random.uniform(40.0, 80.0)
            
            # Higher strain tends to impact next day's recovery
            # If previous day had high strain, recovery is likely lower
            if current > start and random.random() < 0.7:
                prev_day = (session.query(DailyMetrics)
                           .filter_by(date=(current - timedelta(days=1)))
                           .first())
                if prev_day and prev_day.strain and prev_day.strain > 15:
                    recovery = recovery * 0.8  # Reduce recovery after high strain day
            
            # Create a test metrics dictionary
            test_data = {
                "date": current.strftime("%Y-%m-%d"),
                "recovery_score": recovery,
                "strain": strain,
                "hrv": hrv,
                "resting_hr": rhr,
                "sleep_quality": sleep
            }
            
            # Add to database
            record = add_or_update_daily_metrics(test_data)
            results.append(f"Added data for {current.strftime('%Y-%m-%d')}")
            
            # Move to next day
            current += timedelta(days=1)
        
        return f"Successfully generated test data for {len(results)} days.<br>" + "<br>".join(results) + f"<br><a href='{url_for('dashboard')}'>Back to Dashboard</a>"
    
    except Exception as e:
        return f"Error generating test data: {str(e)}"

# Global before_request handler to check authentication
@app.before_request
def check_auth():
    """
    Before request handler to check authentication status.
    Redirects to login page for protected routes if not authenticated.
    """
    # Public routes that don't require authentication
    public_routes = ['login', 'signup', 'static', 'index']
    
    # Check if the route is public
    if request.endpoint in public_routes:
        return  # Allow access to public routes
    
    # Check if the route is already decorated with @login_required
    # (Those will handle authentication themselves)
    view_func = app.view_functions.get(request.endpoint)
    if view_func and hasattr(view_func, '_login_required'):
        return  # Let the decorator handle it
    
    # For all other routes, check authentication
    if not is_authenticated():
        # Remember where the user was trying to go
        flask_session['next_url'] = request.url
        flash("Please log in to access this page")
        return redirect(url_for('login'))

# This login_required function is defined at the top of the file

if __name__ == '__main__':
    # Set Flask environment based on environment variable
    is_production = os.getenv("FLASK_ENV") == "production"
    
    # Initialize Supabase tables if in development
    if not is_production:
        try:
            from supabase_client import init_supabase_tables
            init_supabase_tables()
            logger.info("Supabase tables initialized")
        except Exception as e:
            logger.error(f"Error initializing Supabase tables: {str(e)}")
    
    # Run the app with appropriate settings
    if is_production:
        # Production settings - safer defaults
        logger.info("Starting app in production mode")
        app.run(debug=False, port=int(os.getenv("PORT", 3000)))
    else:
        # Development settings
        logger.info("Starting app in development mode")
        app.run(debug=True, host='127.0.0.1', port=3000)