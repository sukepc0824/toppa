from flask import Flask, request, render_template
import requests

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
        except Exception as e:
            html = f"<p style='color:red;'>エラー: {e}</p>"

    return render_template('index.html', url=url, html=html)
