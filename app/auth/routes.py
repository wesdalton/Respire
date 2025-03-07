"""
Authentication routes for login, signup and user session management
"""

import os
import logging
from flask import render_template, request, redirect, url_for, flash, session as flask_session
from functools import wraps

from . import auth_bp
from app.auth.utils import is_authenticated, get_user_id
from app.database import USE_SUPABASE

# Set up logger
logger = logging.getLogger(__name__)

# Import the correct database functions based on configuration
if USE_SUPABASE:
    from app.database.supabase import sign_up, sign_in, sign_out, get_current_user
else:
    # SQLite fallback
    # This would need additional implementation for password hashing, etc.
    from app.database.sqlite import create_user, get_user_by_email

# Authentication decorator
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flask_session['next_url'] = request.url
            flash("Please log in to access this page")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    
    # Mark this function as having login required
    decorated_function._login_required = True
    return decorated_function

# Authentication routes
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Register a new user"""
    from datetime import datetime
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please provide both email and password")
            return render_template('signup.html', now=datetime.now())
        
        try:
            if USE_SUPABASE:
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
                    return redirect(url_for('core.dashboard'))
            else:
                # SQLite implementation would go here
                # For production, this would need proper password hashing
                flash("SQLite user creation not implemented in this version")
                
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            flash(f"Error creating account: {str(e)}")
    
    return render_template('signup.html', now=datetime.now())

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user"""
    from datetime import datetime
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please provide both email and password")
            return render_template('login.html', now=datetime.now())
        
        try:
            if USE_SUPABASE:
                response = sign_in(email, password)
                
                # Store user in session
                flask_session['user_id'] = response.user.id
                flask_session['user_email'] = email
                flash("Logged in successfully")
                
                # Redirect to original destination if available
                next_url = flask_session.pop('next_url', None)
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('core.dashboard'))
            else:
                # SQLite implementation would go here
                # For production, this would need proper password verification
                flash("SQLite authentication not implemented in this version")
                
        except Exception as e:
            logger.error(f"Error logging in: {str(e)}")
            flash(f"Error logging in: {str(e)}")
            
            return render_template('login.html', now=datetime.now())
    
    return render_template('login.html', now=datetime.now())

@auth_bp.route('/logout')
def logout():
    """Log out the current user"""
    from datetime import datetime
    
    try:
        if USE_SUPABASE:
            sign_out(flask_session)
    except Exception as e:
        logger.error(f"Error signing out: {str(e)}")
    
    # Clear Flask session
    flask_session.clear()
    
    flash("Logged out successfully")
    return redirect(url_for('auth.login'))