from flask import Blueprint, request, jsonify
from database import get_db_connection
from datetime import datetime

pharmacy_bp = Blueprint("pharmacy", __name__)

@pharmacy_bp.route("/add-medicine", methods=["POST"])
def add_medicine():

    data = request.get_json()

    medicine_name = data.get("medicine_name")
    quantity = data.get("quantity")
    expiry_date = data.get("expiry_date")
    original_price = data.get("original_price")
    discount_price = data.get("discount_price")

    user_id = data.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get pharmacy_id
    cursor.execute("SELECT pharmacy_id FROM pharmacy WHERE user_id=%s", (user_id,))
    pharmacy = cursor.fetchone()

    if not pharmacy:
        return jsonify({"message": "Pharmacy not found"}), 400

    pharmacy_id = pharmacy[0]

    # Determine status
    today = datetime.today().date()
    exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

    if exp_date < today:
        status = "EXPIRED"
    elif (exp_date - today).days <= 30:
        status = "NEAR_EXPIRY"
    else:
        status = "SAFE"

    cursor.execute("""
INSERT INTO medicines
(pharmacy_id, medicine_name, quantity, expiry_date,
 original_price, discount_price, status)
VALUES (%s,%s,%s,%s,%s,%s,%s)
""", (
    pharmacy_id,
    medicine_name,
    quantity,
    expiry_date,
    original_price,
    discount_price,
    status
))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Medicine added"})


@pharmacy_bp.route("/get-medicines/<int:user_id>")
def get_medicines(user_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT m.*
        FROM medicines m
        JOIN pharmacy p ON m.pharmacy_id = p.pharmacy_id
        WHERE p.user_id=%s
    """, (user_id,))

    medicines = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(medicines)

@pharmacy_bp.route("/delete-medicine/<int:medicine_id>", methods=["DELETE"])
def delete_medicine(medicine_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM medicines WHERE medicine_id=%s", (medicine_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Medicine deleted"})