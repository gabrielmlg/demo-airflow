import requests
import json

url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-charts"

querystring = {"region":"Brasil","lang":"en","symbol":"MGLU3.SA","interval":"1d","range":"max"}

headers = {
    'x-rapidapi-host': "XXX",
    'x-rapidapi-key': "XXXX"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response["chart"]["result"][0]["timestamp"])

jsonIbovespa = json.loads(response.text)

with open('ibov-MGLU3_5d.json', 'w') as json_file:
    json.dump(jsonIbovespa, json_file)

print(response.text)