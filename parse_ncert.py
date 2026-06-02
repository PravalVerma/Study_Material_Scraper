import re
import json

with open('ncert_html.txt', 'r', encoding='utf-8') as f:
    html = f.read()

# The JS usually looks like: if(class=="1"){ ... } or similar.
# Let's extract any Javascript arrays. 
# Look for something like new Option("Mathematics", "Mathematics")
options = re.findall(r'new Option\("([^"]+)",\s*"([^"]+)"\)', html)
print(f"Found {len(options)} options via regex.")

# Let's try to extract the entire script block containing "function change()"
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
for i, script in enumerate(scripts):
    if 'function change' in script:
        with open('ncert_script.js', 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"Saved script {i} to ncert_script.js. Length: {len(script)}")
        break
