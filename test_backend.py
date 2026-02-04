import requests

url = "http://127.0.0.1:8000/api/analyze"
files = {
    'resume': ('test.pdf', b'%PDF-1.5 dummy pdf content', 'application/pdf')
}
data = {
    'target_role': 'Java Developer'
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, files=files, data=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
