from flask import Flask, Blueprint, request, jsonify
from backend.services.agents import run_agent
from backend.prompt_templates import get_claim_structuring_prompt, get_claim_assessment_prompt
from backend.services.curacel_client import submit_claim_to_curacel
from werkzeug.utils import secure_filename
import os

claims_bp = Blueprint('claims', __name__, url_prefix='/api/claims')

# In-memory store for demo (replace with DB in production)
claims_store = []

@claims_bp.route('', methods=['POST'])
def submit_claim():
    """User submits a new claim"""
    data = request.form.to_dict()
    files = request.files.getlist('files')
    claim_text = data.get('claim_text', '')
    incident_date = data.get('incident_date')
    policy_number = data.get('policy_number')
    file_urls = []
    upload_dir = 'uploads/'
    os.makedirs(upload_dir, exist_ok=True)
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        file_urls.append(filepath)
    # Structure claim using OpenAI agent
    # Use your agent runner for structuring
    try:
        agent_input = f"Claim: {claim_text}\nIncident Date: {incident_date}\nPolicy Number: {policy_number}\nFiles: {file_urls}"
        structured_claim = run_agent(agent_input)
        # If run_agent is async, use asyncio.run(run_agent(...))
        if hasattr(structured_claim, '__await__'):
            import asyncio
            structured_claim = asyncio.run(structured_claim)
    except Exception as e:
        return jsonify({'error': 'Failed to structure claim', 'details': str(e)}), 500
    # Store claim (simulate DB auto-increment id)
    claim_id = len(claims_store) + 1
    structured_claim['id'] = claim_id
    claims_store.append(structured_claim)
    # Send to Curacel API
    curacel_response, status = submit_claim_to_curacel(structured_claim)
    return jsonify({'message': 'Claim submitted', 'claim': structured_claim, 'curacel': curacel_response}), status

@claims_bp.route('', methods=['GET'])
def list_claims():
    """Agent fetches all claims"""
    return jsonify({'claims': claims_store}), 200

@claims_bp.route('/<int:claim_id>/assess', methods=['POST'])
def assess_claim(claim_id):
    """Agent triggers GPT assessment for a claim"""
    claim = next((c for c in claims_store if c['id'] == claim_id), None)
    if not claim:
        return jsonify({'message': 'Claim not found'}), 404
    try:
        agent_input = f"Assess this claim: {claim}"
        assessment = run_agent(agent_input)
        if hasattr(assessment, '__await__'):
            import asyncio
            assessment = asyncio.run(assessment)
    except Exception as e:
        return jsonify({'error': 'Failed to assess claim', 'details': str(e)}), 500
    return jsonify({'assessment': assessment}), 200
