"""
FLL Tournament Scheduler - Configuratie
Pas deze waarden aan voor jouw specifieke toernooi
"""

# ===== TOERNOOI INSTELLINGEN =====

# Aantal teams (10-40)
NUM_TEAMS = 40

# Aantal tafels beschikbaar (4-10)
NUM_TABLES = 4

# Aantal jury rooms beschikbaar (4-10)
NUM_JURY_ROOMS = 8

# Aantal tijdsloten (auto-berekend of handmatig instellen)
NUM_TIMESLOTS = 30  # Verhoog dit als er geen oplossing gevonden wordt

# Aantal wedstrijden per team (standaard 4 voor FLL)
MATCHES_PER_TEAM = 4

# Aantal jury sessies per team (standaard 1)
JURY_SESSIONS_PER_TEAM = 1

# Minimaal aantal tijdsloten tussen activiteiten per team
# 1 = minstens 1 tijdslot tussen elke wedstrijd/jury sessie
MIN_GAP_BETWEEN_ACTIVITIES = 4  # Minimum buffer time in timeslots

# ===== TIMING INSTELLINGEN =====

# Duur van een wedstrijd in minuten
MATCH_DURATION = 7

# Duur van een jury sessie in minuten
JURY_DURATION = 42

# Minimale buffer tijd tussen activiteiten in minuten
MINIMUM_BUFFER_TIME = 30

# Start tijd van het toernooi
START_TIME = "09:30"

# Pauze instellingen (optioneel)
BREAK_START_TIME = 168  # minuten na start
BREAK_DURATION = 30  # minuten

# Maximale oplostijd in seconden
MAX_SOLVE_TIME = 120

# ===== VOORBEELDEN =====

# Klein toernooi:
# NUM_TEAMS = 10
# NUM_TABLES = 4
# NUM_TIMESLOTS = 6

# Middelgroot toernooi:
# NUM_TEAMS = 20
# NUM_TABLES = 8
# NUM_TIMESLOTS = 10

# Groot toernooi:
# NUM_TEAMS = 30
# NUM_TABLES = 10
# NUM_TIMESLOTS = 10
