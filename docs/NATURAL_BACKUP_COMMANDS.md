# Natural Language Backup Commands

## Overview

Your backup officer (Officer Martinez) now responds to **natural language commands** - just tell them what to do in your normal speech and they automatically do it and report back.

**No special syntax. No prefixes. Just talk to your partner like a real officer would.**

## How It Works

### The Old Way (REMOVED)
```
[BACKUP COMMAND]: Go check the garage
[BACKUP COMMAND]: Talk to that witness
```
❌ Special syntax required
❌ Separate from natural dialogue

### The New Way (NOW LIVE)
```
[SAYS]: Martinez, go check the garage for weapons
[SAYS]: Backup, talk to that witness over there
[SAYS]: Ask her about the kids
```
✅ Natural speech
✅ Automatic execution
✅ Immediate reporting

## Examples

### Example 1: Domestic Violence - Directing Investigation

**Your Input:**
```
[SAYS]: Martinez, go talk to her in the kitchen and find out what happened
[SAYS to subject]: Sir, step outside with me right now
[DOES]: Point to the door
```

**Response:**
- **Subject (v1):** "Fine, whatever."
- **Backup Report:** "Officer Martinez: I took v2 to the kitchen out of earshot. She states v1 became enraged over money, grabbed her by the throat and struck her in the face twice. She has visible bruising on her left cheek and red marks on her neck. She's scared and wants him arrested. I asked about children - two kids ages 5 and 8 are in the bedroom, they witnessed the assault."

### Example 2: Assault - Getting the Other Side

**Your Input:**
```
[SAYS]: Backup, get his side of the story
[SAYS to v1]: Tell me what happened here
[DOES]: Check v1 for injuries
```

**Response:**
- **Subject (v1):** "He started it! Came at me over nothing!"
- **Backup Report:** "Officer Martinez: I separated v2 about 40 feet away. He has a bloody nose and swelling under his right eye. He states v1 approached him aggressively in the parking lot and threw the first punch without provocation. There's a store employee who witnessed the entire incident - she confirms v1 was the aggressor. V2 wants to press charges."

### Example 3: Disturbance - Specific Task

**Your Input:**
```
[SAYS]: Martinez, go talk to the manager and see if they want him trespassed
[SAYS to subject]: Sir, you need to calm down
[DOES]: Position between subject and door
```

**Response:**
- **Subject:** "I'm not doing nothing wrong!"
- **Backup Report:** "Officer Martinez: Spoke with the bar manager. Subject has been here 3 hours, heavily intoxicated, harassing other patrons and refusing to leave when asked. Manager wants him removed and trespassed from the property. Manager will sign the trespass form."

### Example 4: Traffic Stop - Search Direction

**Your Input:**
```
[SAYS]: Martinez, search the vehicle for contraband
[SAYS to subject]: Stay right there by my patrol car
[DOES]: Maintain visual on subject
```

**Response:**
- **Subject:** "There's nothing in my car!"
- **Backup Report:** "Officer Martinez: Conducted search of vehicle. Found approximately 2 grams of methamphetamine in a baggie in the center console, and a glass pipe under the driver's seat. Photographing evidence now. Also found opened container of alcohol in cup holder."

### Example 5: Domestic - Specific Question

**Your Input:**
```
[SAYS]: Martinez, did she say if there are any weapons in the house?
[SAYS to v1]: How much have you had to drink tonight?
```

**Response:**
- **Subject (v1):** "Just a couple beers, so what?"
- **Backup Report:** "Officer Martinez: Yes, v2 states there's a handgun in the bedroom nightstand. She said v1 showed it to her during the argument and said 'this could all be over.' I'm securing the weapon now for officer safety."

### Example 6: Multiple Commands in One Turn

**Your Input:**
```
[SAYS]: Martinez, check on the kids and then get her statement about what started this
[SAYS to v1]: Put your hands where I can see them
[DOES]: Draw taser, give loud commands
```

**Response:**
- **Subject (v1):** "Whoa, okay okay!" *raises hands*
- **Backup Report:** "Officer Martinez: Checked on the children first - two kids ages 4 and 6 in the back bedroom, they're unharmed but scared. Interviewed v2 - she states argument started when v1 came home drunk. He became violent when she asked him to leave. This is the 4th time he's assaulted her but first time she's called police. She wants a protection order."

### Example 7: Scene Security

**Your Input:**
```
[SAYS]: Backup, cover the back door in case he runs
[SAYS to subject]: Come out with your hands up!
```

**Response:**
- **Subject:** *silence from inside*
- **Backup Report:** "Officer Martinez: Moving to cover the back exit. In position now, have visual on rear door and windows. No movement observed yet."

### Example 8: Evidence Documentation

**Your Input:**
```
[SAYS]: Martinez, photograph her injuries and document everything you see
[SAYS to v1]: You're under arrest for domestic violence
[DOES]: Handcuff subject
```

