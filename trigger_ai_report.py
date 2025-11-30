import requests
import json

def generate_report():
    url = 'http://localhost:5000/api/ai/market-report'
    data = {
        "market_data": {
            "taiex": 17450,
            "sp500": 4560,
            "nasdaq": 14200,
            "gold": 2040,
            "usdtwd": 31.4
        }
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Report generated successfully!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Failed to generate report: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_report()
