# First Lego League Tournament Scheduler

Een complete planning tool voor First Lego League toernooien die gebruik maakt van Google OR-Tools constraint programming om een optimaal wedstrijdschema te maken met **zowel matches (wedstrijden) als jury sessies**.

## ✨ Functionaliteit

### Matches (Wedstrijden)
- Plant **10-40 teams** over **4-10 tafels**
- Elk team speelt **4 wedstrijden**
- Teams spelen bij voorkeur op **dezelfde tafel** of maximaal 2 tafels
- Wedstrijd duur: **7 minuten** (configureerbaar)

### Jury Sessies
- Plant **jury sessies** in **4-10 jury rooms**
- Elk team heeft **1 jury sessie** (configureerbaar)
- Jury sessie duur: **42 minuten** (configureerbaar)

### Planning Optimalisatie
- **Minimale buffer tijd** tussen activiteiten (standaard 30 minuten)
- Voorkomt overlap tussen matches en jury sessies
- Optimaliseert voor minimale tafelwisselingen
- **Exporteert naar JSON** voor verder gebruik

## 📦 Installatie

### Optie 1: Met Conda (aanbevolen)
```bash
conda create -n ffl python=3.11 -y
conda activate ffl
pip install ortools
```

### Optie 2: Met pip
```bash
pip install -r requirements.txt
```

## 🚀 Gebruik

### Snelstart - Complete Scheduler (aanbevolen)

**Voor complete toernooi planning met matches EN jury sessies:**

1. Pas `config.py` aan met jouw toernooi gegevens:

```python
NUM_TEAMS = 40              # Aantal teams (10-40)
NUM_TABLES = 6              # Aantal tafels (4-10)
NUM_JURY_ROOMS = 8          # Aantal jury rooms (4-10)
NUM_TIMESLOTS = 30          # Aantal tijdsloten (verhoog indien nodig)
MATCHES_PER_TEAM = 4        # Wedstrijden per team
JURY_SESSIONS_PER_TEAM = 1  # Jury sessies per team
MATCH_DURATION = 7          # Minuten per wedstrijd
JURY_DURATION = 42          # Minuten per jury sessie
MINIMUM_BUFFER_TIME = 30    # Min. minuten tussen activiteiten
```

2. Voer uit:

```bash
python complete_scheduler.py
```

Dit genereert een compleet JSON bestand met:
- ✅ Alle wedstrijden (matches) per team
- ✅ Alle jury sessies per team
- ✅ Optimale timing met buffer tijd
- ✅ Minimale tafelwisselingen

### Alternatieve Scripts

### Alternatieve Scripts

- **`complete_scheduler.py`** - 🎯 **AANBEVOLEN**: Complete scheduler met matches + jury sessies
- **`generate_json.py`** - Alleen matches (geen jury), JSON output
- **`run_scheduler.py`** - Alleen matches met CSV export
- **`ffl_simple.py`** - Standalone versie met parameters in het script
- **`quick_schedule.py`** - Command-line tool met argumenten

### JSON Output genereren

De complete scheduler genereert automatisch een JSON bestand met het formaat:
- `constraintConfiguration` - Timing configuratie (wedstrijd/jury duur, buffer tijd)
- `tableList` - Alle tafels met hun table pairs
- `juryList` - Alle jury rooms
- `teamList` - Alle teams
- `tableTimeslotList` - Alle beschikbare timeslots per tafel
- `juryTimeslotList` - Alle jury sessie tijden
- `teamTableAllocationList` - **Match toewijzingen** (team → tafel → tijd)
- `teamJuryAllocationList` - **Jury toewijzingen** (team → jury room → tijd)

## 📊 Output

Het programma genereert:

1. **Complete JSON export** (`schedule-complete-*.json`)
   - Matches: welk team speelt wanneer op welke tafel
   - Jury sessies: welk team heeft wanneer welke jury sessie
   - Volledige timing informatie in minuten
   - Klaar voor import in andere systemen

2. **Console output met statistieken**:
   - Status (OPTIMAAL/HAALBAAR)
   - Oplostijd
   - Aantal matches en jury sessies
   - Tafel verdeling per team

## 💡 Voorbeeld Output

```
🏆 FLL COMPLETE TOURNAMENT SCHEDULER
======================================================================
📋 Configuratie:
   Teams: 40
   Tafels: 6
   Jury Rooms: 8
   Tijdsloten: 30
   Wedstrijden per team: 4
   Jury sessies per team: 1
   Min. buffer tijd: 30 min
======================================================================

� Capaciteit check:
   Matches: 160 nodig, 180 beschikbaar
   Jury sessies: 40 nodig, 240 beschikbaar
   ✅ Capaciteit OK

✅ Oplossing gevonden!

======================================================================
📊 STATISTIEKEN
======================================================================
Status: OPTIMAAL ✅
Oplostijd: 4.78 seconden
Conflicten: 0
Branches: 5,346

Totaal matches: 160
Totaal jury sessies: 40

Tafel verdeling:
  Teams op 1 tafel: 40
  Teams op 2 tafels: 0

💾 Schema opgeslagen als: schedule-complete-2025-11-27T14-27-53.json
```

## ⚙️ Configuratie voorbeelden

### Klein toernooi (12 teams)
```python
NUM_TEAMS = 12
NUM_TABLES = 4
NUM_JURY_ROOMS = 4
NUM_TIMESLOTS = 10
MINIMUM_BUFFER_TIME = 30
```

