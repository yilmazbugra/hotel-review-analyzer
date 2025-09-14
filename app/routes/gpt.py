from flask import Blueprint, request, render_template, flash, redirect, url_for
import openai
import requests
from bs4 import BeautifulSoup
import logging
from flask_login import login_required, current_user
from app.models import db, Favorite
from datetime import datetime
import pytz
from app.models import CalendarEvent


# OpenAI API key
openai.api_key = "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"  

# Define GPT Blueprint
gpt = Blueprint('gpt', __name__)

# Review analysis route
@gpt.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    if not url:
        flash('Please enter a valid URL.', 'danger')
        return render_template('user_index.html')

    try:
        # Request page content
        response = requests.get(url)
        if response.status_code != 200:
            flash('There was a problem loading the page. Please try again.', 'danger')
            return render_template('user_index.html')

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract hotel reviews
        review_elements = soup.find_all("div", class_="b99b6ef58f d14152e7c3")
        reviews = [el.text.strip() for el in review_elements if el.text.strip()]
        if not reviews:
            flash('No reviews found to analyze.', 'danger')
            return render_template('user_index.html')
        all_reviews = " ".join(reviews)

        # Extract city name
        location_element = soup.find("div", class_="b99b6ef58f cb4b7a25d9")
        city = location_element.text.strip().split(",")[0] if location_element else "unknown city"

        # Get analysis from OpenAI
        analysis_result = analyze_with_openai(all_reviews)

        # Get location-based tips
        location_recommendation = get_city_recommendation(city)

        # Render analysis page with hotel info
        return render_template('user_analyze.html',
                               analysis=analysis_result,
                               location_recommendation=location_recommendation,
                               hotel_url=url)  # pass url to use in hidden form field

    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        flash('An error occurred during analysis. Please try again.', 'danger')
        return render_template('user_index.html')


def analyze_with_openai(text):
    try:
        prompt = f"""
Based on the following hotel reviews, give me a concise and insightful summary that helps me decide whether staying at this hotel would be a good experience or not. Focus on overall impressions, recurring themes, and what a traveler should expect.

Reviews:
{text}
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes hotel reviews."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"OpenAI API error (reviews): {e}")
        return "An error occurred while analyzing reviews. Please try again."


def get_city_recommendation(city):
    try:
        prompt = f"You're a local travel assistant. Briefly suggest 1–2 must-see places and a famous food someone should try when visiting {city}. Your response must be no more than 3 sentences."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful local travel guide."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"OpenAI API error (city guide): {e}")
        return f"Could not fetch recommendations for {city}."


# Re-show form (optional)
@gpt.route('/form', methods=['GET'])
def analyze_form():
    return render_template('user_index.html')


# Add favorite hotel
@gpt.route('/add_to_favorites', methods=['POST'])
@login_required
def add_to_favorites():
    try:
        turkey_time = datetime.now(pytz.timezone("Europe/Istanbul")) 
        fav = Favorite(
            user_id=current_user.id,
            url=request.form.get('url'),
            analysis=request.form.get('analysis'),
            date_added=turkey_time
        )
        db.session.add(fav)
        db.session.commit()
        flash('Hotel has been added to your favorites!', 'success')
    except Exception as e:
        logging.error(f"Error saving favorite: {e}")
        flash('There was an error adding the hotel to favorites.', 'danger')

    return redirect('/gpt/favorites')



# Show user's favorites
@gpt.route('/favorites')
@login_required
def favorites():
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.date_added.desc()).all()
    return render_template('favorites.html', favorites=user_favorites)


# Remove favorite
@gpt.route('/remove_favorite/<int:fav_id>', methods=['GET'])
@login_required
def remove_favorite(fav_id):
    fav = Favorite.query.get_or_404(fav_id)
    if fav.user_id != current_user.id:
        flash("You don't have permission to remove this favorite.", "danger")
        return redirect('/gpt/favorites')
    db.session.delete(fav)
    db.session.commit()
    flash("Favorite removed successfully.", "success")
    return redirect('/gpt/favorites')

from flask import request, jsonify, render_template
from flask_login import login_required, current_user
from app.models import Favorite
from app import db

@gpt.route('/add_to_plan/<int:fav_id>', methods=['POST'])
@login_required
def add_to_plan(fav_id):
    favorite = Favorite.query.filter_by(id=fav_id, user_id=current_user.id).first()
    if not favorite:
        flash("Favorite not found.", "danger")
        return redirect(url_for('gpt.favorites'))

    # Zaten plans'a eklenmişse tekrar ekleme
    if favorite.order_index is not None:
        flash("Already in your plan!", "info")
        return redirect(url_for('gpt.plans'))

    # En son sıraya ekle
    max_order = db.session.query(db.func.max(Favorite.order_index)).filter(Favorite.user_id == current_user.id).scalar()
    favorite.order_index = (max_order or 0) + 1
    db.session.commit()

    return redirect(url_for('gpt.plans'))

@gpt.route('/remove_from_plan/<int:fav_id>', methods=['POST'])
@login_required
def remove_from_plan(fav_id):
    favorite = Favorite.query.filter_by(id=fav_id, user_id=current_user.id).first()
    if favorite:
        favorite.order_index = None
        db.session.commit()
    return redirect(url_for('gpt.plans'))

@gpt.route('/plans', methods=['GET', 'POST'])
@login_required
def plans():
    if request.method == 'POST':
        try:
            data = request.get_json()
            order_list = data.get('order', [])

            for idx, fav_id in enumerate(order_list):
                favorite = Favorite.query.filter_by(id=fav_id, user_id=current_user.id).first()
                if favorite:
                    favorite.order_index = idx
            db.session.commit()
            return jsonify({"status": "success"})
        except Exception as e:
            logging.error(f"Plan update error: {e}")
            return jsonify({"status": "error"})

    
    favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.order_index).all()
    calendar_events = CalendarEvent.query.filter_by(user_id=current_user.id).all()

    return render_template("plans.html", favorites=favorites, calendar_events=calendar_events)


    
    favorites = Favorite.query.filter(
        Favorite.user_id == current_user.id,
        Favorite.order_index != None
    ).order_by(Favorite.order_index).all()

    return render_template('plans.html', favorites=favorites)

@gpt.route("/save_calendar_event", methods=["POST"])
@login_required
def save_calendar_event():
    data = request.form
    title = data.get("title")
    date = data.get("date")

    if not title or not date:
        return "Missing data", 400

    new_event = CalendarEvent(
        user_id=current_user.id,
        title=title,
        url=data.get("url", ""),  
        start=date
    )
    db.session.add(new_event)
    db.session.commit()

    flash("Plan added to your calendar!", "success")
    return redirect(url_for('gpt.plans'))

from datetime import datetime

@gpt.route("/add_to_calendar", methods=["POST"])
@login_required
def add_to_calendar():
    title = request.form.get("title")
    url = request.form.get("url")
    date_str = request.form.get("date")
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("gpt.plans"))

    event = CalendarEvent(
        user_id=current_user.id,
        title=title,
        url=url,
        start=date  
    )

    db.session.add(event)
    db.session.commit()
    flash("Event added to calendar successfully.", "success")
    return redirect(url_for("gpt.plans"))


@gpt.route('/delete_calendar_event/<int:event_id>', methods=['POST'])
@login_required
def delete_calendar_event(event_id):
    try:
        event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user.id).first()
        if event:
            db.session.delete(event)
            db.session.commit()
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "not_found"})
    except Exception as e:
        print("Error deleting calendar event:", e)
        return jsonify({"status": "error"})












"""
from flask import Blueprint, request, render_template, flash, redirect
import openai
import requests
from bs4 import BeautifulSoup
import logging

