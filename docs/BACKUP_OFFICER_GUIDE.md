# ⚠️ DEPRECATED - This Guide is Outdated

## This Command-Based System Has Been Replaced

**The backup officer no longer needs commands!** This guide describes an old system that required micromanagement.

👉 **See the new guide:** `AUTONOMOUS_BACKUP_OFFICER.md`

The new system features a **fully autonomous AI partner** who acts independently without needing to be told what to do. Much more realistic and useful!

---

# Old Backup Officer Command and Reporting System (DEPRECATED)

## Overview (OLD SYSTEM - NO LONGER USED)

~~The BlueShield AI training system now supports commanding your backup officer and receiving information reports back from them. This is especially useful in domestic violence scenarios where you need to separate subjects and gather independent statements.~~

**This system has been replaced with an autonomous backup officer who acts independently. No commands needed!**

## How to Use

### 1. Commanding Your Backup Officer

Use the `[BACKUP COMMAND]:` prefix in your message to direct your backup officer:

```
[BACKUP COMMAND]: Go talk to v2 and get her statement
[SAYS]: Sir, I need you to step outside with me
[DOES]: Position myself between subject and the doorway
```

### 2. Common Backup Commands

- `Go talk to v2` - Send backup to interview the second subject (victim, witness, etc.)
- `Search the area for weapons` - Have backup look for weapons mentioned in the call
- `Check on the children` - Have backup check welfare of children at scene
- `Get v2's injuries documented` - Have backup photograph/document injuries
- `Keep v1 and v2 separated` - Maintain separation between subjects
- `Search the vehicle` - If you have consent/PC, have backup search vehicle

### 3. Receiving Backup Reports

When your backup officer completes their task, you'll receive a `backup_report` field in the response:

```json
{
  "subject_response": "I didn't do nothing! She's lying!",
  "subject_mood": "agitated",
  "backup_report": "Officer Miller reporting: I spoke with v2 in the kitchen. She states v1 punched her in the face during an argument about money. She has a visible bruise on her left cheek, appears scared. She said this has happened 3 times before but she never called police. Two children (ages 4 and 7) are in the bedroom, unharmed but aware of the fight."
}
```

## Domestic Violence Scenario Example

### Scenario Setup
You're responding to a domestic violence call. There are two subjects:
- **v1**: Adult male who allegedly struck his partner
- **v2**: Female victim who called 911

### Example Interaction

**Officer Turn 1:**
```
[BACKUP COMMAND]: Take v2 into the kitchen and get her full statement. Ask about injuries, what happened, and if this has occurred before.
[SAYS]: Sir, I'm Officer Johnson. I need you to step outside with me so we can talk.
[DOES]: Position myself at the doorway, maintain visual on subject's hands
```

**System Response:**
```json
{
  "subject_response": "What? No, everything's fine officer. We were just having a discussion. Nobody needs to go anywhere.",
  "subject_mood": "defensive",
  "subject_action": "Crosses arms, blocks doorway slightly",
  "backup_report": "Officer Martinez: I've separated v2 to the kitchen. She's crying, has a visible red mark on her left cheek. She states v1 became angry when she asked about money he spent. He grabbed her by the shoulders, shook her, then struck her once in the face with an open hand. She fell backwards into the kitchen table. She says he's done this twice before but she was too scared to call. Children are in the back bedroom, she says they saw the incident.",
  "dispatch_response": null
}
```

**Officer Turn 2:**
```
[RADIOS]: Dispatch, show me Code 4 on scene. Run a 10-27/29 on [subject name and DOB]
[SAYS]: Sir, I understand, but we received a 911 call from this address. I need to speak with both of you separately. Step outside with me now.
[DOES]: Use command voice, point to the door
```

**System Response:**
```json
{
  "subject_response": "*sighs heavily* Fine. This is ridiculous. She probably called you because she's mad at me.",
  "subject_mood": "defeated",
  "subject_action": "Reluctantly steps outside, hands visible",
  "dispatch_response": "Unit 23, your 10-27 shows valid Arizona DL, no wants. 10-29 shows one prior domestic violence arrest, charges dropped.",
  "backup_report": null
}
```

## Tips for Using Backup Officers

1. **Always separate subjects in domestic violence calls** - This is both for safety and to get independent statements

2. **Use backup for evidence collection** - Have them photograph injuries, secure weapons, or document the scene

3. **Backup can talk to witnesses** - In multi-person incidents, have backup interview witnesses while you handle the primary subject

4. **Information flows naturally** - The backup report will appear when the backup officer completes their task, usually in the next turn

5. **Backup follows your commands** - The AI simulates a competent backup officer who follows your directions

## Multiple Subject Scenarios

Currently supported scenarios with multiple subjects (v1, v2):
- `domestic` - Domestic disturbance with male suspect (v1) and female victim (v2)
- `domestic_weapons` - Domestic violence with weapon, suspect (v1) and victim (v2)

More scenarios will be updated to support multiple subjects in future updates.

## Technical Details

The backup officer command system works by:
1. Parsing your `[BACKUP COMMAND]:` input
2. Simulating the backup officer performing that task with the specified subject
3. Generating realistic findings based on the scenario
4. Returning those findings in the `backup_report` field

The AI understands the scenario context and generates appropriate responses for what v2 or other subjects would say to your backup officer.
