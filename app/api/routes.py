"""
API routes for Burnout Predictor
JSON endpoints for data retrieval and AI insights
"""

import logging
from flask import jsonify, request
from datetime import datetime, date

from . import api_bp
from app.auth.utils import get_user_id
from app.auth.routes import login_required
from app.database import USE_SUPABASE

logger = logging.getLogger(__name__)

# Import correct database functions
if USE_SUPABASE:
    from app.database.supabase import get_daily_metrics, get_metrics_range
else:
    from app.database.sqlite import get_all_metrics, get_metrics_date_range

# Import services
from app.services.ai_service import get_burnout_insights

@api_bp.route('/insights', methods=['POST'])
@login_required
def insights():
    """API endpoint for getting AI insights."""
    user_id = get_user_id()
    
    try:
        # Get request data
        data = request.get_json() or {}
        query = data.get('query')
        
        # Log request
        logger.info(f"Insights API request received with query: {query}")
        
        # Get user data from the database
        if USE_SUPABASE:
            records_data = get_daily_metrics(user_id)
        else:
            records_data = get_all_metrics(user_id)
        
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
            "success": False,
            "error": "Internal server error",
            "insight": "Something went wrong while analyzing your data. Please try again later."
        }
        logger.info(f"Sending error response to frontend: {error_response}")
        return jsonify(error_response)

@api_bp.route('/data', methods=['GET'])
@login_required
def get_data():
    """API endpoint to get all metrics as JSON."""
    user_id = get_user_id()
    
    try:
        # Get all metrics from database
        if USE_SUPABASE:
            records = get_daily_metrics(user_id)
        else:
            records = get_all_metrics(user_id)
        
        # Convert dates to strings for JSON serialization
        for r in records:
            if isinstance(r.get('date'), date):
                r['date'] = r['date'].strftime("%Y-%m-%d")
        
        # Return as JSON
        return jsonify(records)
    except Exception as e:
        logger.error(f"Error getting data: {str(e)}")
        return jsonify({"error": str(e)})

@api_bp.route('/calendar_data/<string:year>/<string:month>', methods=['GET'])
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
            
        # Format dates for database query
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Get metrics for date range
        if USE_SUPABASE:
            records = get_metrics_range(user_id, start_str, end_str)
        else:
            records = get_metrics_date_range(user_id, start_str, end_str)
        
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