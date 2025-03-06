from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session as flask_session
from datetime import date, datetime, timedelta
from database import session, DailyMetrics, add_or_update_daily_metrics, User, Base, engine
from whoop_api import (
    get_all_daily_metrics, get_auth_url, save_token_to_env, 
    get_client_credentials_token, get_valid_access_token, REDIRECT_URI
)
from analysis import compute_correlation, generate_time_series_plot, generate_correlation_plot, get_burnout_risk_score
import os
import requests
import uuid
from functools import wraps
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Try to import Supabase client
try:
    from supabase_client import (
        sign_up, sign_in, sign_out, get_current_user, 
        save_daily_metrics, get_daily_metrics, get_metrics_range,
        save_whoop_token, get_whoop_token
    )
    USE_SUPABASE = True
    print("Using Supabase for authentication and storage")
except ImportError:
    USE_SUPABASE = False
    print("Using SQLite for storage (Supabase client not available)")

load_dotenv()

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
    if USE_SUPABASE:
        # Check Supabase session
        try:
            current_user = get_current_user()
            return current_user is not None
        except:
            return False
    else:
        # Check Flask session
        return 'user_id' in flask_session

def get_user_id():
    """Get the current user ID"""
    if USE_SUPABASE:
        try:
            current_user = get_current_user()
            if current_user:
                return current_user.id
            return None
        except:
            return None
    else:
        return flask_session.get('user_id', "default")

# Scheduler to fetch data daily
scheduler = BackgroundScheduler()

