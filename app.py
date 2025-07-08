from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>ページビューアー</title>
        <style>
            body {
                font-family: sans-serif;
                padding: 2em;
                text-align: center;
            }
            input[type="text"] {
                width: 60%;
                font-size: 1.2em;
            }
            button {
                font-size: 1.2em;
                padding: 0.4em 1em;
            }
        </style>
    </head>
    <body>
        <h1>URLを入力して表示</h1>
        <form method="POST" action="/view">
            <input type="text" name="url" placeholder="https://example.com" required>
            <button type="submit">表示</button>
        </form>
    </body>
    </html>
    '''

@app.route('/view', methods=['POST'])
def view():
    url = request.form['url']
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = response.apparent_encoding
        final_url = response.url

        soup = BeautifulSoup(response.text, 'html.parser')

        # <base> を挿入して相対パスの画像やCSSを解決
        base_tag = soup.new_tag('base', href=final_url)
        if soup.head:
            soup.head.insert(0, base_tag)
        else:
            head_tag = soup.new_tag('head')
            head_tag.insert(0, base_tag)
            soup.insert(0, head_tag)

        # 不要な<script>などの除去をしたい場合はここで
        html = str(soup)

        # 表示ページはそのHTMLだけを描画（Flaskテンプレートのヘッダーなどなし）
        return render_template_string(html)

    except Exception as e:
        return f"<p>読み込みエラー: {e}</p><a href='/'>戻る</a>"
