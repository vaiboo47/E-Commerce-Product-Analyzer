# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
df = pd.read_csv("data/fake_product_reviews_500.csv")
df['review_count'] = df['review_count'].apply(lambda x: min(x, 5000))  # Cap max
X = df[['rating', 'review_count', 'owner_response', 'verified_reviewers', 'templated_reviews']]
y = df['label']  # 0 = Genuine, 1 = Fake

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X, y)

# Save model
joblib.dump(model, 'backend/model.pkl')
print("✅ Model saved to backend/model.pkl")
# Add this to your train_model.py or test separately
print(df['label'].value_counts())
