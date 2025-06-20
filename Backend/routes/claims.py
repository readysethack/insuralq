from flask import Flask
from flask import Blueprint
from backend.services.agents import *

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@claims_bp.route('/list', methods=['GET'])
def get_claims():
    # This is a placeholder for the actual implementation
    return {"message": "List of claims"}, 200
