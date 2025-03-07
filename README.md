# Burnout Predictor

A sophisticated web application that helps predict and prevent burnout by analyzing your WHOOP health data combined with self-reported mood ratings. It leverages AI to provide personalized insights and recommendations based on your unique health patterns.

## Features

- **WHOOP API Integration:** Automatically fetches daily health metrics (recovery score, strain, HRV, sleep quality)
- **Mood Tracking:** Simple and intuitive interface to log daily mood and notes
- **Advanced Analytics:** Sophisticated burnout risk algorithm using multiple health metrics
- **Data Visualization:** Interactive charts showing trends and correlations over time
- **AI-Powered Insights:** Personalized recommendations and analysis using OpenAI
- **Modern Dashboard:** Clean, visually appealing interface optimized for usability
- **Multi-device Support:** Responsive design works on desktop and mobile
- **Cloud Synchronization:** Secure data storage with Supabase (with SQLite fallback)

## Technology Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** Supabase (PostgreSQL) with SQLite fallback
- **API:** RESTful architecture with JSON endpoints
- **Authentication:** Secure user login via Supabase Auth
- **Data Analysis:** Pandas, NumPy, SciPy
- **Visualization:** Plotly interactive charts
- **AI/ML:** OpenAI API integration
- **Frontend:** HTML, CSS, JavaScript with Bootstrap 5

## Installation

### Prerequisites

- Python 3.8 or higher
- WHOOP account and API credentials
- Supabase account (recommended)
- OpenAI API key (for AI insights)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/burnout-predictor.git
   cd burnout-predictor
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp example.env .env
   # Edit .env file with your credentials
   ```

4. **Initialize the database**
   ```bash
   # If using Supabase (recommended)
   python -m app.database.supabase
   
   # Or create a test account with sample data
   python create_test_account.py
   ```

### Running the Application

**Development mode**
```bash
python run.py
```

**Production mode**
```bash
gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT
```

Access the application at http://localhost:3000

## Project Structure

```
burnout-predictor/
├── app/                  # Application package
│   ├── __init__.py       # App factory and configuration
│   ├── auth/             # Authentication
│   ├── api/              # API endpoints
│   ├── core/             # Main functionality
│   ├── database/         # Database access
│   ├── services/         # Business logic
│   ├── static/           # Assets (CSS, JS, images)
│   ├── templates/        # HTML templates
│   └── utils/            # Common utilities
├── tests/                # Test suite
├── .env                  # Environment variables (create from example.env)
├── example.env           # Example environment file
├── requirements.txt      # Python dependencies
├── run.py                # Application entry point
└── README.md             # Documentation
```

## WHOOP API Setup

1. Create a developer account at [WHOOP Developer Portal](https://developer.whoop.com/)
2. Register a new application
3. Set your redirect URI to `http://localhost:3000/` (development) or your production URL
4. Add your client ID and secret to the `.env` file

## Supabase Setup

Refer to [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed instructions on setting up your Supabase project.

## OpenAI Setup

1. Create an account at [OpenAI](https://platform.openai.com/)
2. Generate an API key
3. Add the key to your `.env` file as `OPENAI_API_KEY`

## Usage Guide

1. **Account Setup**
   - Sign up for an account
   - Connect your WHOOP account via OAuth

2. **Daily Usage**
   - View your health metrics dashboard
   - Log your daily mood (1-10 scale)
   - Check your burnout risk score

3. **Analysis**
   - Explore trend charts
   - View correlations between metrics
   - Get AI-powered insights and recommendations

4. **Settings**
   - Configure integrations
   - Manage notification preferences
   - Update AI model settings

## Data Privacy & Security

- All data is encrypted in transit and at rest
- Supabase provides enterprise-grade security for cloud storage
- Local SQLite option available for complete privacy
- OpenAI API calls follow strict data minimization principles
- No third-party analytics or tracking

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- WHOOP for providing the health metrics API
- Supabase for the excellent database platform
- OpenAI for the AI insights technology
- All contributors who have helped build this application