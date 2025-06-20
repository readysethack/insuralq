import os
from openai import OpenAI
import asyncio
from agents import Agent, Runner, function_tool
from backend.routes.auth import get_current_user

@function_tool
def moderation_tool(input : str) -> bool:
    """Moderation tool to check if input is flagged by OpenAI's moderation API."""
    client = OpenAI()
    responses = client.moderations.create(
        model="omni-moderation-latest",
        input=input, 
    )
    return responses["results"][0]["flagged"] # type: ignore


@function_tool
def get_claim():
    """Returns a list of claims attributed to a user"""
    user = get_current_user()

claim_feature_extraction_agent = Agent(
    name="Claim Extraction Agent",
    instructions=
    """
        You are an expert insurance claim analyzer. Extract structured information from claim texts.

        Extract the following information:
        1. Timeline details (dates, sequence of events)
        2. Damage/loss amounts mentioned
        3. Evidence referenced (photos, reports, witnesses)
        4. Level of detail (specific vs vague descriptions)
        5. Emotional tone and language patterns
        6. Policy-related mentions
        7. Any inconsistencies or contradictions
        8. Urgency indicators

        Format your response as JSON with these keys:
        - timeline
        - amounts
        - evidence
        - detail_level
        - language_tone
        - policy_mentions
        - inconsistencies
        - urgency_indicators

        Additional Information:
        1. Ask for details only if you don't understand the claim. Prompt the user for key feature information if needed.
    """
)

fraud_analysis_agent = Agent(
    name="Fraud Analysis Agent",
    instructions=
    """
        You are an insurance fraud detection expert.

        Check for these specific fraud indicators and provide evidence:

        NARRATIVE CONSISTENCY:
        - Are there contradictory timeline elements?
        - Do story details change or conflict?
        - Are facts inconsistent?

        DETAIL LEVEL:
        - Is the description overly vague?
        - Are there excessive unnecessary details?
        - Are critical details missing?

        SUPPORTING EVIDENCE:
        - Is documentation mentioned or absent?
        - Are there signs of evidence avoidance?
        - Convenient losses of evidence?

        TIMING PATTERNS:
        - Recent policy changes?
        - Suspicious timing of incident?
        - Pattern concerns?

        LANGUAGE PATTERNS:
        - Over-explaining behavior?
        - Defensive language?
        - Rehearsed-sounding responses?

        CLAIM CHARACTERISTICS:
        - Round number amounts?
        - Maximum coverage claims?
        - Multiple recent claims mentioned?

        BEHAVIORAL FLAGS:
        - Pressure for quick settlement?
        - Unusual policy knowledge?
        - Evasive responses?

        For each category, respond with:
        - detected: true/false
        - confidence: 0.0-1.0
        - evidence: specific text or pattern that supports detection
        - explanation: why this indicates potential fraud

        Format as JSON with categories as keys.
    """,
    tools=[

    ]
)

internal_agent = Agent(
    name="Second Opinion Agent", 
    instructions=
    """
        You are a senior insurance fraud analyst. 
        Your job is to evaluate submitted insurance claims for red flags, completeness, and recommend next actions. 
        Be strict, consistent, and return only structured output.

        Format your response in JSON with these keys:
        - verdict
        - 
    """,
    tools = [
        claim_feature_extraction_agent,
        fraud_analysis_agent,
        moderation_tool,
    ] 
)

user_agent = Agent(
    name="Claim Ticket Agent",
    instructions=
    """

    """
)

orchestration_agent = Agent(
    name="Orchestration Agent",
    instructions=
    """
    Handoff to the appropriate agent based on:
    1. Type of the request.
    2. Role of the user (e.g claimant or fraud analyst)
    """,
    tools=[
        internal_agent,
        user_agent,
    ]
)

async def run_agent(input : str):
    runner =  await Runner.run(orchestration_agent, input)
    return runner.final_output