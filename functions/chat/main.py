"""
BlueShield AI Chat Function
Handles scenario chat with Claude API
"""

import json
import os
import functions_framework
from anthropic import Anthropic

client = Anthropic()

SCENARIO_PROMPT = """You are an AI training system for law enforcement officers, simulating a DUI traffic stop scenario.

CURRENT SCENARIO:
- Location: State Route 87, Arizona
- Time: 11:42 PM
- Situation: Officer has pulled over a vehicle for weaving between lanes
- Subject: Adult male, 35-45 years old, has been drinking

YOUR ROLE - Play the SUBJECT (the driver):
- You've had 4-5 beers over the past 3 hours
- You're nervous and want to avoid arrest
- You're not aggressive, but evasive and trying to talk your way out
- Respond realistically - short, defensive responses
- If asked to do field sobriety tests, be reluctant but eventually comply if pressed
- Never break character or acknowledge you're an AI

RESPONSE FORMAT:
Return a JSON object with these fields:
{
  "subject_response": "What the subject says (in quotes, realistic dialogue)",
  "hint": "Training hint for the officer based on their last action (or null if no hint needed)",
  "evaluation": {
    "action_taken": "Brief description of what the officer did",
    "legal_basis": "Relevant ARS or legal principle (or null)",
    "assessment": "correct" | "needs_improvement" | "incorrect",
    "note": "Brief explanation"
  },
  "scenario_complete": false,
  "end_scenario_reason": null
}

Set scenario_complete to true if:
- Officer places subject under arrest
- Officer lets subject go
- 8+ exchanges have occurred

LEGAL FRAMEWORK (Arizona):
- ARS 28-1381: DUI - impaired to slightest degree or BAC >= 0.08
- ARS 28-1321: Implied consent - license suspension for refusal
- ARS 28-1595: Must provide license/registration on request
- Officers need Reasonable Suspicion for detention, Probable Cause for arrest
- SFSTs are voluntary but refusal can be noted
- Observations like slurred speech, bloodshot eyes, odor of alcohol establish RS

Always respond with valid JSON only. No other text."""

DEBRIEF_PROMPT = """You are an AI training evaluator for law enforcement. Based on the following conversation between an officer and a DUI suspect, provide a comprehensive debrief.

CONVERSATION:
{conversation}

Provide a JSON response with:
{{
  "score": 0-100,
  "summary": "2-3 sentence overall assessment",
  "legal_analysis": [
    {{
      "topic": "e.g., Initial Contact",
      "status": "correct" | "needs_improvement" | "incorrect",
      "detail": "What happened and relevant ARS",
      "ars_reference": "e.g., ARS 28-1595"
    }}
  ],
  "recommendations": "Paragraph with specific improvement suggestions",
  "strengths": ["List of things done well"],
  "areas_for_improvement": ["List of areas to work on"]
}}

Be specific, reference actual ARS sections, and be constructive. Respond with valid JSON only."""


@functions_framework.http
def chat(request):
    """Handle chat requests."""
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    try:
        data = request.get_json()
        action = data.get('action', 'chat')

        if action == 'chat':
            return handle_chat(data, headers)
        elif action == 'debrief':
            return handle_debrief(data, headers)
        else:
            return (json.dumps({'error': 'Invalid action'}), 400, headers)

    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, headers)


def handle_chat(data, headers):
    """Process a chat message."""
    messages = data.get('messages', [])
    officer_message = data.get('message', '')
    training_mode = data.get('training_mode', True)

    # Build conversation for Claude
    claude_messages = []

    # Add conversation history
    for msg in messages:
        if msg['role'] == 'officer':
            claude_messages.append({
                'role': 'user',
                'content': f"OFFICER: {msg['content']}"
            })
        elif msg['role'] == 'subject':
            claude_messages.append({
                'role': 'assistant',
                'content': msg['raw_response'] if 'raw_response' in msg else json.dumps({
                    'subject_response': msg['content'],
                    'hint': None,
                    'evaluation': None,
                    'scenario_complete': False
                })
            })

    # Add new officer message
    if officer_message:
        claude_messages.append({
            'role': 'user',
            'content': f"OFFICER: {officer_message}"
        })

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=1024,
        system=SCENARIO_PROMPT,
        messages=claude_messages
    )

    response_text = response.content[0].text

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        parsed = {
            'subject_response': response_text,
            'hint': None,
            'evaluation': None,
            'scenario_complete': False
        }

    # Only include hint if in training mode
    if not training_mode:
        parsed['hint'] = None

    result = {
        'subject_response': parsed.get('subject_response', ''),
        'hint': parsed.get('hint'),
        'evaluation': parsed.get('evaluation'),
        'scenario_complete': parsed.get('scenario_complete', False),
        'raw_response': response_text
    }

    return (json.dumps(result), 200, headers)


def handle_debrief(data, headers):
    """Generate scenario debrief."""
    messages = data.get('messages', [])

    # Format conversation for debrief
    conversation_text = ""
    for msg in messages:
        if msg['role'] == 'system':
            conversation_text += f"[SCENARIO START] {msg['content']}\n\n"
        elif msg['role'] == 'officer':
            conversation_text += f"OFFICER: {msg['content']}\n"
        elif msg['role'] == 'subject':
            conversation_text += f"SUBJECT: {msg['content']}\n"
        if msg.get('evaluation'):
            conversation_text += f"[EVAL: {msg['evaluation']}]\n"
        conversation_text += "\n"

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=2048,
        messages=[{
            'role': 'user',
            'content': DEBRIEF_PROMPT.format(conversation=conversation_text)
        }]
    )

    response_text = response.content[0].text

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        parsed = {
            'score': 75,
            'summary': 'Unable to parse detailed analysis.',
            'legal_analysis': [],
            'recommendations': response_text
        }

    return (json.dumps(parsed), 200, headers)
