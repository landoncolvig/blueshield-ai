"""
BlueShield AI Chat Function
Handles scenario chat with Claude API
"""

import json
import os
import functions_framework
from anthropic import Anthropic

client = Anthropic()

def get_scenario_prompt(scenario_type, difficulty, scenario_config, difficulty_modifier):
    """Generate scenario-specific prompt based on type and difficulty."""

    scenario_prompts = {
        # Traffic
        'dui': {
            'situation': 'Officer has pulled over a vehicle for weaving between lanes',
            'subject': 'Adult male, 35-45 years old, has been drinking (4-5 beers over 3 hours)',
            'behavior': 'Nervous, wants to avoid arrest, evasive, trying to talk way out'
        },
        'traffic_warrant': {
            'situation': 'Routine traffic stop, dispatch advises driver has active felony warrant',
            'subject': 'Adult with outstanding warrant for failure to appear',
            'behavior': 'May deny identity, become nervous, attempt to flee, or claim mistaken identity'
        },
        'traffic_drugs': {
            'situation': 'Traffic stop with strong marijuana odor from vehicle',
            'subject': 'Adult with possible drug possession',
            'behavior': 'Nervous, may deny odor, claim medical card, or consent/refuse search'
        },
        'traffic_suspended': {
            'situation': 'Traffic stop, driver cannot produce license',
            'subject': 'Adult driving on suspended license',
            'behavior': 'Claims license at home, may give false name, nervous about discovery'
        },
        # Domestic/Violence
        'domestic': {
            'situation': 'Officer responding to domestic disturbance call - yelling and breaking glass reported',
            'subject': 'Adult male, 30-40 years old, in heated argument with partner',
            'behavior': 'Defensive, claims everything is fine, may try to prevent entry or contact with partner'
        },
        'domestic_weapons': {
            'situation': 'Domestic violence call with weapon (knife) mentioned',
            'subject': 'Adult who threatened partner with weapon',
            'behavior': 'May still be armed, denies weapon, claims self-defense, very defensive'
        },
        'assault': {
            'situation': 'Physical fight in parking lot, one party injured',
            'subject': 'Adult involved in physical altercation',
            'behavior': 'Claims self-defense, blames other party, may be injured or intoxicated'
        },
        'threats': {
            'situation': 'Neighbor threatening another after dispute',
            'subject': 'Adult who made verbal threats',
            'behavior': 'Denies threats or claims they were joking, blames victim for provocation'
        },
        # Property
        'shoplifting': {
            'situation': 'Loss prevention has detained suspect for concealing merchandise',
            'subject': 'Adult, claiming misunderstanding or wrongful detention',
            'behavior': 'May claim innocence, demand to leave, or become confrontational with LP staff'
        },
        'burglary': {
            'situation': 'Silent alarm at closed business, back door forced',
            'subject': 'Possible burglar inside business',
            'behavior': 'May hide, flee, claim to be employee, or surrender'
        },
        'theft': {
            'situation': 'Victim reporting theft from vehicle',
            'subject': 'Victim reporting crime (officer takes report)',
            'behavior': 'Cooperative but may be frustrated, wants action taken'
        },
        'vehicle_theft': {
            'situation': 'Plate reader hit on stolen vehicle, occupied',
            'subject': 'Person driving stolen vehicle',
            'behavior': 'Claims borrowed from friend, denies knowledge, may have false documents'
        },
        # Trespass/Disturbance
        'trespass': {
            'situation': 'Individual refusing to leave private property after being asked by owner/security',
            'subject': 'Adult who may be homeless or intoxicated, has personal belongings on site',
            'behavior': 'May claim right to be there, become argumentative, or plead for time to gather belongings'
        },
        'disturbance': {
            'situation': 'Intoxicated individual causing scene at bar, yelling at patrons, refusing to leave',
            'subject': 'Adult male, heavily intoxicated, aggressive demeanor',
            'behavior': 'Loud, confrontational, may challenge officer authority, unstable on feet'
        },
        'noise': {
            'situation': 'Multiple noise complaints about loud party',
            'subject': 'Party host/resident',
            'behavior': 'May minimize noise level, claim right to party, reluctant to end gathering'
        },
        'loitering': {
            'situation': 'Aggressive panhandler at business entrance',
            'subject': 'Adult panhandler who has been trespassed before',
            'behavior': 'May claim public property, become argumentative, plead for money'
        },
        # Civil
        'civil_property': {
            'situation': 'Neighbors arguing over property line/fence',
            'subject': 'Two neighbors in dispute (civil matter)',
            'behavior': 'Both want officer to take their side, frustrated this is civil matter'
        },
        'civil_custody': {
            'situation': 'Custody exchange dispute, one parent refusing to release child',
            'subject': 'Parent refusing to honor custody order',
            'behavior': 'Claims other parent is dangerous, may cite excuses, very emotional'
        },
        'civil_landlord': {
            'situation': 'Tenant locked out by landlord',
            'subject': 'Tenant and landlord in dispute',
            'behavior': 'Tenant demands entry, landlord claims eviction, both want police action'
        },
        'civil_repo': {
            'situation': 'Vehicle repossession, owner blocking tow truck',
            'subject': 'Vehicle owner trying to prevent repo',
            'behavior': 'Claims payments made, very upset, may obstruct process'
        },
        'civil_business': {
            'situation': 'Customer/business dispute over payment',
            'subject': 'Customer and business owner arguing',
            'behavior': 'Both claim to be right, want officer to resolve civil matter'
        },
        # Mental Health/Welfare
        'mental_crisis': {
            'situation': 'Person in apparent mental health crisis at public location',
            'subject': 'Adult experiencing psychological distress',
            'behavior': 'May be confused, paranoid, delusional, talking to unseen persons'
        },
        'welfare_check': {
            'situation': 'Family requests welfare check on elderly resident',
            'subject': 'Elderly person who may need medical attention',
            'behavior': 'May be incapacitated, confused, refusing help, or just fine'
        },
        'suicide_threat': {
            'situation': 'Person threatened suicide via text messages',
            'subject': 'Adult who made suicidal statements',
            'behavior': 'May deny statements, refuse to speak, be in crisis, may have weapons'
        },
        'intoxicated': {
            'situation': 'Unconscious person on park bench with alcohol bottles',
            'subject': 'Heavily intoxicated adult',
            'behavior': 'May be unresponsive, combative when woken, confused, medical emergency'
        },
        # Other
        'suspicious': {
            'situation': 'Reports of person looking into windows in neighborhood',
            'subject': 'Person in dark clothing with backpack',
            'behavior': 'May claim to be looking for address, lost, visiting friend'
        },
        'alarm': {
            'situation': 'Silent alarm at bank, doors appear secure',
            'subject': 'Unknown - clearing alarm call',
            'behavior': 'Building check, key holder response, may be false alarm or actual crime'
        },
        'harassment': {
            'situation': 'Ex-partner sending threatening messages and showing up at workplace',
            'subject': 'Person being accused of harassment',
            'behavior': 'May claim messages taken out of context, deny harassment, blame victim'
        },
        'stalking': {
            'situation': 'Victim reports being followed for weeks',
            'subject': 'Person accused of stalking',
            'behavior': 'Denies following, claims coincidence, may admit to wanting to talk'
        }
    }

    difficulty_behaviors = {
        'trainee': 'immediately compliant, answers all questions honestly, follows every command without hesitation, very cooperative',
        'easy': 'relatively cooperative when confronted with authority, provides clear answers, follows commands with minimal resistance',
        'medium': 'evasive and tries to talk their way out, requires persistence, may become agitated if pressed but eventually complies',
        'hard': 'resistant and argumentative, challenges authority, may attempt to leave, requires firm command presence',
        'expert': 'hostile and potentially volatile, may attempt to flee or fight, challenges everything, complex legal issues arise'
    }

    scenario_info = scenario_prompts.get(scenario_type, scenario_prompts['dui'])
    difficulty_behavior = difficulty_behaviors.get(difficulty, difficulty_behaviors['medium'])

    return f"""You are an AI training system for law enforcement officers, simulating a realistic scenario.

CURRENT SCENARIO:
- Type: {scenario_config.get('title', 'Unknown')}
- Location: {scenario_config.get('location', 'Unknown')}
- Situation: {scenario_info['situation']}
- Subject: {scenario_info['subject']}

DIFFICULTY LEVEL: {difficulty.upper()}
{difficulty_modifier}

YOUR ROLE - Play the SUBJECT:
- Base behavior: {scenario_info['behavior']}
- Adjusted for difficulty: {difficulty_behavior}
- Respond realistically with short, natural dialogue
- React to officer actions appropriately
- Never break character or acknowledge you're an AI

OFFICER INPUT FORMAT:
The officer's input may include up to three parts:
- [SAYS]: What the officer verbally says to you
- [DOES]: Physical actions the officer takes (shining flashlight, positioning, observing)
- [RADIOS]: Communication with dispatch (you may overhear some of this)

React appropriately to ALL parts of their input. If they shine a light at you, react to that. If they position themselves tactically, notice that.

RESPONSE FORMAT:
Return a JSON object with these fields:
{{
  "subject_response": "What the subject says (in quotes, realistic dialogue)",
  "subject_mood": "calm" | "nervous" | "agitated" | "hostile" | "defeated",
  "subject_action": "Brief description of body language/actions",
  "hint": "Training hint for the officer based on their last action (or null if no hint needed)",
  "new_observations": ["List of new observations the officer would notice based on their actions, or empty array"],
  "evaluation": {{
    "action_taken": "Brief description of what the officer did",
    "legal_basis": "Relevant ARS or legal principle (or null)",
    "assessment": "correct" | "needs_improvement" | "incorrect",
    "note": "Brief explanation"
  }},
  "scenario_complete": false,
  "end_scenario_reason": null
}}

MOOD GUIDELINES:
- "calm": Cooperative, relaxed (rare for DUI suspect)
- "nervous": Fidgety, sweating, avoiding eye contact (default start)
- "agitated": Argumentative, raised voice, defensive
- "hostile": Aggressive, threatening, non-compliant
- "defeated": Resigned, knows they're caught, compliant

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
    scenario_type = data.get('scenario', 'dui')
    difficulty = data.get('difficulty', 'medium')
    scenario_config = data.get('scenario_config', {'title': 'Unknown', 'location': 'Unknown'})
    difficulty_modifier = data.get('difficulty_modifier', '')

    # Generate dynamic prompt based on scenario and difficulty
    system_prompt = get_scenario_prompt(scenario_type, difficulty, scenario_config, difficulty_modifier)

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
        system=system_prompt,
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
        'subject_mood': parsed.get('subject_mood', 'nervous'),
        'subject_action': parsed.get('subject_action', ''),
        'hint': parsed.get('hint'),
        'new_observations': parsed.get('new_observations', []),
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
