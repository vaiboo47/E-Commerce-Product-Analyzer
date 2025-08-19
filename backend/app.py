# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
from scraper import extract_amazon_data

app = Flask(__name__)
CORS(app)

# Load model
try:
    model = joblib.load("model.pkl")  # adjust path if needed
    print("✅ Model loaded successfully.")
    print("🚀 Starting E-Commerce Product Analyzer backend...")
except Exception as e:
    model = None
    print(f"❌ Failed to load model: {e}")

@app.route("/api/check", methods=["POST"])
def check_product():
    if not model:
        return jsonify({"error": "Model not loaded on server"}), 500

    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Extract product data from Amazon
        features = extract_amazon_data(url)
    except Exception as e:
        return jsonify({"error": f"Failed to extract data from URL: {str(e)}"}), 500

    print("⭐ Rating:", features["rating"])
    print("📝 Review Count:", features["review_count"])
    print("📦 Product Name:", features.get("product_name", "Unknown"))
    print("🏪 Seller Name:", features.get("seller_name", "Unknown"))
    print("Extracted Features:", features)

    # Prepare model input
    input_data = pd.DataFrame([{
        "rating": features["rating"],
        "review_count": features["review_count"],
        "owner_response": features["owner_response"],
        "verified_reviewers": features["verified_reviewers"],
        "templated_reviews": features["templated_reviews"]
    }])

    prediction = model.predict(input_data)[0]

    # --- Heuristic checks ---
    heuristic_override = False
    heuristic_reason = ""

    # Ensure "verified_reviewers" is False if no reviews
    verified_reviewers_pass = False
    if features["review_count"] > 0:
        verified_reviewers_pass = features["verified_reviewers"]

    rules_info = {
        "owner_response": features["owner_response"],
        "verified_reviewers": verified_reviewers_pass,
        "no_templated_reviews": not features["templated_reviews"],
        "review_count_check": features["review_count"] >= 5
    }

    rules_satisfied = sum(rules_info.values())

    # Rule 1: Zero reviews → Fake
    if features["review_count"] == 0:
        prediction = 0
        heuristic_override = True
        heuristic_reason = "Product has 0 reviews"
    # Rule 2: At least 2 of 4 → Genuine
    elif rules_satisfied >= 2:
        prediction = 1
        heuristic_override = True
        heuristic_reason = f"{rules_satisfied} out of 4 trust signals satisfied"

    print(
        "✅ Prediction overridden by heuristic rules:" if heuristic_override else "🤖 Model Prediction used:",
        "Genuine" if prediction == 1 else "Fake"
    )

    # Response for frontend
    return jsonify({
    "product_name": features.get("product_name") or features.get("title", "Unknown Product"),
    "seller_name": features.get("seller_name", "Unknown Seller"),
    "image": features.get("image", ""),  # added so UI can display product image
    "rating": features.get("rating", "N/A"),
    "review_count": features.get("review_count", "N/A"),
    "verified_purchase_percent": features.get("verified_purchase_percent", 0),
    "prediction": int(prediction),
    "label": "Genuine" if prediction == 1 else "Fake",
    "heuristics_passed": rules_satisfied,
    "heuristics_total": len(rules_info),
    "heuristic_override": heuristic_override,
    "heuristic_reason": heuristic_reason,
    "details": {
        "owner_response": features["owner_response"],
        "verified_reviewers": verified_reviewers_pass,
        "templated_reviews": features["templated_reviews"],
        "rating": features["rating"],
        "review_count": features["review_count"]
    }
})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
