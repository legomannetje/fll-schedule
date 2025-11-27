# First Lego League Tournament Scheduler

Een planning tool voor First Lego League toernooien die gebruik maakt van Google OR-Tools constraint programming om een optimaal wedstrijdschema te maken.

## Functionaliteit

- Plant **10-40 teams** over **4-10 tafels**
- Elk team speelt **4 wedstrijden**
- Flexibel aantal **tijdsloten** (4-10)
- **Minimaal 1 tijdslot tussen wedstrijden** per team
- Teams spelen bij voorkeur op **dezelfde tafel** of maximaal 2 tafels
- Optimaliseert voor minimale tafelwisselingen

## Installatie

```bash
pip install ortools
```

## Gebruik

Pas de parameters aan in `ffl_scheduler.py`:

```python
num_teams = 12          # Aantal teams (10-40)
num_tables = 6          # Aantal tafels (4-10)
num_timeslots = 8       # Aantal tijdsloten (4-10)
matches_per_team = 4    # Wedstrijden per team
min_gap_between_matches = 1  # Minimale tijdsloten tussen wedstrijden
```

Voer uit:

```bash
python ffl_scheduler.py
```

## Output

Het programma genereert:
1. **Schema per tijdslot**: Welk team speelt op welke tafel
2. **Overzicht per team**: Alle wedstrijden van elk team met tafelnummers
3. **Statistieken**: Aantal tafelwisselingen en oplostijd

## Voorbeeld Output

```
Tijdslot 1:
  Tafel 1: Team 3
  Tafel 2: Team 7
  ...

Team 1:
  Tijdslot 2: Tafel 3
  Tijdslot 4: Tafel 3
  Tijdslot 6: Tafel 3
  Tijdslot 8: Tafel 3
  → Gebruikt 1 tafel(s): [3]
```

## Tips

Als er geen oplossing wordt gevonden:
- Verhoog het aantal tijdsloten
- Verlaag het aantal teams
- Verklein de gap tussen wedstrijden
- Voeg meer tafels toe

## Technologie

Gebruikt [Google OR-Tools CP-SAT solver](https://developers.google.com/optimization/cp/cp_solver) voor constraint programming optimalisatie.
