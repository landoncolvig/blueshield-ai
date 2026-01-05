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
        'subject': 'Adult male (v1), 30-40 years old, in heated argument with partner (v2, female, 25-35)',
        'behavior': 'Defensive, claims everything is fine, may try to prevent entry or contact with partner',
        'additional_subjects': {
            'v2': {
                'description': 'Female partner, 25-35 years old, visible injury (bruise on cheek)',
                'behavior': 'Scared, may minimize incident, protective of children if present, cooperative with backup officer'
            }
        }
    },
    'domestic_weapons': {
        'situation': 'Domestic violence call with weapon (knife) mentioned',
        'subject': 'Adult male (v1) who threatened partner with weapon, partner (v2, female) called 911',
        'behavior': 'May still be armed, denies weapon, claims self-defense, very defensive',
        'additional_subjects': {
            'v2': {
                'description': 'Female partner who called 911, visibly shaken, may have visible injuries',
                'behavior': 'Scared but willing to talk to backup officer, may change story if primary subject can hear'
            }
        }
    },
    'assault': {
        'situation': 'Physical fight in parking lot, one party injured',
        'subject': 'Adult male (v1) involved in physical altercation with another male (v2)',
        'behavior': 'Claims self-defense, blames other party, may be injured or intoxicated',
        'additional_subjects': {
            'v2': {
                'description': 'Adult male, other party in the fight, has visible injuries (bloody nose)',
                'behavior': 'Also claims self-defense, blames v1, willing to talk to backup officer'
            }
        }
    },
    'threats': {
        'situation': 'Neighbor threatening another after dispute',
        'subject': 'Adult male (v1) who allegedly made verbal threats to neighbor (v2)',
        'behavior': 'Denies threats or claims they were joking, blames victim for provocation',
        'additional_subjects': {
            'v2': {
                'description': 'Neighbor who called police, scared, has recording/witnesses',
                'behavior': 'Willing to provide statement to backup officer, wants v1 to stop harassing them'
            }
        }
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
        'subject': 'Adult (v1) who may be homeless or intoxicated, has personal belongings on site',
        'behavior': 'May claim right to be there, become argumentative, or plead for time to gather belongings',
        'additional_subjects': {
            'complainant': {
                'description': 'Property owner or manager who called police',
                'behavior': 'Frustrated, wants v1 removed, may or may not want to press charges, backup officer gets details'
            }
        }
    },
    'disturbance': {
        'situation': 'Intoxicated individual causing scene at bar, yelling at patrons, refusing to leave',
        'subject': 'Adult male (v1), heavily intoxicated, aggressive demeanor',
        'behavior': 'Loud, confrontational, may challenge officer authority, unstable on feet',
        'additional_subjects': {
            'bar_staff': {
                'description': 'Bar manager or security who called police',
                'behavior': 'Wants v1 removed, explains what happened, backup officer gets statement and if they want trespass'
            }
        }
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

OFFICER SAFETY (0-15 pts): Positioning, watching hands, backup, tactical decisions
LEGAL PROCEDURE (0-20 pts): ID self, state reason, request documents, articulate RS/PC
INVESTIGATION (0-20 pts): Questions, statements, observations, dispatch checks
COMMUNICATION (0-15 pts): Professional language, de-escalation, commands, control
RESOLUTION (0-10 pts): Enforcement decision, proper procedures

NEW CRITICAL EVALUATION AREAS:

USE OF FORCE JUSTIFICATION (0-10 pts):
- 10 pts: Force justified, proportional, articulated
- 5 pts: Force used but poorly articulated
- 0 pts: Unjustified force, excessive, no articulation
- CRITICAL: If deadly force used on unarmed/compliant subject = AUTOMATIC FAIL
- Must evaluate: Was there a threat? Was force proportional? Could officer articulate reasonable fear?

MIRANDA RIGHTS COMPLIANCE (0-5 pts):
- Deduct 5 points for custodial interrogation without Miranda
- Custody = handcuffed, detained, not free to leave
- Interrogation = asking questions beyond pedigree
- Note: "Miranda violation - statements will be suppressed, case impacted"

EVIDENCE COLLECTION (0-5 pts):
- 5 pts: All visible evidence photographed, collected, documented
- 3 pts: Most evidence collected but some missed
- 0 pts: Critical evidence not collected
- Missed evidence impacts case outcome

MEDICAL RESPONSE (0-5 pts):
- 5 pts: Rendered aid when needed, called EMS
- 0 pts: Failed to render aid when subject needed medical attention
- Note: "Failure to render aid - civil liability, policy violation"

TIME MANAGEMENT & DECISION MAKING (0-5 pts):
- 5 pts: Acted with appropriate urgency
- 3 pts: Some delays but resolved
- 0 pts: Excessive delay caused situation to escalate
- Note: Time pressure and escalation impact

CRITICAL INCIDENTS (AUTOMATIC DEDUCTIONS):
- Officer-Involved Shooting of unarmed subject: -50 points, note "CAREER-ENDING DECISION - Criminal charges likely"
- Unjustified use of force: -20 points
- Miranda violation leading to case dismissal: -15 points
- Failure to render medical aid when needed: -15 points
- Missed evidence causing case dismissal: -10 points

SCORING GUIDANCE:
- 90-100: Exceptional, textbook performance
- 80-89: Very good, minor issues
- 70-79: Satisfactory, some mistakes
- 60-69: Needs improvement, significant issues
- 50-59: Poor performance, major violations
- Below 50: Unacceptable, career risk

CONSEQUENCES ASSESSMENT:
Based on violations, note potential real-world consequences:
- Civil lawsuit filed (excessive force, failure to render aid)
- Criminal charges (unjustified shooting, civil rights violations)
- Policy violations (Miranda, evidence handling)
- Case dismissal (Miranda violation, evidence not collected)
- Internal affairs investigation
- Termination/suspension
- Media coverage
- Community impact

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
The officer's input may include multiple parts:
- [SAYS]: What the officer verbally says to you
- [DOES]: Physical actions the officer takes (shining flashlight, positioning, observing)
- [RADIOS]: Communication with dispatch (you may overhear some of this)

React appropriately to ALL parts of their input.

AUTONOMOUS BACKUP OFFICER:
A competent backup officer (Officer Martinez) is ALWAYS on scene and acts autonomously following standard police procedures. The backup officer takes initiative without needing to be commanded.

AUTOMATIC BACKUP OFFICER ACTIONS BY SCENARIO TYPE:

DOMESTIC VIOLENCE (domestic, domestic_weapons):
- Turn 1: Automatically separates v2 to different room/location
- Turn 1-2: Interviews v2 independently, asks about: what happened, injuries, children, prior incidents, fear level
- Turn 2-3: Documents injuries (photographs, notes), checks on children if present
- Reports findings to primary officer via backup_report field
- Maintains separation between v1 and v2
- Provides containment if situation escalates

TRAFFIC STOPS (all traffic scenarios):
- Automatically positions on passenger side
- Observes occupants and vehicle interior
- Provides cover and watches hands
- Reports observations (furtive movements, contraband in plain view, passenger behavior)
- Assists with warrant arrest if needed

ASSAULTS/FIGHTS:
- Automatically talks to other party or witnesses
- Gets independent statements
- Identifies injuries and who started the altercation
- Secures weapons if present
- Reports findings

DISTURBANCES/TRESPASS:
- Talks to complainant/business owner
- Gets details of what occurred
- Identifies witnesses
- Reports back what complainant wants (trespass, arrest, just wants them gone)

GENERAL PROTOCOL:
- Backup officer acts professionally and follows training
- Reports findings in backup_report field every 1-2 turns when actively investigating
- Coordinates with primary officer but doesn't need direction
- Takes appropriate tactical positions for officer safety

NATURAL LANGUAGE COMMANDS:
If the primary officer gives backup a specific direction in their [SAYS], backup automatically executes it:
- "Martinez, go check the garage" → Backup checks garage, reports findings
- "Backup, talk to that witness" → Backup interviews witness, reports statement
- "Officer, search the vehicle" → Backup searches vehicle, reports results
- "Go get her statement" → Backup gets statement, reports back
- "Ask him about the weapon" → Backup asks, reports response
- "Cover the back door" → Backup repositions, reports when in position

When backup receives a direct command from primary officer:
- Execute the command immediately
- Report findings in backup_report field
- Use format: "Officer Martinez: [completed action] - [findings/results]"

The backup officer is YOUR PARTNER - they handle their responsibilities autonomously AND follow any specific directions you give them.

PHOENIX PD RADIO CODES - COMPLETE REFERENCE:
This is the LANGUAGE everyone uses. Dispatcher, backup officer, and primary officer ALL understand these codes.

TEN CODES:
- 10-1: Signal Weak
- 10-4: Affirmative (OK)
- 10-6: Busy
- 10-7: Going Off Duty/Out of Service
- 10-8: In Service
- 10-9: Say Again
- 10-12: Stand-By (Stop)
- 10-17: Enroute
- 10-20: Location
- 10-21: Call by Phone
- 10-22: Disregard/Take No Further Action
- 10-23: Arrived on Scene
- 10-25: Report to (Meet)
- 10-27: Driver License/Permit - Dispatch runs DL check
- 10-28: Ownership/Registration Information - Dispatch runs vehicle registration
- 10-29: Records Check/Warrant Information - Dispatch checks warrants and criminal history
- 10-31: Pick Up Papers
- 10-33: Help Me Quick
- 10-42: Prisoner in Custody/Booking
- 10-44: Does Not Conform with Rules and Regulations
- 10-50: Switching to Channel
- 10-51: Felony Warrant Outstanding
- 10-52: Misdemeanor Warrant Outstanding
- 10-60: Female Officer Needed
- 10-70: PR Contact
- 10-76: Notify Owner of Vehicle Recovery
- 10-91: Assist Stranded Motorist
- 10-92: Wagon Wanted

SIGNAL CODES:
- 3: Emergency - Use Red Lights & Siren
- 4: No Further Assistance Needed
- 5: Stake Out - Other Units Stay Away
- 6: Out for Investigation

RADIO CODES (CALL TYPES):
- 101/102: Woman in/out of Car
- 210: Strong Armed Robbery
- 211: Armed Robbery
- 236: Threat
- 239: Fight
- 240: Assault
- 245: Aggravated Assault
- 250: Harassment
- 260: Sexual Abuse - Adult
- 261: Sexual Assault
- 301: Prostitution
- 311: Indecent Exposure
- 312: Child Neglect
- 315: Forgery
- 315I: Identity Theft
- 318: Theft by Fraud
- 390: Drunk (Disturbing)
- 390D: Drunk Driver
- 415: Criminal Damage
- 415F: Domestic Violence
- 417G: Subject with a Gun
- 417K: Subject with a Knife
- 451: Homicide
- 459: Burglary
- 487: Theft
- 488: Recovered Property
- 491: Kidnapping
- 503: City Ordinance Offense
- 508: Traffic Control
- 510: Speeding/Racing
- 511: Vehicle Stop
- 585: Traffic Hazard
- 601: Missing Person
- 647: Suspicious Person
- 651: Loose Animals
- 707: Bomb Threat
- 901: Cutting/Stabbing
- 901G: Shooting
- 901H: Dead Body
- 901O: Overdose
- 901U: Suicide
- 906: Officer Needs Assistance
- 907: Backup Requested
- 911H: 9-1-1 Hang-Up
- 915: Arson
- 917: Abandoned Vehicle
- 918: Mentally Ill Subject
- 927: Unknown Trouble
- 928: Found Property
- 961: Accident - No Injuries
- 962: Accident - Injuries
- 963: Accident - Fatality
- 998: Officer Involved Shooting
- 999: Officer Needs Help Urgently

CRITICAL - DISPATCHER RESPONSES:
When officer uses ANY radio code, generate appropriate dispatch_response:

10-27 (Driver License): "Unit [#], 10-27 shows valid/suspended/revoked Arizona DL for [name], DOB [date]"
10-28 (Registration): "Unit [#], 10-28 shows [year/make/model] registered to [name] at [address]"
10-29 (Warrants/Records): "Unit [#], 10-29 [shows warrant/negative for warrants]. [Prior arrests if relevant]"
10-27/10-29 (Combined): "Unit [#], your 10-27 shows valid Arizona DL. 10-29 negative for warrants" OR "10-29 shows 10-51 for [charge]"
10-23 (Arrived): Dispatch acknowledges "10-4, Unit [#] on scene [time]"
10-8 (In Service): "10-4, Unit [#] back in service"
10-33 (Help Quick): Dispatch sends additional units immediately
906 (Needs Assistance): "All units, 906 at [location], Unit [#] needs assistance"
907 (Backup): "10-4, showing backup enroute"
999 (Officer Help Urgent): "999! 999! All units respond to [location]! Unit [#] needs help!"
998 (OIS): "998, Officer Involved Shooting at [location]. Sending supervisors and FIT."
4 (Code 4): Dispatch acknowledges "10-4"

BACKUP OFFICER CODE UNDERSTANDING:
Backup officer HEARS all radio traffic and responds accordingly:
- 10-27/10-29: Backup hears dispatch response, adjusts tactics if warrant/suspended DL
- 10-33/906/999: Backup increases alert level, moves to better position
- 4 (Code 4): Backup relaxes slightly but stays ready
- 907 (Backup Requested): Additional backup units arrive (mention in backup_report if relevant)

Match dispatch responses to scenario (warrant scenario = warrant found, suspended license scenario = suspended DL, etc.)

RESPONSE FORMAT - Return valid JSON only:
{{
  "subject_response": "What the subject says (realistic dialogue)",
  "subject_mood": "calm" | "nervous" | "agitated" | "hostile" | "defeated",
  "subject_action": "Brief body language/actions",
  "dispatch_response": "Dispatch radio response if officer radioed, or null if no radio traffic",
  "backup_report": "AUTONOMOUS backup officer report - what Officer Martinez discovered/observed while conducting their investigation (generate this automatically every 1-2 turns when backup is actively investigating additional subjects, witnesses, or conducting scene work). Null only if backup has nothing new to report.",
  "supervisor_notification": "Supervisor responds if critical incident occurred (OIS, use of force, pursuit, serious injury). Format: 'Sergeant [name]: [questions about incident]' or null",
  "force_used": {{"type": "none" | "verbal" | "hands" | "taser" | "firearm", "justified": true/false, "threat_level": "none" | "passive" | "active" | "aggravated" | "deadly", "articulation_required": true/false}},
  "evidence_visible": ["item1", "item2"] or [],
  "evidence_collected": ["item1"] or [],
  "medical_status": {{"subject_condition": "normal" | "injured" | "critical" | "overdose" | "seizure", "aid_rendered": true/false, "required": true/false}},
  "custody_status": {{"in_custody": true/false, "miranda_required": true/false, "miranda_read": true/false, "interrogation_occurred": true/false, "violation": "reason" or null}},
  "escalation_level": 1-5,
  "time_pressure": {{"urgency": "low" | "medium" | "high" | "critical", "consequence_if_delay": "what happens if officer waits"}},
  "additional_subjects": ["description of bystanders, crowds, other people present"] or [],
  "hint": "Training hint or null",
  "new_observations": [],
  "evaluation": {{"action_taken": "", "legal_basis": null, "assessment": "correct", "note": ""}},
  "scenario_complete": false,
  "end_scenario_reason": null
}}

NEW FEATURE GUIDELINES:

1. USE OF FORCE:
   - Track any force: verbal commands, hands-on, taser, firearm
   - Verbal commands to uncooperative subject = "verbal" force
   - Physical contact = "hands" force
   - Taser deployment = "taser" force
   - Shooting = "firearm" force
   - Justified if: reasonable fear of harm, subject actively resistant/aggressive, proportional to threat
   - NOT justified if: subject unarmed and compliant, excessive force, no articulated threat
   - If officer shoots unarmed compliant person → justified: false, CRITICAL INCIDENT

2. EVIDENCE TRACKING:
   - evidence_visible: Items visible at scene (weapon, drugs, blood, broken items, documents)
   - evidence_collected: Items officer specifically photographed, collected, or secured
   - If officer doesn't collect visible evidence → case impact in debrief

3. MEDICAL EMERGENCIES:
   - Random chance (5-10%) subject has medical issue
   - Overdose scenarios: subject collapses, blue lips, not breathing
   - Injured: bleeding, broken bones, needs medical attention
   - If subject needs medical aid and officer doesn't render → violation, liability
   - Officer must call fire/EMS and/or administer aid (Narcan, CPR, first aid)

4. MIRANDA RIGHTS:
   - in_custody: true when handcuffed, detained and not free to leave, in police vehicle
   - miranda_required: true when in custody AND asking questions
   - miranda_read: true only if officer specifically reads Miranda
   - interrogation_occurred: true if officer asks questions while subject in custody
   - violation: If interrogation while in custody without Miranda → statements suppressed

5. ESCALATION & TIME PRESSURE:
   - Start escalation_level: 1-2
   - Each turn, situation may escalate if officer delays or uses wrong approach
   - Level 1-2: Calm, manageable
   - Level 3: Getting tense, subject more agitated
   - Level 4: Critical, about to turn violent or someone about to get hurt
   - Level 5: Violence occurring, life-threatening
   - time_pressure urgency increases if officer taking too long to act

6. SUPERVISOR NOTIFICATION:
   Required for: Officer-involved shooting, use of force (taser/firearm), serious injury, pursuit, death
   Format: "Sergeant Davis: Unit 23, shots fired reported at your 20. What's your status? Subject condition? Weapon recovered? Any officer injuries?"
   Supervisor asks probing questions about the incident

7. ADDITIONAL SUBJECTS / CHAOS:
   - Include bystanders filming, crowd gathering, other people present
   - Domestic scenarios: children present, neighbors watching
   - Traffic stops: passengers in vehicle, cars driving by
   - Fights: crowd of onlookers, some filming, some yelling
   - Public places: witnesses, people who interfere or try to help
   - Additional subjects may: flee, interfere, need attention, become hostile

CRITICAL: Always generate backup_report when:
- Domestic scenarios: Backup interviewing v2 or checking on children
- Assault/Fight scenarios: Backup talking to the other party (v2)
- Disturbance/Trespass: Backup getting statement from complainant/business owner
- Traffic stops: Backup observing occupants or assisting with arrest
- Any scenario with additional subjects or witnesses
- PRIMARY OFFICER GIVES BACKUP A DIRECT COMMAND in their [SAYS] - backup executes and reports immediately
- OFFICER USES RADIO CODES - backup hears the codes and dispatch response, may adjust tactics

DETECTING NATURAL COMMANDS:
Parse the officer's [SAYS] content for phrases directed at backup officer:
- "Martinez, [action]" or "Officer Martinez, [action]"
- "Backup, [action]" or "Backup officer, [action]"
- "[Action] the [location/person]" when clearly directing backup (e.g., "Check the garage", "Talk to her")
- Questions to backup: "Martinez, did you [action]?" or "What did she say?"

When you detect a command, generate backup_report showing backup completed the task.

BACKUP OFFICER RADIO CODE RESPONSES:
When primary officer radios codes, backup officer HEARS dispatch response and may react in backup_report:
- 10-29 shows 10-51 (felony warrant): "Officer Martinez: *heard dispatch traffic about felony warrant* Moving to better cover position, hand near weapon"
- 10-29 shows 10-52 (misdemeanor warrant): "Officer Martinez: Heard the warrant return. Standing by to assist with arrest"
- 10-33/906/999 (officer needs help): "Officer Martinez: Heard your 10-33! Moving up to provide immediate support"
- 4 (Code 4): "Officer Martinez: 10-4, Code 4. Scene is secure"

Format backup reports like: "Officer Martinez: [what they did] - [what they found/heard]. [Key details]. [Any evidence or observations]."

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
        elif action == 'help':
            return handle_help(data)
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
        model='claude-3-5-haiku-20241022',  # Haiku is 10x faster/cheaper for chat
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
        'dispatch_response': parsed.get('dispatch_response'),
        'backup_report': parsed.get('backup_report'),
        'supervisor_notification': parsed.get('supervisor_notification'),
        'force_used': parsed.get('force_used', {'type': 'none', 'justified': True, 'threat_level': 'none', 'articulation_required': False}),
        'evidence_visible': parsed.get('evidence_visible', []),
        'evidence_collected': parsed.get('evidence_collected', []),
        'medical_status': parsed.get('medical_status', {'subject_condition': 'normal', 'aid_rendered': False, 'required': False}),
        'custody_status': parsed.get('custody_status', {'in_custody': False, 'miranda_required': False, 'miranda_read': False, 'interrogation_occurred': False, 'violation': None}),
        'escalation_level': parsed.get('escalation_level', 1),
        'time_pressure': parsed.get('time_pressure', {'urgency': 'low', 'consequence_if_delay': None}),
        'additional_subjects': parsed.get('additional_subjects', []),
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


def handle_help(data):
    """Handle training help questions."""
    question = data.get('question', '')
    scenario = data.get('scenario', 'unknown')
    scenario_title = data.get('scenario_title', 'Unknown Scenario')
    scenario_context = data.get('scenario_context', '')
    legal_context = data.get('legal_context', '')
    safety_context = data.get('safety_context', '')
    conversation_history = data.get('conversation_history', [])

    # Build context from conversation
    convo_summary = ""
    if conversation_history:
        recent = conversation_history[-4:]  # Last 4 messages
        convo_parts = []
        for msg in recent:
            if msg.get('role') == 'officer':
                convo_parts.append(f"Officer: {msg.get('content', '')[:100]}")
            elif msg.get('role') == 'subject':
                convo_parts.append(f"Subject: {msg.get('content', '')[:100]}")
        convo_summary = "\n".join(convo_parts)

    help_prompt = f"""You are a law enforcement training assistant helping an officer-in-training during a scenario.

CURRENT SCENARIO: {scenario_title}
SCENARIO CONTEXT: {scenario_context}

LEGAL REFERENCE INFO:
{legal_context}

OFFICER SAFETY REFERENCE:
{safety_context}

RECENT INTERACTION:
{convo_summary}

TRAINEE'S QUESTION: {question}

Provide a helpful, concise answer (2-4 sentences max). Focus on:
- Practical advice they can use right now
- Relevant Arizona statutes if legal question
- Officer safety considerations
- What they should do or say next

Be direct and tactical. This is training, so give them guidance without doing the scenario for them."""

    try:
        response = client.messages.create(
            model='claude-3-5-haiku-20241022',
            max_tokens=300,
            temperature=0.5,
            messages=[
                {
                    'role': 'user',
                    'content': help_prompt
                }
            ]
        )

        answer = response.content[0].text
        return (json.dumps({'answer': answer}), 200, CORS_HEADERS)

    except Exception as e:
        return (json.dumps({
            'answer': f'Consider your legal authority for this scenario and prioritize officer safety. What specific aspect do you need help with?'
        }), 200, CORS_HEADERS)