# OpenAI API anahtarı
openai.api_key = "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"  # Buraya geçerli API anahtarınızı koyun

# GPT Blueprint'i tanımlayın
gpt = Blueprint('gpt', __name__)

# Analiz formu (user_index.html'de çağrılan ana buton)

@gpt.route('/analyze', methods=['POST'])
def analyze():

    # Formdan gelen linki al
    url = request.form.get('url')
    if not url:
        flash('Lütfen geçerli bir URL girin.', 'danger')
        return render_template('user_index.html')

    try:
        # Booking.com'dan sayfa içeriğini al
        response = requests.get(url)
        if response.status_code != 200:
            flash('Sayfa yüklenirken bir sorun oluştu. Lütfen tekrar deneyin.', 'danger')
            return render_template('user_index.html')

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all("div", class_="b99b6ef58f d14152e7c3")

        # Yorumları çek
        comments = [element.text.strip() for element in elements]
        if not comments:
            flash('Sayfada analiz edilecek yorum bulunamadı.', 'danger')
            return render_template('user_index.html')

        # Tüm yorumları birleştir
        all_comments = " ".join(comments)

        # OpenAI ile yorumları analiz et
        analysis_result = analyze_with_openai(all_comments)

        # Analiz sonucunu user_analyze.html şablonuna gönder
        return render_template('user_analyze.html', analysis=analysis_result)

    except Exception as e:
        logging.error(f"Analiz sırasında hata: {e}")
        flash('Analiz sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'danger')
        return render_template('user_index.html')


def analyze_with_openai(text):
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant analyzing hotel reviews."},
                {"role": "user", "content": f"Analyze the following hotel reviews and provide a summary: {text}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"OpenAI API hatası: {e}")
        return "Yorumları analiz ederken bir hata oluştu. Lütfen tekrar deneyin."

# Analiz sayfasını döndüren GET rotası (isteğe bağlı)
@gpt.route('/form', methods=['GET'])
def analyze_form():
    return render_template('user_index.html')

"""
