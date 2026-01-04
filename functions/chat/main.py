"""
BlueShield AI Chat Function
Handles scenario chat with Claude API

Optimizations:
- Module-level constants for scenario data (no recreation per request)
- Haiku model for chat (faster, cheaper), Sonnet for debrief
- Reduced max_tokens for chat responses
- JSON prefilling for reliable output
- Temperature setting for natural responses
"""

import json
import re
import functions_framework
from anthropic import Anthropic

# Initialize client once at module level
client = Anthropic()

# CORS headers as constant
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

# Scenario prompts as module-level constant (not recreated per request)
SCENARIO_PROMPTS = {
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

DIFFICULTY_BEHAVIORS = {
    'trainee': 'immediately compliant, answers all questions honestly, follows every command without hesitation, very cooperative',
    'easy': 'relatively cooperative when confronted with authority, provides clear answers, follows commands with minimal resistance',
    'medium': 'evasive and tries to talk their way out, requires persistence, may become agitated if pressed but eventually complies',
    'hard': 'resistant and argumentative, challenges authority, may attempt to leave, requires firm command presence',
    'expert': 'hostile and potentially volatile, may attempt to flee or fight, challenges everything, complex legal issues arise'
}

VALID_DIFFICULTIES = {'trainee', 'easy', 'medium', 'hard', 'expert'}

DEBRIEF_PROMPT = """You are a STRICT law enforcement training evaluator. Evaluate the officer's SCENARIO PERFORMANCE based on what they actually did during the contact.

CONVERSATION:
{conversation}

SCENARIO SCORING (0-100 points):

OFFICER SAFETY (0-15 pts): Positioning, watching hands, backup
LEGAL PROCEDURE (0-25 pts): ID self, state reason, request documents, articulate RS/PC, Miranda
INVESTIGATION (0-25 pts): Questions, statements, observations, evidence, dispatch
COMMUNICATION (0-20 pts): Professional language, de-escalation, commands, control
RESOLUTION (0-15 pts): Enforcement decision, documentation, proper procedures

SCORING GUIDANCE:
- 0-20: Did nothing or ended immediately
- 20-40: Minimal interaction, no real procedure
- 40-60: Attempted investigation but missed key steps
- 60-80: Did most things correctly with some issues
- 80-100: Exceptional performance

Respond with valid JSON only:"""


def get_scenario_prompt(scenario_type, difficulty, scenario_config, difficulty_modifier):
    """Generate scenario-specific prompt based on type and difficulty."""
    scenario_info = SCENARIO_PROMPTS.get(scenario_type, SCENARIO_PROMPTS['dui'])
    difficulty_behavior = DIFFICULTY_BEHAVIORS.get(difficulty, DIFFICULTY_BEHAVIORS['medium'])

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
- [BACKUP DOES]: Actions taken by the backup officer on scene
- [BACKUP SAYS]: What the backup officer says

React appropriately to ALL parts of their input including backup officer actions.

RESPONSE FORMAT - Return valid JSON only:
{{
  "subject_response": "What the subject says (realistic dialogue)",
  "subject_mood": "calm" | "nervous" | "agitated" | "hostile" | "defeated",
  "subject_action": "Brief body language/actions",
  "hint": "Training hint or null",
  "new_observations": [],
  "evaluation": {{"action_taken": "", "legal_basis": null, "assessment": "correct", "note": ""}},
  "scenario_complete": false,
  "end_scenario_reason": null
}}

MOOD GUIDELINES:
- "calm": Cooperative, relaxed
- "nervous": Fidgety, sweating, avoiding eye contact
- "agitated": Argumentative, raised voice, defensive
- "hostile": Aggressive, threatening, non-compliant
- "defeated": Resigned, knows they're caught, compliant

Set scenario_complete to true if officer arrests subject, lets them go, or 8+ exchanges occurred.

LEGAL FRAMEWORK (Arizona):
- ARS 28-1381: DUI - impaired to slightest degree or BAC >= 0.08
- ARS 28-1321: Implied consent - license suspension for refusal
- ARS 28-1595: Must provide license/registration on request
- Officers need Reasonable Suspicion for detention, Probable Cause for arrest
- SFSTs are voluntary but refusal can be noted"""


@functions_framework.http
def chat(request):
    """Handle chat requests."""
    if request.method == 'OPTIONS':
        return ('', 204, CORS_HEADERS)

    try:
        data = request.get_json()
        if not data:
            return (json.dumps({'error': 'No JSON data provided'}), 400, CORS_HEADERS)

        action = data.get('action', 'chat')

        if action == 'chat':
            return handle_chat(data)
        elif action == 'debrief':
            return handle_debrief(data)
        else:
            return (json.dumps({'error': 'Invalid action'}), 400, CORS_HEADERS)

    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, CORS_HEADERS)


def handle_chat(data):
    """Process a chat message."""
    messages = data.get('messages', [])
    officer_message = data.get('message', '')
    training_mode = data.get('training_mode', True)
    scenario_type = data.get('scenario', 'dui')
    difficulty = data.get('difficulty', 'medium')
    scenario_config = data.get('scenario_config', {'title': 'Unknown', 'location': 'Unknown'})
    difficulty_modifier = data.get('difficulty_modifier', '')

    # Validate difficulty
    if difficulty not in VALID_DIFFICULTIES:
        difficulty = 'medium'

    # Validate scenario_type
    if scenario_type not in SCENARIO_PROMPTS:
        scenario_type = 'dui'

    # Generate dynamic prompt based on scenario and difficulty
    system_prompt = get_scenario_prompt(scenario_type, difficulty, scenario_config, difficulty_modifier)

    # Build conversation for Claude - only include essential data
    claude_messages = []
    for msg in messages:
        if msg['role'] == 'officer':
            claude_messages.append({
                'role': 'user',
                'content': f"OFFICER: {msg['content']}"
            })
        elif msg['role'] == 'subject':
            # Only send the raw response, not reconstructed JSON
            claude_messages.append({
                'role': 'assistant',
                'content': msg.get('raw_response', json.dumps({
                    'subject_response': msg['content'],
                    'subject_mood': 'nervous',
                    'scenario_complete': False
                }))
            })

    # Add new officer message
    if officer_message:
        claude_messages.append({
            'role': 'user',
            'content': f"OFFICER: {officer_message}"
        })

    # Use Haiku for faster, cheaper chat responses
    # Add prefill to ensure JSON output
    claude_messages.append({
        'role': 'assistant',
        'content': '{'
    })

    response = client.messages.create(
        model='claude-haiku-4-20250414',  # Haiku is 10x faster/cheaper for chat
        max_tokens=512,  # Reduced from 1024 - responses are short
        temperature=0.7,  # Slightly higher for more natural roleplay
        system=system_prompt,
        messages=claude_messages
    )

    # Reconstruct full JSON (we prefilled with '{')
    response_text = '{' + response.content[0].text

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to fix common JSON issues
        try:
            # Sometimes response has trailing text after JSON
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                parsed = json.loads(json_match.group(0))
            else:
                raise ValueError("No JSON found")
        except:
            parsed = {
                'subject_response': response_text,
                'subject_mood': 'nervous',
                'subject_action': '',
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

    return (json.dumps(result), 200, CORS_HEADERS)


def handle_debrief(data):
    """Generate scenario debrief."""
    messages = data.get('messages', [])

    # Format conversation for debrief - more concise
    conversation_parts = []
    for msg in messages:
        if msg['role'] == 'system':
            conversation_parts.append(f"[SCENARIO] {msg['content']}")
        elif msg['role'] == 'officer':
            conversation_parts.append(f"OFFICER: {msg['content']}")
        elif msg['role'] == 'subject':
            conversation_parts.append(f"SUBJECT: {msg['content']}")

    conversation_text = "\n".join(conversation_parts)

    # Use Sonnet for debrief (more complex analysis needed)
    # Prefill JSON for reliable output
    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=1536,  # Reduced from 2048
        temperature=0.3,  # Lower for more consistent scoring
        messages=[
            {
                'role': 'user',
                'content': DEBRIEF_PROMPT.format(conversation=conversation_text)
            },
            {
                'role': 'assistant',
                'content': '{"overall_score":'
            }
        ]
    )

    # Reconstruct JSON with prefill
    response_text = '{"overall_score":' + response.content[0].text

    # Try to parse JSON
    parsed = None
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    if not parsed:
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

    # Try finding JSON object in text
    if not parsed:
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

    # Fallback
    if not parsed:
        parsed = {
            'overall_score': 0,
            'scenario_score': 0,
            'scenario_summary': 'Unable to parse response.',
            'scenario_analysis': [],
            'scenario_strengths': [],
            'scenario_improvements': ['Complete the scenario with more interactions'],
            'report_score': 0,
            'report_summary': 'Report not evaluated.',
            'report_analysis': [],
            'recommendations': 'Try the scenario again.'
        }

    return (json.dumps(parsed), 200, CORS_HEADERS)
