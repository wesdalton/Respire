# Burnout Predictor - Project Context for AI Assistants

## Project Overview
The Burnout Predictor is a web application that helps predict and prevent burnout by analyzing WHOOP health data combined with self-reported mood ratings. It leverages AI to provide personalized insights and recommendations based on health patterns.

## Key Features
- **WHOOP API Integration:** Automatically fetches daily health metrics (recovery score, strain, HRV, sleep quality)
- **Mood Tracking:** User interface to log daily mood ratings (1-10) and notes
- **Burnout Risk Algorithm:** Sophisticated algorithm using multiple health metrics
- **Apple-Inspired UI:** Modern, clean design with insights cards and simplified visualizations
- **AI Insights:** Personalized recommendations and analysis using OpenAI
- **Cloud Synchronization:** Secure data storage with Supabase (with SQLite fallback)

## Tech Stack
- **Backend:** Python, Flask (with Blueprint structure)
- **Database:** Supabase (PostgreSQL) with SQLite fallback
- **Authentication:** Supabase Auth
- **Data Analysis:** Pandas, NumPy, SciPy
- **Visualization:** Plotly interactive charts
- **AI/ML:** OpenAI API integration
- **Frontend:** HTML, CSS, JavaScript with Bootstrap 5
- **Design Philosophy:** Apple-inspired minimalist design with clear insights

## Project Structure
```
/Users/wesdalton/Desktop/Burnout/
├── app/                  # Main application package
│   ├── __init__.py       # App factory and configuration
│   ├── api/              # API endpoints
│   ├── auth/             # Authentication
│   ├── core/             # Main routes and functionality
│   ├── database/         # Database access (Supabase & SQLite)
│   ├── services/         # Business logic
│   │   ├── ai_service.py         # OpenAI integration for insights
│   │   ├── analysis_service.py   # Data analysis and visualization
│   │   └── whoop_service.py      # WHOOP API integration
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   └── utils/            # Utility functions and scripts
├── run.py                # Application entry point
└── requirements.txt      # Python dependencies
```

## Key Templates
- **dashboard.html** - Main user interface with health metrics visualization
- **input.html** - Interface for logging daily mood ratings
- **ai_insights.html** - Detailed AI insights page
- **layout.html** - Base template with common elements

## Design Elements
The app follows an Apple-inspired design language with:
- Clean, minimalist card-based interface
- Meaningful insights cards with color-coding (positive, neutral, negative)
- Simplified data visualizations focusing on trends and actionable insights
- Consistent spacing, typography, and visual hierarchy
- Interactive elements with subtle animations

## Common Tasks

### Running the App
```bash
python3 run.py  # Starts development server on http://127.0.0.1:3000
```

### Data Model
Key data entities:
1. **User** - Authenticated user with email/password
2. **DailyMetrics** - Health data for a specific date:
   - recovery_score (0-100)
   - hrv (heart rate variability in ms)
   - resting_hr (beats per minute)
   - strain (0-21 scale) 
   - sleep_quality (0-100)
   - mood_rating (1-10, user-input)
   - notes (text, user-input)
   - burnout_current (calculated risk score 0-100)

### Burnout Risk Calculation
The burnout risk algorithm uses multiple factors:
- Recovery scores (25% weight)
- Mood ratings (30% weight)
- HRV metrics (15% weight)
- Sleep quality (15% weight)
- Strain-recovery balance (15% weight)

### Dashboard Visualization
The dashboard has been redesigned to focus on:
1. Key metrics with trend indicators
2. Simplified, Apple-like charts for health data
3. Burnout risk gauge with actionable recommendations
4. AI-powered insights section
5. Recent history timeline

## Design Philosophy
The application has been specifically redesigned to follow Apple's design principles:
- Focus on clarity and simplicity
- Content-focused design with plenty of white space
- Visual hierarchy that guides users to important information
- Action-oriented recommendations rather than just data visualization
- Accessibility through clear typography and color-coding

## Recent Changes
- Completely redesigned the metrics visualization to be more consumer-friendly
- Added Apple-inspired insight cards to replace complex graphs
- Implemented a more visually appealing burnout risk display
- Enhanced the AI insights section with better styling and clearer information
- Simplified technical visualizations to provide actionable insights

## Common Issues
- Some Jinja2 template expressions may need careful handling of None values
- WHOOP API integration requires OAuth authentication
- Supabase tables sometimes show initialization errors but app functions normally

## Accessibility Considerations
- Color-coding is supplemented with clear text labels
- Status indicators use both icons and text
- Numeric values have clear context and explanations