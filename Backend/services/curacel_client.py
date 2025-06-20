import os
import requests

CURACEL_API_URL = os.getenv('CURACEL_API_URL', 'https://api.curacel.co/grow/v1')
CURACEL_API_KEY = os.getenv('CURACEL_API_KEY')

def submit_claim_to_curacel(structured_claim):
    """Submit a structured claim to Curacel Grow API."""
    url = f"{CURACEL_API_URL}/claims"
    headers = {
        'Authorization': f'Bearer {CURACEL_API_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.post(url, json=structured_claim, headers=headers)
    try:
        response.raise_for_status()
        return response.json(), response.status_code
    except Exception as e:
        return {'error': str(e), 'details': response.text}, response.status_code
