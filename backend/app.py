from flask import Flask
from database import get_db_connection
from auth_routes import auth_bp

app = Flask(__name__)

# Register authentication routes
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return "Backend is running successfully!"

@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return "Database connection successful!"
    except Exception as e:
        return f"Database error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
