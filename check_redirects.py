import requests

jee_link = "https://links.mathongo.com/hFUS"
neet_link = "https://drive.google.com/file/d/1wTR96oFOVvLeH532kWA_-lEuPrG7IoJD/view?usp=sharing"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

print("Checking JEE link...")
resp = requests.get(jee_link, headers=headers, allow_redirects=True, stream=True)
print(f"Final URL: {resp.url}")
print(f"Content-Type: {resp.headers.get('Content-Type')}")

print("\nChecking NEET link...")
resp2 = requests.get(neet_link, headers=headers, allow_redirects=True, stream=True)
print(f"Final URL: {resp2.url}")
print(f"Content-Type: {resp2.headers.get('Content-Type')}")
