from flask import Blueprint, request, render_template, flash, redirect
import openai
import requests
from bs4 import BeautifulSoup
import logging

# OpenAI API anahtarı
openai.api_key = "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"  # Buraya geçerli API anahtarınızı koyun

# GPT Blueprint'i tanımlayın
gpt_owner = Blueprint('gpt_owner', __name__)

# Analiz formu (owner_index.html'de çağrılan ana buton)
@gpt_owner.route('/owner_analyze', methods=['POST'])
def analyze():
    """
    Kullanıcı tarafından gönderilen linki analiz eder ve sonuçları döndürür.
    """
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
            return render_template('owner_index.html')

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all("div", class_="b99b6ef58f d14152e7c3")

        # Yorumları çek
        comments = [element.text.strip() for element in elements]
        if not comments:
            flash('No reviews found to analyze.', 'danger')
            return render_template('owner_index.html')

        # Tüm yorumları birleştir
        all_comments = " ".join(comments)

        # OpenAI ile yorumları analiz et
        analysis_result = analyze_with_openai(all_comments)

        # Analiz sonucunu owner_analyze.html şablonuna gönder
        return render_template('owner_analyze.html', analysis=analysis_result, url=url)

    except Exception as e:
        logging.error(f"Analiz sırasında hata: {e}")
        flash('Analiz sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'danger')
        return render_template('owner_index.html')


def analyze_with_openai(text):
    """
   Analyzes comments with OpenAI GPT. 
   Returns summary and recommendations separately.
    """
    try:
        prompt = f"""
Analyze the following hotel customer reviews:
1. Write a short summary (positive/negative attributes).
2. Provide 4 suggestions to improve the service.

Yorumlar:
{text}

Return only in this JSON format:
{{
  "summary": "...",
  "suggestions": [
    "Suggestion 1.",
    "Suggestion 2.",
    "Suggestion 3."
  ]
}}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response['choices'][0]['message']['content']

        # JSON formatı gibi gelen metni gerçekten parse edelim
        import json, re
        json_str = re.search(r'\{.*\}', content, re.DOTALL).group()
        return json.loads(json_str)

    except Exception as e:
        logging.error(f"OpenAI analiz hatası: {e}")
        return {
            "summary": "Özet oluşturulamadı.",
            "suggestions": "Öneriler oluşturulamadı."
        }


# Analiz sayfasını döndüren GET rotası (isteğe bağlı)
@gpt_owner.route('/form', methods=['GET'])
def analyze_form():
    return render_template('owner_index.html')




