# backend/model.py
import joblib
import pandas as pd
from scraper import extract_amazon_data

model = joblib.load("model.pkl")

def predict_product(url):
    features = extract_amazon_data(url)
    print("Extracted Features:", features)

    # Ensure the column order matches exactly what was used in training
    X = pd.DataFrame([{
        'rating': features['rating'],
        'owner_response': int(features['owner_response']),
        'verified_reviewers': int(features['verified_reviewers']),
        'templated_reviews': int(features['templated_reviews']),
        'review_count': features['review_count']
    }])

    print("📊 Model Input DataFrame:\n", X)

    prediction = model.predict(X)[0]
    return "Fake" if prediction == 1 else "Genuine"
