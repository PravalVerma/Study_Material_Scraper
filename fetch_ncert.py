import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://ncert.nic.in/textbook.php?ln=en"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
        html = response.read().decode('utf-8')
        with open('ncert_html.txt', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Saved ncert_html.txt. Length:", len(html))
except urllib.error.URLError as e:
    print(e)
