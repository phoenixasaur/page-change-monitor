import requests

URL = "https://api.bigcartel.com/carnaldish/products.json"

response = requests.get(URL)

print(response.status_code)
print(response.text[:500])
