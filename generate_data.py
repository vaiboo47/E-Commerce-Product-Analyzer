import pandas as pd
import random

def generate_synthetic_dataset(n=500):
    data = []
    for _ in range(n):
        label = random.choices([0, 1], weights=[0.5, 0.5])[0]  # 0 = genuine, 1 = fake

        if label == 0:  # Genuine
            rating = round(random.uniform(3.5, 5.0), 1)
            review_count = random.randint(100, 5000)
            owner_response = random.choices([1, 0], weights=[0.7, 0.3])[0]
            verified_reviewers = random.choices([1, 0], weights=[0.9, 0.1])[0]
            templated_reviews = random.choices([0, 1], weights=[0.85, 0.15])[0]
        else:  # Fake
            rating = round(random.uniform(1.0, 4.0), 1)
            review_count = random.randint(0, 500)
            owner_response = random.choices([0, 1], weights=[0.8, 0.2])[0]
            verified_reviewers = random.choices([0, 1], weights=[0.7, 0.3])[0]
            templated_reviews = random.choices([1, 0], weights=[0.8, 0.2])[0]

        data.append({
            "rating": rating,
            "review_count": review_count,
            "owner_response": owner_response,
            "verified_reviewers": verified_reviewers,
            "templated_reviews": templated_reviews,
            "label": label
        })

    df = pd.DataFrame(data)
    df.to_csv("data/fake_product_reviews_500.csv", index=False)
    print("✅ Dataset generated and saved to: data/fake_product_reviews_500.csv")

if __name__ == "__main__":
    generate_synthetic_dataset()