**Response:**
- **Subject (v1):** "This is bullshit!"
- **Backup Report:** "Officer Martinez: Photographed v2's injuries - bruising on left cheek, red marks on neck consistent with strangulation, scratches on forearms. Also documented broken lamp and hole in wall. V2 signed photo consent form. Injuries are fresh and consistent with her statement."

## Supported Command Formats

The AI recognizes these natural patterns:

### Direct Address
- "Martinez, [action]"
- "Officer Martinez, [action]"
- "Backup, [action]"
- "Backup officer, [action]"

### Task Assignment
- "Go [action]"
- "Check [location/item]"
- "Search [location/item]"
- "Talk to [person]"
- "Get [information]"
- "Ask [person] about [topic]"
- "Find out [information]"

### Questions
- "Martinez, what did [person] say?"
- "Did [person] mention [topic]?"
- "Is there [item/condition]?"

### Positioning
- "Cover [location]"
- "Watch [location/person]"
- "Secure [location/item]"

## How Backup Responds

When you give a command:

1. **Backup executes immediately** - No delay, no confirmation needed
2. **Reports findings in backup_report field** - You see results in the response
3. **Provides complete information** - Statements, observations, evidence
4. **Maintains autonomy** - Still handles standard procedures independently

## Combining Autonomous + Command

The best part: **Backup acts autonomously AND follows your specific directions.**

**Turn 1 - Autonomous:**
```
You: [SAYS]: Sir, step outside

Response:
- Backup Report: "Officer Martinez: I've automatically separated v2 to the
  kitchen. She has visible injuries. Standing by for your direction."
```

**Turn 2 - Specific Command:**
```
You: [SAYS]: Martinez, ask her if she wants to press charges and get a written statement

Response:
- Backup Report: "Officer Martinez: Asked v2 about pressing charges. She's
  adamant she wants him arrested and prosecuted. I have her written statement
  documenting the assault. She signed it."
```

**Turn 3 - Autonomous Again:**
```
You: [SAYS to v1]: You're under arrest
     [DOES]: Apply handcuffs

Response:
- Backup Report: "Officer Martinez: I've called for victim services to respond.
  Family member is en route to get the children. Scene is Code 4."
```

## Pro Tips

### 1. Be Specific When Needed
```
Good: "Martinez, ask her about prior domestic violence incidents"
Okay: "Martinez, talk to her"
```

### 2. Let Backup Handle Standard Procedures
```
Don't need: "Martinez, separate the subjects"  ← They do this automatically
Do need: "Martinez, check the basement for the suspect"  ← Specific direction
```

### 3. Use Natural Police Language
```
"Cover the back"
"Get a statement"
"Search the vehicle"
"Secure that weapon"
"Check on the kids"
```

### 4. Ask Follow-Up Questions
```
"Martinez, what did the witness say about who started it?"
"Did she mention any weapons?"
"Is the manager willing to sign a trespass?"
```

## Realistic Scenarios

### Scenario: Burglary in Progress

**Turn 1:**
```
[SAYS]: Martinez, cover the back exit
[SAYS]: Police! Come out with your hands up!
```
→ Backup: "In position covering rear. No movement observed."

**Turn 2:**
```
[SAYS]: Backup, check those back rooms for additional suspects
[DOES]: Clear front area
```
→ Backup: "Checked back rooms - one suspect hiding in closet, detained and secured. No other suspects found."

### Scenario: Traffic Stop with Passenger

**Turn 1:**
```
[SAYS]: Martinez, keep an eye on the passenger
[SAYS to driver]: License and registration please
```
→ Backup: "Watching passenger closely. He's extremely nervous, fidgeting with something under the seat."

**Turn 2:**
```
[SAYS]: Backup, have the passenger step out and talk to him
[SAYS to driver]: Step out of the vehicle
```
→ Backup: "Passenger is out of vehicle. He admitted there's marijuana in the center console. Says it's his, not the driver's."

### Scenario: Mental Health Crisis

**Turn 1:**
```
[SAYS]: Martinez, talk to the family member and find out what's going on
[SAYS to subject]: Sir, I'm here to help you
```
→ Backup: "Spoke with the sister. Subject stopped taking his schizophrenia medication 3 weeks ago. He's been having paranoid delusions, thinks people are following him. Not violent but needs psychiatric evaluation. Sister wants him transported to crisis center."

## Summary

**Old System:** Required special `[BACKUP COMMAND]:` syntax

**New System:** Just talk naturally

**How to use:**
1. Address backup by name: "Martinez, [action]"
2. Give them tasks: "Go check...", "Talk to...", "Search..."
3. Ask questions: "What did she say?", "Did you find anything?"

**What happens:**
- Backup executes immediately
- Reports findings automatically
- Handles standard procedures autonomously
- Follows your specific directions when given

**Result:** Realistic partner coordination without micromanagement or special syntax.

Just talk to your backup officer like a real partner and they handle the rest!
