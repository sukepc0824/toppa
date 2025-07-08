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
            <input type="text" name="url" placeholder="https://example.com" size="50" required>
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

        # HTMLでなければそのまま返す（画像・CSS・JSなど）
        if not content_type.startswith('text/html'):
            return Response(resp.content, content_type=content_type)

        soup = BeautifulSoup(resp.text, 'html.parser')

        # 相対パス対応
        base_url = resp.url
        base_tag = soup.new_tag('base', href=base_url)
        if soup.head:
            soup.head.insert(0, base_tag)

        # meta refresh の削除
        for meta in soup.find_all('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'refresh'}):
            meta.decompose()

        # JS 削除（必要に応じて）
        for script in soup.find_all('script'):
            script.decompose()

        # aタグのhrefを書き換え
        for a in soup.find_all('a', href=True):
            original = a['href']
            new_url = urljoin(base_url, original)
            a['href'] = f"/proxy?url={quote(new_url)}"

        html = str(soup)
        return render_template_string(html)

    except Exception as e:
        return f"<p>読み込みエラー: {e}</p><a href='/'>戻る</a>"
