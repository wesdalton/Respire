from app import create_app

app = create_app()

# This allows Vercel to find the Flask app
if __name__ == "__main__":
    app.run()