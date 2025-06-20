from flask import Flask
from flask import Blueprint
import dotenv
import os

dotenv.load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
curacel_api_key = os.getenv('CURACEL_BASE_URL')

claims_bp = Blueprint('claims', __name__, '/api/claims')

def get_claims():
    pass