def fetch_and_store_whoop_data():
    """
    Background task to fetch Whoop data and store it in the database.
    """
    today_str = datetime.today().strftime("%Y-%m-%d")
    
    # In a multi-user environment, this would need to iterate through all users
    if USE_SUPABASE:
        # For demo purposes, use admin user from env
        user_id = os.getenv("SUPABASE_USER_ID")
        if not user_id:
            print("No admin user ID set, cannot fetch data")
            return
        
        # Get metrics using Whoop API
        metrics = get_all_daily_metrics(today_str, "default")  # Username doesn't matter here
        
        if metrics:
            # Store in Supabase
            save_daily_metrics(user_id, metrics)
            print(f"Successfully updated metrics for {today_str} in Supabase")
        else:
            print(f"Failed to fetch metrics for {today_str}")
    else:
        # Use SQLite storage
        username = "default"
        metrics = get_all_daily_metrics(today_str, username)
        
        if metrics:
            add_or_update_daily_metrics(metrics)
            print(f"Successfully updated metrics for {today_str} in SQLite")
        else:
            print(f"Failed to fetch metrics for {today_str}")

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
            return render_template('signup.html')
        
        if USE_SUPABASE:
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
                flash(f"Error creating account: {str(e)}")
        else:
            # For SQLite, just generate a user ID and store in session
            user_id = str(uuid.uuid4())
            flask_session['user_id'] = user_id
            flask_session['user_email'] = email
            flash("Account created successfully")
            
            # Redirect to original destination if available
            next_url = flask_session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please provide both email and password")
            return render_template('login.html')
        
        if USE_SUPABASE:
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
                flash(f"Error logging in: {str(e)}")
        else:
            # For SQLite, just generate a user ID and store in session
            # In production, you would validate credentials
            user_id = "default"
            flask_session['user_id'] = user_id
            flask_session['user_email'] = email
            flash("Logged in successfully")
            
            # Redirect to original destination if available
            next_url = flask_session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out the current user"""
    if USE_SUPABASE:
        sign_out(flask_session)
    
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
        
        # Load latest 30 days of data
        if USE_SUPABASE:
            # Get data from Supabase
            records_data = get_daily_metrics(user_id)
            records = records_data[:30] if records_data else []  # Limit to 30 records
        else:
            # Get data from SQLite
            records = session.query(DailyMetrics).order_by(DailyMetrics.date.desc()).limit(30).all()
        
        # Calculate correlation if enough data points
        corr, p_value = compute_correlation()
        corr_text = None
        if corr is not None:
            significance = "significant" if p_value < 0.05 else "not significant"
            corr_text = f"Correlation between recovery and mood: {corr:.2f} (p-value: {p_value:.3f}, {significance})"
        
        # Generate visualizations
        time_series = generate_time_series_plot()
        correlation_plot = generate_correlation_plot()
        
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
        if USE_SUPABASE:
            # Get from Supabase
            date_str = display_date.strftime("%Y-%m-%d")
            selected_records = get_daily_metrics(user_id, date_str)
            selected_record = selected_records[0] if selected_records else None
            
            # Convert Supabase record for template compatibility
            if selected_record:
                # Create a compatible object with the same attributes as SQLite model
                class SupabaseRecord:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                selected_record = SupabaseRecord(selected_record)
        else:
            # Get from SQLite
            selected_record = session.query(DailyMetrics).filter_by(date=display_date).first()
        
        # Use the already calculated burnout risk if available, otherwise calculate it
        burnout_risk = None
        if selected_record:
            if hasattr(selected_record, 'burnout_current') and selected_record.burnout_current is not None:
                burnout_risk = selected_record.burnout_current
            else:
                burnout_risk = get_burnout_risk_score(selected_record)
            
        # Calculate next and previous dates
        next_date = (display_date + timedelta(days=1)).strftime("%Y-%m-%d")
        prev_date = (display_date - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Make previous day always available and next day available up to today
        has_next = display_date < date.today()
        has_prev = True  # Always allow going back to previous days
        
        # Check if authenticated with Whoop
        if USE_SUPABASE:
            # Get from Supabase
            token_info = get_whoop_token(user_id)
            whoop_authenticated = token_info.get("is_valid", False)
        else:
            # Get from SQLite
            username = user_id if isinstance(user_id, str) else "default"
            whoop_authenticated = get_valid_access_token(username) is not None
        
        # Debugging
        print(f"Rendering dashboard for {display_date}, authenticated: {whoop_authenticated}")
        
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
                    for key, value in data.items():
                        setattr(self, key, value)
            
            record = SupabaseRecord(record)
    else:
        # Get from SQLite
        record = session.query(DailyMetrics).filter_by(date=mood_date).first()
    
    return render_template('input.html', now=datetime.now(), mood_date=mood_date, date_str=date_str, record=record)

@app.route('/fetch_whoop_data', methods=['POST'])
@login_required
def manual_fetch_data():
    """
    Manually fetch Whoop data for a specific date or date range.
    """
    date_str = request.form.get("date")
    
    if not date_str:
        date_str = date.today().strftime("%Y-%m-%d")
    
    try:
        # Convert to date object to validate format
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Fetch data using database token
        username = "default"  # You can use a real username if you have user accounts
        print(f"Fetching Whoop data for {date_str}...")
        metrics = get_all_daily_metrics(date_str, username)
        print(f"Retrieved metrics: {metrics}")
        
        if metrics and any(v is not None for k, v in metrics.items() if k != 'date'):
            # Store in database
            record = add_or_update_daily_metrics(metrics)
            flash(f"Successfully fetched Whoop data for {date_str}")
        else:
            flash(f"No Whoop data available for {date_str}")
        
        # Redirect back to the same date's dashboard
        return redirect(url_for('dashboard', selected_date=date_str))
        
    except ValueError:
        flash("Please enter a valid date in YYYY-MM-DD format.")
        return redirect(url_for('dashboard'))

@app.route('/data')
@login_required
def get_data():
    """
    API endpoint to get all metrics as JSON.
    """
    records = session.query(DailyMetrics).order_by(DailyMetrics.date).all()
    
    data = [{
        "date": record.date.strftime("%Y-%m-%d"),
        "recovery_score": record.recovery_score,
        "strain": record.strain,
        "hrv": record.hrv,
        "resting_hr": record.resting_hr,
        "sleep_quality": record.sleep_quality,
        "mood_rating": record.mood_rating,
        "notes": record.notes,
        "burnout_risk": record.burnout_current if record.burnout_current is not None else get_burnout_risk_score(record)
    } for record in records]
    
    return jsonify(data)

@app.route('/calendar_data/<string:year>/<string:month>')
@login_required
def calendar_data(year, month):
    """
    API endpoint to get calendar data for a specific month.
    Returns dates with burnout risk data for calendar visualization.
    """
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
            
        # Query all records for the month
        records = session.query(DailyMetrics).filter(
            DailyMetrics.date >= start_date,
            DailyMetrics.date < end_date
        ).all()
        
        # Process burnout risk for all records first
        for r in records:
            if r.burnout_current is None and r.recovery_score is not None:
                get_burnout_risk_score(r)
        
        # Create calendar data
        calendar_data = []
        for r in records:
            risk_level = None
            if r.burnout_current is not None:
                if r.burnout_current < 33:
                    risk_level = "low"
                elif r.burnout_current < 66:
                    risk_level = "medium"
                else:
                    risk_level = "high"
            
            # Compile data for this date
            day_data = {
                "date": r.date.strftime("%Y-%m-%d"),
                "has_data": True,
                "risk_level": risk_level,
                "recovery_score": r.recovery_score,
                "mood_rating": r.mood_rating,
                "strain": r.strain,
                "burnout_risk": r.burnout_current
            }
            
            calendar_data.append(day_data)
        
        # Return as JSON
        return jsonify(calendar_data)
        
    except Exception as e:
        return jsonify({"error": str(e)})

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
                    if user_id:
                        save_whoop_token(user_id, token)
                else:
                    username = get_user_id() or "default"
                    save_token_to_env(token, username)
                    
                flash("Successfully authenticated with Whoop!")
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
                # Store the token in the database
                username = "default"  # You can use a real username if you have user accounts
                save_token_to_env(token, username)
                flash("Successfully authenticated with Whoop!")
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
    # Ensure the database tables exist
    from database import Base, engine
    Base.metadata.create_all(engine)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=3000)