### Middelgroot toernooi (24 teams)
```python
NUM_TEAMS = 24
NUM_TABLES = 6
NUM_JURY_ROOMS = 6
NUM_TIMESLOTS = 20
MINIMUM_BUFFER_TIME = 30
```

### Groot toernooi (40 teams)
```python
NUM_TEAMS = 40
NUM_TABLES = 6
NUM_JURY_ROOMS = 8
NUM_TIMESLOTS = 30
MINIMUM_BUFFER_TIME = 30  # Meer rust tussen activiteiten
```

## 🔧 Tips & Troubleshooting

### Geen oplossing gevonden?

Als er geen oplossing wordt gevonden, probeer:
- ✅ **Verhoog NUM_TIMESLOTS** (meest effectief) - voeg 5-10 tijdsloten toe
- ✅ Verlaag MINIMUM_BUFFER_TIME (van 30 naar 20 minuten)
- ✅ Verhoog MAX_SOLVE_TIME (van 120 naar 300 seconden)
- ✅ Voeg meer tafels of jury rooms toe
- ✅ Verlaag het aantal teams

### Vuistregel voor aantal tijdsloten

**Voor matches:**
Minimaal = `(aantal_teams × matches_per_team) / aantal_tafels`

**Voor jury sessies:**
Minimaal = `(aantal_teams × jury_sessions_per_team) / aantal_jury_rooms`

**Totaal aanbevolen:**
Neem het maximum van beide + **5-10 extra tijdsloten** voor flexibiliteit

**Voorbeeld:** 40 teams, 6 tafels, 8 jury rooms
- Matches: (40 × 4) / 6 = 27 tijdsloten
- Jury: (40 × 1) / 8 = 5 tijdsloten
- Aanbevolen: 30-35 tijdsloten

### Teams op te veel tafels?

Als teams op meer dan 2 tafels spelen:
- Verhoog NUM_TIMESLOTS (geeft meer flexibiliteit voor optimalisatie)
- De optimizer probeert dit automatisch te minimaliseren

### Timing configuratie

De timing werkt als volgt:
- Elk **match timeslot** = MATCH_DURATION (7 min)
- Elk **jury timeslot** = JURY_DURATION (42 min)
- **Buffer tijd** = MINIMUM_BUFFER_TIME (30 min) tussen alle activiteiten van een team
- Teams kunnen niet tegelijk een match EN jury sessie hebben

## 📁 Bestandsstructuur

```
ffl-schedule/
├── config.py                    # ⚙️ Configuratie (pas dit aan!)
├── complete_scheduler.py        # 🎯 Complete scheduler (matches + jury)
├── generate_json.py             # 📝 Alleen matches, JSON output
├── run_scheduler.py             # 🚀 Matches met CSV export
├── ffl_simple.py                # 📝 Standalone versie
├── quick_schedule.py            # � Command-line tool
├── requirements.txt             # 📦 Dependencies
├── schedule-complete-*.json     # 💾 Complete JSON output (gegenereerd)
├── schedule-*.json              # 💾 Matches-only JSON (gegenereerd)
├── ffl_schedule.csv             # 💾 CSV output (gegenereerd)
└── README.md                    # 📖 Deze documentatie
```

## 🧮 Hoe werkt het?

De scheduler gebruikt **Constraint Programming** (CP-SAT solver van Google OR-Tools):

### 1. Harde Constraints (moeten voldaan worden)
**Voor Matches:**
- Elk team speelt exact 4 wedstrijden
- Maximaal 1 team per tafel per tijdslot
- Een team kan maar op 1 tafel per tijdslot spelen

**Voor Jury Sessies:**
- Elk team heeft exact 1 jury sessie
- Maximaal 1 team per jury room per tijdslot
- Een team kan maar in 1 jury room per tijdslot zijn

**Overlap Preventie:**
- Een team kan niet tegelijk een match EN jury sessie hebben
- Minimale buffer tijd tussen alle activiteiten van een team

### 2. Zachte Constraints (optimalisatie doelen)
- Minimaliseer aantal verschillende tafels per team
- Bij voorkeur speelt elk team op 1 tafel

De solver zoekt automatisch naar de beste oplossing binnen de gestelde grenzen en vindt een optimale balans tussen matches en jury sessies.

## 📄 JSON Output Structuur

Het gegenereerde JSON bestand bevat:

```json
{
  "constraintConfiguration": {
    "matchDuration": 7,
    "juryDuration": 42,
    "minimumBreakDuration": 30,
    "startTime": "09:30"
  },
  "tableList": [...],           // Alle tafels
  "juryList": [...],            // Alle jury rooms  
  "teamList": [...],            // Alle teams
  "tableTimeslotList": [...],   // Match tijdsloten
  "juryTimeslotList": [...],    // Jury tijdsloten
  "teamTableAllocationList": [...],  // Match planning
  "teamJuryAllocationList": [...]    // Jury planning
}
```

Elk team krijgt:
- 4 entries in `teamTableAllocationList` (4 matches)
- 1 entry in `teamJuryAllocationList` (1 jury sessie)

Met buffer tijd ertussen gegarandeerd!

## 🤝 Contributing

Suggesties en verbeteringen zijn welkom! Maak een issue of pull request aan.

## 📜 Licentie

Free to use voor FLL toernooien. Gebaseerd op OR-Tools voorbeelden.

## 🔗 Links

- [Google OR-Tools](https://developers.google.com/optimization)
- [CP-SAT Solver](https://developers.google.com/optimization/cp/cp_solver)
- [First Lego League](https://www.firstlegoleague.org/)
