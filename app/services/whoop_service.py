import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import uuid

# Load environment variables first
load_dotenv()

# Try to import from Supabase client first, falling back to SQLite if not available
try:
    from app.database.supabase import get_whoop_token, save_whoop_token
    USE_SUPABASE = True
    print("Using Supabase for token storage")
except ImportError:
    # Import database functions for SQLite storage
    from app.database.sqlite import get_user_token, save_user_token
    USE_SUPABASE = False
    print("Using SQLite for token storage")

WHOOP_API_BASE = "https://api.prod.whoop.com/developer"
WHOOP_AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI", "http://127.0.0.1:3000/callback")

def get_auth_url():
    """
    Get the authorization URL for the user to authorize the app.
    """
    # Use only the scopes that were approved for your app
    print(f"Using REDIRECT_URI: {REDIRECT_URI}")
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, 
                         scope=["read:recovery", "read:profile", "read:cycles", "read:sleep", 
                                "read:workout", "read:body_measurement"])
    authorization_url, state = oauth.authorization_url(WHOOP_AUTH_URL)
    print(f"Generated auth URL: {authorization_url}")
    return authorization_url, state

def get_token_from_code(authorization_response):
    """
    Exchange the authorization code for an access token.
    """
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    
    # Extract the code from the authorization response
    if "?code=" in authorization_response:
        code = authorization_response.split("?code=")[1].split("&")[0]
        
        # Make a direct request to the token endpoint
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = requests.post(WHOOP_TOKEN_URL, data=token_data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error exchanging code for token: {response.text}")
    else:
        # If there's an error in the response, extract and raise it
        if "error=" in authorization_response:
            error = authorization_response.split("error=")[1].split("&")[0]
            error_description = ""
            if "error_description=" in authorization_response:
                error_description = authorization_response.split("error_description=")[1].split("&")[0]
            raise Exception(f"Authentication error: {error} - {error_description}")
        
        raise Exception("Invalid authorization response")

def get_client_credentials_token():
    """
    Get an access token using client credentials flow (if supported by Whoop).
    """
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url=WHOOP_TOKEN_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    return token

def save_token_to_env(token, username="default"):
    """
    Save the token information to the database.
    This stores the access token, refresh token, and expiration time.
    """
    if USE_SUPABASE:
        # For Supabase, we need a user_id (UUID)
        # In production, you'd get this from the session
        user_id = os.getenv("SUPABASE_USER_ID", str(uuid.uuid4()))
        
        # Store token in Supabase
        access_token = save_whoop_token(user_id, token)
    else:
        # Store token in SQLite database
        access_token = save_user_token(token, username)
    
    # Log saved token info 
    print(f"Token saved for user {username} - Access: {access_token[:10] if access_token else 'None'}..., Expires in: {token.get('expires_in', 0)} seconds")
    
    return access_token

def refresh_access_token(username="default"):
    """
    Refresh the access token using the stored refresh token.
    """
    if USE_SUPABASE:
        # For Supabase, we need a user_id (UUID)
        # In production, you'd get this from the session
        user_id = os.getenv("SUPABASE_USER_ID")
        
        # Get token from Supabase
        token_info = get_whoop_token(user_id)
    else:
        # Get token from SQLite database
        token_info = get_user_token(username)
        
    refresh_token = token_info.get("refresh_token")
    
    if not refresh_token:
        raise Exception("No refresh token available")
    
    token_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(WHOOP_TOKEN_URL, data=token_data)
    if response.status_code == 200:
        token = response.json()
        return save_token_to_env(token, username)
    else:
        raise Exception(f"Error refreshing token: {response.text}")

def is_token_valid(username="default"):
    """
    Check if the current access token is still valid.
    """
    if USE_SUPABASE:
        # For Supabase, we need a user_id (UUID)
        user_id = os.getenv("SUPABASE_USER_ID")
        
        # Get token from Supabase
        token_info = get_whoop_token(user_id)
    else:
        # Get token from SQLite database
        token_info = get_user_token(username)
        
    return token_info.get("is_valid", False)

def get_valid_access_token(username="default"):
    """
    Get a valid access token, refreshing if necessary.
    """
    if USE_SUPABASE:
        # For Supabase, we need a user_id (UUID)
        user_id = os.getenv("SUPABASE_USER_ID")
        
        # Get token from Supabase
        token_info = get_whoop_token(user_id)
    else:
        # Get token from SQLite database
        token_info = get_user_token(username)
        
    print(f"Token info from database: {token_info}")
    
    # First check if we have an unexpired token
    if token_info.get("is_valid"):
        print(f"Using valid token from database")
        return token_info.get("access_token")
    
    # Try to refresh the token if we have a refresh token
    if token_info.get("refresh_token"):
        try:
            print(f"Attempting to refresh token")
            return refresh_access_token(username)
        except Exception as e:
            print(f"Error refreshing token: {e}")
    
    print(f"No valid token available")
    return None

def get_headers(username="default"):
    """
    Return the authorization headers using a valid access token.
    Attempts to refresh the token if it's expired.
    """
    token = get_valid_access_token(username)
    return {"Authorization": f"Bearer {token}"}

def get_daily_recovery(date_str=None, username="default"):
    """
    Get comprehensive recovery data for a specific date.
    If date_str is None, will fetch today's data.
    
    Returns an expanded set of recovery metrics including SPO2 and skin temperature when available.
    """
    if date_str is None:
        date_str = datetime.today().strftime("%Y-%m-%d")
    
    print(f"Fetching recovery data for {date_str}")
    url = f"{WHOOP_API_BASE}/v1/recovery"
    params = {"start": date_str, "end": date_str}
    
    headers = get_headers(username)
    print(f"Using headers: {headers}")
    
    response = requests.get(url, headers=headers, params=params)
    print(f"Recovery API response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Recovery API response: {data}")
        if data.get("records") and len(data["records"]) > 0:
            record = data["records"][0]
            score = record.get("score", {})
            
            result = {
                "recovery_score": score.get("recovery_score"),
                "resting_hr": score.get("resting_heart_rate"),
                "hrv": score.get("hrv_rmssd_milli"),
                "date": date_str
            }
            
            # Add optional WHOOP 4.0 metrics if available
            if "spo2_percentage" in score:
                result["spo2_percentage"] = score.get("spo2_percentage")
            
            if "skin_temp_celsius" in score:
                result["skin_temp_celsius"] = score.get("skin_temp_celsius")
                
            # Additional metadata
            result["user_calibrating"] = score.get("user_calibrating", False)
            
            print(f"Extracted recovery data: {result}")
            return result
    
    print(f"Failed to get recovery data: {response.status_code}, {response.text}")
    return None

def get_daily_strain(date_str=None, username="default"):
    """
    Get comprehensive strain data for a specific date.
    If date_str is None, will fetch today's data.
    
    Returns expanded strain metrics including average heart rate, max heart rate, and kilojoules burned.
    """
    if date_str is None:
        date_str = datetime.today().strftime("%Y-%m-%d")
    
    print(f"Fetching strain data for {date_str}")
    url = f"{WHOOP_API_BASE}/v1/cycle"
    params = {"start": date_str, "end": date_str}
    
    response = requests.get(url, headers=get_headers(username), params=params)
    print(f"Strain API response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Strain API response: {data}")
        if data.get("records") and len(data["records"]) > 0:
            record = data["records"][0]
            score = record.get("score", {})
            
            result = {
                "strain": score.get("strain"),
                "avg_hr": score.get("average_heart_rate"),
                "max_hr": score.get("max_heart_rate"),
                "kilojoules": score.get("kilojoule"),
                "date": date_str
            }
            
            print(f"Extracted strain data: {result}")
            return result
    
    print(f"Failed to get strain data: {response.status_code}, {response.text}")
    return None

def get_daily_sleep(date_str=None, username="default"):
    """
    Get comprehensive sleep data for a specific date.
    If date_str is None, will fetch today's data.
    
    Returns expanded sleep metrics including sleep stages, efficiency, and respiratory rate.
    """
    if date_str is None:
        date_str = datetime.today().strftime("%Y-%m-%d")
    
    print(f"Fetching sleep data for {date_str}")
    url = f"{WHOOP_API_BASE}/v1/sleep"
    params = {"start": date_str, "end": date_str}
    
    response = requests.get(url, headers=get_headers(username), params=params)
    print(f"Sleep API response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Sleep API response: {data}")
        if data.get("records") and len(data["records"]) > 0:
            record = data["records"][0]
            score = record.get("score", {})
            
            # Base sleep metrics
            result = {
                "sleep_quality": score.get("quality_duration_score"),
                "date": date_str
            }
            
            # Add sleep performance and efficiency metrics if available
            if "sleep_performance_percentage" in score:
                result["sleep_performance"] = score.get("sleep_performance_percentage")
                
            if "sleep_consistency_percentage" in score:
                result["sleep_consistency"] = score.get("sleep_consistency_percentage")
                
            if "sleep_efficiency_percentage" in score:
                result["sleep_efficiency"] = score.get("sleep_efficiency_percentage")
                
            # Add respiratory rate if available
            if "respiratory_rate" in score:
                result["respiratory_rate"] = score.get("respiratory_rate")
                
            # Add sleep stage information if available
            if "stage_summary" in score:
                stages = score.get("stage_summary", {})
                
                # Convert milliseconds to minutes for easier interpretation
                if "total_in_bed_time_milli" in stages:
                    result["total_sleep_time"] = stages.get("total_in_bed_time_milli") / 60000
                    
                if "total_slow_wave_sleep_time_milli" in stages:
                    result["deep_sleep_time"] = stages.get("total_slow_wave_sleep_time_milli") / 60000
                    
                if "total_rem_sleep_time_milli" in stages:
                    result["rem_sleep_time"] = stages.get("total_rem_sleep_time_milli") / 60000
            
            print(f"Extracted sleep data: {result}")
            return result
    
    print(f"Failed to get sleep data: {response.status_code}, {response.text}")
    return None

def get_daily_workouts(date_str=None, username="default"):
    """
    Get workout data for a specific date.
    If date_str is None, will fetch today's data.
    
    Returns a dictionary with workout count and accumulated strain from workouts.
    """
    if date_str is None:
        date_str = datetime.today().strftime("%Y-%m-%d")
    
    print(f"Fetching workout data for {date_str}")
    url = f"{WHOOP_API_BASE}/v1/activity/workout"
    
    # Convert date string to datetime for proper formatting
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    start_dt = date_obj.replace(hour=0, minute=0, second=0).isoformat() + "Z"
    end_dt = date_obj.replace(hour=23, minute=59, second=59).isoformat() + "Z"
    
    params = {"start": start_dt, "end": end_dt, "limit": 25}
    
    response = requests.get(url, headers=get_headers(username), params=params)
    print(f"Workout API response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Workout API response: {data}")
        
        workouts = data.get("records", [])
        workout_count = len(workouts)
        
        if workout_count > 0:
            # Calculate total workout strain and other metrics
            total_strain = 0
            total_time = 0
            max_hr_overall = 0
            
            for workout in workouts:
                score = workout.get("score", {})
                if score and "strain" in score:
                    total_strain += score.get("strain", 0)
                if score and "max_heart_rate" in score:
                    max_hr_overall = max(max_hr_overall, score.get("max_heart_rate", 0))
                
                # Calculate duration in minutes
                if workout.get("start") and workout.get("end"):
                    start_time = datetime.fromisoformat(workout["start"].replace("Z", "+00:00"))
                    end_time = datetime.fromisoformat(workout["end"].replace("Z", "+00:00"))
                    duration = (end_time - start_time).total_seconds() / 60
                    total_time += duration
            
            result = {
                "workout_count": workout_count,
                "workout_strain": total_strain,
                "workout_duration": total_time,
                "workout_max_hr": max_hr_overall,
                "date": date_str
            }
            
            print(f"Extracted workout data: {result}")
            return result
        else:
            return {"workout_count": 0, "workout_strain": 0, "date": date_str}
    
    print(f"Failed to get workout data: {response.status_code}, {response.text}")
    return None

def get_all_daily_metrics(date_str=None, username="default"):
    """
    Fetch all metrics (recovery, strain, sleep, workouts) for a specific date.
    Returns a combined dictionary of all available metrics.
    
    This function provides a comprehensive dataset for burnout prediction.
    """
    if date_str is None:
        date_str = datetime.today().strftime("%Y-%m-%d")
    
    recovery_data = get_daily_recovery(date_str, username) or {}
    strain_data = get_daily_strain(date_str, username) or {}
    sleep_data = get_daily_sleep(date_str, username) or {}
    workout_data = get_daily_workouts(date_str, username) or {}
    
    # Combine all metrics into a single dictionary
    combined_data = {"date": date_str}
    combined_data.update({k: v for k, v in recovery_data.items() if k != "date"})
    combined_data.update({k: v for k, v in strain_data.items() if k != "date"})
    combined_data.update({k: v for k, v in sleep_data.items() if k != "date"})
    combined_data.update({k: v for k, v in workout_data.items() if k != "date"})
    
    return combined_data

def fetch_and_store_whoop_data():
    """
    Background task to fetch Whoop data and store it in the database.
    Used by the scheduler to automatically update data daily.
    """
    import os
    import logging
    logger = logging.getLogger(__name__)
    
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
            # Store in database
            if USE_SUPABASE:
                from app.database.supabase import save_daily_metrics
                save_daily_metrics(user_id, metrics)
            else:
                from app.database.sqlite import add_or_update_daily_metrics
                add_or_update_daily_metrics(metrics)
                
            logger.info(f"Successfully updated metrics for {today_str}")
        else:
            logger.warning(f"No metrics data available for {today_str}")
    except Exception as e:
        logger.error(f"Error fetching/storing Whoop data: {str(e)}")


if __name__ == "__main__":
    # Test the API functions
    today = datetime.today().strftime("%Y-%m-%d")
    print(f"Testing API for date: {today}")
    
    metrics = get_all_daily_metrics(today)
    print(f"Daily metrics: {metrics}")