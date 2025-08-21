# backend/scraper.py
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def extract_product_title(soup):
    title_tag = soup.select_one("#productTitle")
    return title_tag.get_text(strip=True) if title_tag else "Unknown Product"

def extract_product_image(soup):
    img_tag = soup.select_one("#landingImage")
    return img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

def extract_review_count(soup):
    count_tag = soup.select_one("#acrCustomerReviewText")
    if count_tag:
        count_text = count_tag.get_text(strip=True).split()[0].replace(",", "")
        return int(count_text) if count_text.isdigit() else 0
    return 0

def extract_rating(soup, review_count):
    if review_count == 0:
        return 0.0
    rating_tag = soup.select_one("span[data-asin] i span.a-icon-alt")
    if rating_tag:
        try:
            return float(rating_tag.get_text(strip=True).split()[0])
        except:
            return 0.0
    return 0.0

def extract_top_reviews(soup):
    review_blocks = soup.select(".review-text-content span")
    return [rb.get_text(strip=True) for rb in review_blocks[:5]]

def analyze_reviews(reviews):
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    suspicious_mentions = 0
    burst_detected = False

    for review in reviews:
        analysis = TextBlob(review).sentiment.polarity
        if analysis > 0.1:
            sentiments["positive"] += 1
        elif analysis < -0.1:
            sentiments["negative"] += 1
        else:
            sentiments["neutral"] += 1

        if "great product" in review.lower() or "very good" in review.lower():
            suspicious_mentions += 1

    if len(reviews) >= 5 and sentiments["positive"] >= 4:
        burst_detected = True

    return sentiments, suspicious_mentions, burst_detected

def extract_seller_name(soup):
    seller_tag = soup.select_one("#bylineInfo")
    return seller_tag.get_text(strip=True) if seller_tag else "Unknown Seller"

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

        soup = BeautifulSoup(response.content, "html.parser")

        product_title = extract_product_title(soup)
        product_image = extract_product_image(soup)
        review_count = extract_review_count(soup)
        rating = extract_rating(soup, review_count)
        top_reviews = extract_top_reviews(soup)
        sentiments, suspicious_mentions, burst_detected = analyze_reviews(top_reviews)
        seller_name = extract_seller_name(soup)

        owner_response = False
        verified_reviewers = review_count > 0
        templated_reviews = suspicious_mentions > 2

        return {
            "product_name": product_title,   # fixed key
            "seller_name": seller_name,      # added seller
            "image": product_image,
            "rating": rating,
            "review_count": review_count,
            "owner_response": owner_response,
            "verified_reviewers": verified_reviewers,
            "templated_reviews": templated_reviews,
            "sentiments": sentiments,
            "suspicious_mentions": suspicious_mentions,
            "burst_detected": burst_detected,
        }

    except Exception as e:
        print(f"[ERROR] Failed to extract data: {e}")
        return {
            "product_name": "Unknown Product",  # fixed key
            "seller_name": "Unknown Seller",    # added fallback
            "image": "",
            "rating": 0.0,
            "review_count": 0,
            "owner_response": False,
            "verified_reviewers": False,
            "templated_reviews": True,
            "sentiments": {"positive": 0, "neutral": 0, "negative": 0},
            "suspicious_mentions": 0,
            "burst_detected": False,
        }
