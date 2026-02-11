from flask import Blueprint, request, jsonify
from database import get_db_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check user credentials
    cursor.execute("""
        SELECT user_id, name, email, role
        FROM users
        WHERE email = %s AND password = %s
    """, (email, password))

    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"message": "Invalid email or password"}), 401

    user_id = user["user_id"]
    role = user["role"]

    # If pharmacy, get pharmacy_id
    if role == "pharmacy":
        cursor.execute("""
            SELECT pharmacy_id
            FROM pharmacy
            WHERE user_id = %s
        """, (user_id,))
        pharmacy_row = cursor.fetchone()

        conn.close()

        return jsonify({
            "message": "Login successful",
            "role": "pharmacy",
            "user_id": user_id,
            "pharmacy_id": pharmacy_row["pharmacy_id"]
        })

    # If NGO, get ngo_id
    else:
        cursor.execute("""
            SELECT ngo_id
            FROM ngo
            WHERE user_id = %s
        """, (user_id,))
        ngo_row = cursor.fetchone()

        conn.close()

        return jsonify({
            "message": "Login successful",
            "role": "ngo",
            "user_id": user_id,
            "ngo_id": ngo_row["ngo_id"]
        })
