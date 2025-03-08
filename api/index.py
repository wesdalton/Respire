from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <html>
            <head>
                <title>Burnout Predictor</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        line-height: 1.6;
                    }
                    h1 {
                        color: #333;
                    }
                    .message {
                        background-color: #f8f9fa;
                        border-left: 4px solid #007bff;
                        padding: 15px;
                        margin-bottom: 20px;
                    }
                    .btn {
                        display: inline-block;
                        background-color: #007bff;
                        color: white;
                        padding: 10px 15px;
                        text-decoration: none;
                        border-radius: 4px;
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <h1>Burnout Predictor</h1>
                <div class="message">
                    <p>Welcome to Burnout Predictor! This is a simple placeholder page deployed on Vercel.</p>
                    <p>The full application requires configuration of environment variables for:</p>
                    <ul>
                        <li>WHOOP API integration</li>
                        <li>Supabase database connection</li>
                        <li>OpenAI API access</li>
                    </ul>
                </div>
                <p>To set up the full application, follow the instructions in the README.</p>
                <a href="https://github.com/yourusername/burnout-predictor" class="btn">View on GitHub</a>
            </body>
        </html>
        """
        
        self.wfile.write(html_content.encode())