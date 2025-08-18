# backend/scraper.py
import requests
from bs4 import BeautifulSoup
import re
from textblob import TextBlob
from datetime import datetime

SUSPICIOUS_KEYWORDS = ["fake", "broken", "scam", "poor quality", "cheap quality", "waste of money"]

def extract_product_title(soup):
    title_tag = soup.select_one("#productTitle")
    return title_tag.get_text(strip=True) if title_tag else "Unknown Product"

def extract_product_image(soup):
    img_tag = soup.select_one("#landingImage")
    return img_tag['src'] if img_tag and img_tag.has_attr('src') else ""

def extract_review_count(soup):
    try:
        count_tag = soup.select_one("#acrCustomerReviewText")
        if count_tag:
            text = count_tag.get_text(strip=True)
            count_str = re.sub(r"[^\d]", "", text)
            return int(count_str) if count_str else 0
    except Exception as e:
        print(f"[Review Count Error] {e}")
    return 0

def extract_rating(soup, review_count):
    if review_count == 0:
        return 0.0
    try:
        rating_tags = soup.find_all("span", class_="a-icon-alt")
        for tag in rating_tags:
            text = tag.get_text(strip=True)
            if "out of" in text:
                rating_str = text.split(" out of")[0]
                if rating_str.replace('.', '', 1).isdigit():
                    return float(rating_str)
    except Exception as e:
        print(f"[Rating Error] {e}")
    return 0.0

def extract_top_reviews(soup, limit=10):
    reviews = []
    review_blocks = soup.select(".review-text-content span")
    review_dates = soup.select(".review-date")

    for i in range(min(limit, len(review_blocks))):
        text = review_blocks[i].get_text(strip=True)
        date_text = review_dates[i].get_text(strip=True) if i < len(review_dates) else ""
        reviews.append({"text": text, "date": date_text})
    return reviews

def analyze_reviews(reviews):
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    suspicious_mentions = 0
    dates = []

    for review in reviews:
        blob = TextBlob(review["text"])
        polarity = blob.sentiment.polarity
        if polarity > 0.1:
            sentiments["positive"] += 1
        elif polarity < -0.1:
            sentiments["negative"] += 1
        else:
            sentiments["neutral"] += 1

        if any(kw in review["text"].lower() for kw in SUSPICIOUS_KEYWORDS):
            suspicious_mentions += 1

        if review["date"]:
            try:
                dates.append(datetime.strptime(review["date"], "%d %B %Y"))
            except:
                pass

    # Burst detection
    burst_detected = False
    if dates:
        months = [d.strftime("%Y-%m") for d in dates]
        most_common_month = max(set(months), key=months.count)
        if months.count(most_common_month) > len(months) / 2:
            burst_detected = True

    return sentiments, suspicious_mentions, burst_detected

def extract_amazon_data(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')

        product_title = extract_product_title(soup)
        product_image = extract_product_image(soup)
        review_count = extract_review_count(soup)
        rating = extract_rating(soup, review_count)
        top_reviews = extract_top_reviews(soup)
        sentiments, suspicious_mentions, burst_detected = analyze_reviews(top_reviews)

        owner_response = False
        verified_reviewers = review_count > 0
        templated_reviews = suspicious_mentions > 2

        return {
            "title": product_title,
            "image": product_image,
            "rating": rating,
            "review_count": review_count,
            "owner_response": owner_response,
            "verified_reviewers": verified_reviewers,
            "templated_reviews": templated_reviews,
            "sentiments": sentiments,
            "suspicious_mentions": suspicious_mentions,
            "burst_detected": burst_detected
        }

    except Exception as e:
        print(f"[ERROR] Failed to extract data: {e}")
        return {
            "title": "Unknown",
            "image": "",
            "rating": 0.0,
            "review_count": 0,
            "owner_response": False,
            "verified_reviewers": False,
            "templated_reviews": True,
            "sentiments": {"positive": 0, "neutral": 0, "negative": 0},
            "suspicious_mentions": 0,
            "burst_detected": False
        }
