from flask import Flask, request, Response, redirect, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>プロキシビューア</title></head>
    <body style="font-family:sans-serif;text-align:center;margin-top:4em;">
        <h1>URLを入力して表示</h1>
        <form action="/proxy">
            <input type="text" name="url" placeholder="https://omocoro.jp" size="50" required>
            <button type="submit">表示</button>
        </form>
    </body>
    </html>
    '''

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return redirect('/')

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(target_url, headers=headers, timeout=10)
        resp.encoding = resp.apparent_encoding
        content_type = resp.headers.get('Content-Type', '')

        # HTMLでなければ asset として直接返す
        if not content_type.startswith('text/html'):
            return redirect(f"/asset?url={quote(target_url)}")

        soup = BeautifulSoup(resp.text, 'html.parser')
        base_url = resp.url

        # base タグ挿入（相対パス解決用）
        base_tag = soup.new_tag('base', href=base_url)
        if soup.head:
            soup.head.insert(0, base_tag)

        # <a href>書き換え
        for tag in soup.find_all('a', href=True):
            new_url = urljoin(base_url, tag['href'])
            tag['href'] = f"/proxy?url={quote(new_url)}"

        # <img src> / <script src> / <link href> などを /asset に置換
        for tag in soup.find_all(['img', 'script', 'link'], src=True):
            new_url = urljoin(base_url, tag['src'])
            tag['src'] = f"/asset?url={quote(new_url)}"
        for tag in soup.find_all(['link'], href=True):
            new_url = urljoin(base_url, tag['href'])
            tag['href'] = f"/asset?url={quote(new_url)}"

        # meta refresh 削除
        for meta in soup.find_all('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'refresh'}):
            meta.decompose()

        html = str(soup)
        return render_template_string(html)

    except Exception as e:
        return f"<p>読み込みエラー: {e}</p><a href='/'>戻る</a>"

@app.route('/asset')
def asset():
    url = request.args.get('url')
    if not url:
        return "URLがありません", 400

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10, stream=True)
        return Response(resp.content, content_type=resp.headers.get('Content-Type', 'application/octet-stream'))
    except Exception as e:
        return f"読み込みエラー: {e}", 500
