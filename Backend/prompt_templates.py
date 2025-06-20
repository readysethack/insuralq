# prompt_templates.py

# User-facing claim structuring prompt
def get_claim_structuring_prompt():
    return (
        """
        You are an expert insurance assistant. Given a user's claim submission, extract and structure the following fields as JSON:
        - incident_date
        - policy_number
        - claim_text
        - attached_files (list of filenames or URLs)
        
        If any field is missing, set its value to null or an empty list.
        """
    )

# Agent-facing assessment prompt
def get_claim_assessment_prompt():
    return (
        """
        You are an insurance claim assessment expert. Given a structured claim, return:
        - risk_score (1-5, 5=highest risk)
        - missing_info (list of required docs or info not present)
        - recommendation (short reasoning)
        
        Respond as a JSON object with these keys.
        """
    )
