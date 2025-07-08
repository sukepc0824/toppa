from flask import Flask, request, render_template, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    html = ''
    url = ''
    if request.method == 'POST':
        url = request.form['url']
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            response.encoding = response.apparent_encoding
            html = response.text

            # <base> タグを追加して相対パス対策
            soup = BeautifulSoup(html, 'html.parser')
            base_tag = soup.new_tag('base', href=url)
            if soup.head:
                soup.head.insert(0, base_tag)
            else:
                new_head = soup.new_tag('head')
                new_head.insert(0, base_tag)
                soup.insert(0, new_head)

            # iframeで表示
            with open("templates/index.html", "r", encoding="utf-8") as f:
                base_template = f.read()

            return render_template_string(base_template, url=url, embedded_html=str(soup))

        except Exception as e:
            html = f"<p style='color:red;'>エラー: {e}</p>"
            return render_template_string("""
                <p>{{ html|safe }}</p>
                <a href="/">戻る</a>
            """, html=html)

    # GET時
    return render_template("index.html", url='', embedded_html='')
