from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/view', methods=['POST'])
def view():
    url = request.form['url']
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = response.apparent_encoding

        final_url = response.url
        soup = BeautifulSoup(response.text, 'html.parser')

        # 相対パス解決用 base タグ追加
        base_tag = soup.new_tag('base', href=final_url)
        if soup.head:
            soup.head.insert(0, base_tag)
        else:
            new_head = soup.new_tag('head')
            new_head.insert(0, base_tag)
            soup.insert(0, new_head)

        content = str(soup)
    except Exception as e:
        content = f"<p>読み込みエラー: {e}</p>"

    return render_template("view.html", html=content)
