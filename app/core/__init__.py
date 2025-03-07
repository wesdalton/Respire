"""
Core functionality for Burnout Predictor
Includes dashboard, data input, and main user interface
"""

from flask import Blueprint

core_bp = Blueprint('core', __name__)

# Import routes to register them with the blueprint
from . import routes