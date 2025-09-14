# Başlıklar ve kütüphaneler
from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash
import openai
import os
import json
from dotenv import load_dotenv
import fitz  # PDF
from docx import Document
from werkzeug.utils import secure_filename
from app.models import ReviewResult  
from flask_login import current_user, login_required
from app import db
from pytz import timezone
import pandas as pd 
from collections import Counter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

analytics_bp = Blueprint("analytics_bp", __name__, template_folder="templates")

# CSV içeriğini metne çevirme
def extract_text_from_csv(file):
    df = pd.read_csv(file)
    if df.empty:
        return ""
    return "\n".join(df.iloc[:, 0].dropna().astype(str))

# WordCloud için ağırlıklı kelime listesi çıkarımı
def calculate_word_weights(words, top_n=30):
    return Counter(words).most_common(top_n)

# 200 yorum destekleyen GPT çağrısı (50 yorumluk parçalarla)
def gpt_chunked_analysis(reviews):
    all_reviews = reviews[:200]  # hard cap
    chunks = [all_reviews[i:i+50] for i in range(0, len(all_reviews), 50)]

    all_positive = []
    all_negative = []
    total_positive = 0
    total_negative = 0
    for chunk in chunks:
        prompt = f"""
Based on the following hotel customer reviews:
1. Classify each review as Positive or Negative.
2. Extract the most frequent positive and negative keywords.
3. Estimate the hotel's overall score between 0 and 10, and explain it in one sentence.

Reviews:
{chr(10).join(f"- {review}" for review in chunk)}

Return in JSON format like this:
{{
  "summary": {{
    "total_reviews": ...,
    "positive_count": ...,
    "negative_count": ...,
    "positive_percentage": ...,
    "negative_percentage": ...
  }},
  "positive_keywords": [...],
  "negative_keywords": [...],
  "score": 7.8,
  "score_reason": "Clean rooms and helpful staff were appreciated, but noisy environment was a major complaint."
}}
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response["choices"][0]["message"]["content"]
        partial = json.loads(content)

        all_positive.extend(partial.get("positive_keywords", []))
        all_negative.extend(partial.get("negative_keywords", []))
        total_positive += partial["summary"].get("positive_count", 0)
        total_negative += partial["summary"].get("negative_count", 0)

    total_reviews = total_positive + total_negative
    positive_pct = round((total_positive / total_reviews) * 100, 2) if total_reviews else 0
    negative_pct = round((total_negative / total_reviews) * 100, 2) if total_reviews else 0

    summary = {
        "total_reviews": total_reviews,
        "positive_count": total_positive,
        "negative_count": total_negative,
        "positive_percentage": positive_pct,
        "negative_percentage": negative_pct
    }

    result = {
        "summary": summary,
        "positive_keywords": all_positive,
        "negative_keywords": all_negative,
        "score": round((positive_pct / 10), 1),
        "score_reason": "This score is based on the balance of positive and negative feedback."
    }
    return result

@analytics_bp.route("/analytics")
@login_required
def analytics_page():
    return render_template("analytics.html")

@analytics_bp.route("/analytics_result", methods=["POST"])
@login_required
def result():
    reviews_text = request.form.get("reviews", "")
    reviews = [r.strip() for r in reviews_text.split("\n") if r.strip()][:200]

    result_data = gpt_chunked_analysis(reviews)
    result_data["positive_keywords"] = calculate_word_weights(result_data.get("positive_keywords", []))
    result_data["negative_keywords"] = calculate_word_weights(result_data.get("negative_keywords", []))

    try:
        review = ReviewResult(
            user_id=current_user.id,
            total_reviews=result_data["summary"].get("total_reviews", 0),
            positive_count=result_data["summary"].get("positive_count", 0),
            negative_count=result_data["summary"].get("negative_count", 0),
            positive_keywords=", ".join([w for w, _ in result_data["positive_keywords"]]),
            negative_keywords=", ".join([w for w, _ in result_data["negative_keywords"]]),
            score=result_data.get("score", 0.0),
            reason=result_data.get("score_reason", "")
        )
        db.session.add(review)
        db.session.commit()
    except Exception as e:
        print("Failed to save review:", e)

    return render_template("analytics_result.html", result=result_data)

@analytics_bp.route("/upload_file", methods=["POST"])
@login_required
def upload_file():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return "No file uploaded", 400

    filename = secure_filename(uploaded_file.filename)
    ext = filename.rsplit(".", 1)[-1].lower()

    text = ""
    if ext == "pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    elif ext == "docx":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif ext == "csv":
        text = extract_text_from_csv(uploaded_file)
    else:
        return "Unsupported file type", 400

    reviews = [line.strip() for line in text.split("\n") if line.strip()][:200]
    result_data = gpt_chunked_analysis(reviews)
    result_data["positive_keywords"] = calculate_word_weights(result_data.get("positive_keywords", []))
    result_data["negative_keywords"] = calculate_word_weights(result_data.get("negative_keywords", []))

    try:
        review = ReviewResult(
            user_id=current_user.id,
            total_reviews=result_data["summary"].get("total_reviews", 0),
            positive_count=result_data["summary"].get("positive_count", 0),
            negative_count=result_data["summary"].get("negative_count", 0),
            positive_keywords=", ".join([w for w, _ in result_data["positive_keywords"]]),
            negative_keywords=", ".join([w for w, _ in result_data["negative_keywords"]]),
            score=result_data.get("score", 0.0),
            reason=result_data.get("score_reason", "")
        )
        db.session.add(review)
        db.session.commit()
    except Exception as e:
        print("Failed to save review:", e)

    return render_template("analytics_result.html", result=result_data)

@analytics_bp.route("/owner_reviews")
@login_required
def owner_reviews():
    turkey_tz = timezone("Europe/Istanbul")
    results = ReviewResult.query.filter_by(user_id=current_user.id).order_by(ReviewResult.created_at.desc()).all()
    for r in results:
        if r.created_at:
            r.created_at = r.created_at.astimezone(turkey_tz)
    return render_template("owner_reviews.html", results=results)

@analytics_bp.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = ReviewResult.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash("You are not authorized to delete this review.", "danger")
        return redirect(url_for('owner_reviews'))

    db.session.delete(review)
    db.session.commit()
    flash("Review deleted successfully.", "success")
    return redirect(url_for('owner_reviews'))
