"""
FLL Scheduler met JSON output formaat
Genereert scheduling data in het juiste formaat voor verder gebruik
"""
from ortools.sat.python import cp_model
from config import (
    NUM_TEAMS,
    NUM_TABLES,
    NUM_TIMESLOTS,
    MATCHES_PER_TEAM,
    MIN_GAP_BETWEEN_MATCHES,
    MAX_SOLVE_TIME
)
import json
from datetime import datetime, timedelta


def create_schedule_json():
    """Maakt een FLL wedstrijdschema en exporteert naar JSON"""
    
    all_teams = range(NUM_TEAMS)
    all_tables = range(NUM_TABLES)
    all_timeslots = range(NUM_TIMESLOTS)
    
    print(f"\n🏆 FLL TOURNAMENT SCHEDULER")
    print(f"=" * 70)
    print(f"Teams: {NUM_TEAMS} | Tafels: {NUM_TABLES} | Tijdsloten: {NUM_TIMESLOTS}")
    print(f"Wedstrijden per team: {MATCHES_PER_TEAM}")
    print(f"Minimale gap tussen wedstrijden: {MIN_GAP_BETWEEN_MATCHES} tijdslot(en)")
    print(f"=" * 70 + "\n")

    model = cp_model.CpModel()

    # Variabelen
    matches = {}
    for team in all_teams:
        for timeslot in all_timeslots:
            for table in all_tables:
                matches[(team, timeslot, table)] = model.new_bool_var(
                    f"t{team}_ts{timeslot}_tb{table}"
                )

    # Constraints
    # 1. Elk team speelt precies MATCHES_PER_TEAM wedstrijden
    for team in all_teams:
        model.add(sum(matches[(team, ts, tb)] 
                     for ts in all_timeslots 
                     for tb in all_tables) == MATCHES_PER_TEAM)

    # 2. Maximaal 1 team per tafel per tijdslot
    for timeslot in all_timeslots:
        for table in all_tables:
            model.add_at_most_one(matches[(team, timeslot, table)] 
                                 for team in all_teams)

    # 3. Maximaal 1 wedstrijd per team per tijdslot
    for team in all_teams:
        for timeslot in all_timeslots:
            model.add_at_most_one(matches[(team, timeslot, table)] 
                                 for table in all_tables)

    # 4. Minimale gap tussen wedstrijden
    for team in all_teams:
        for ts in range(NUM_TIMESLOTS):
            for next_ts in range(ts + 1, min(ts + 1 + MIN_GAP_BETWEEN_MATCHES, NUM_TIMESLOTS)):
                model.add(sum(matches[(team, ts, tb)] for tb in all_tables) +
                         sum(matches[(team, next_ts, tb)] for tb in all_tables) <= 1)

    # 5. Optimalisatie: Teams bij voorkeur op dezelfde tafel
    tables_used = {}
    for team in all_teams:
        for table in all_tables:
            tables_used[(team, table)] = model.new_bool_var(f"t{team}_uses_tb{table}")
            team_matches_on_table = [matches[(team, ts, table)] for ts in all_timeslots]
            model.add(sum(team_matches_on_table) >= 1).only_enforce_if(
                tables_used[(team, table)])
            model.add(sum(team_matches_on_table) == 0).only_enforce_if(
                tables_used[(team, table)].Not())

    model.minimize(sum(tables_used[(team, table)] 
                      for team in all_teams 
                      for table in all_tables))

    # Oplossen
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = MAX_SOLVE_TIME
    
    print("🔍 Bezig met zoeken naar optimale oplossing...")
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return build_json_output(solver, matches, all_teams, all_tables, all_timeslots, status)
    else:
        return None


def build_json_output(solver, matches, all_teams, all_tables, all_timeslots, status):
    """Bouwt de JSON output in het gewenste formaat"""
    
    # Configuration (met standaard waarden, kun je later configureerbaar maken)
    match_duration = 7  # minuten per wedstrijd
    start_time = "09:30"
    
    output = {
        "constraintConfiguration": {
            "constraintWeight": "1hard/0medium/0soft",
            "minimumBreakDuration": 27,
            "startTime": start_time,
            "breakStartTime": 168,
            "breakDuration": 30,
            "matchDuration": match_duration,
            "juryDuration": 42
        },
        "tableList": [],
        "tablePairList": [],
        "juryList": [],
        "teamList": [],
        "tableTimeslotList": [],
        "juryTimeslotList": [],
        "teamTableAllocationList": [],
        "score": "0hard/0medium/0soft" if status == cp_model.OPTIMAL else "1hard/0medium/0soft"
    }
    
    # Genereer tablePairs (2 tafels per paar)
    num_table_pairs = (NUM_TABLES + 1) // 2
    for pair_id in range(num_table_pairs):
        output["tablePairList"].append({"id": pair_id})
    
    # Genereer tables
    for table_id in all_tables:
        pair_id = table_id // 2
        output["tableList"].append({
            "id": table_id,
            "tablePair": {"id": pair_id}
        })
    
    # Genereer jury's (1 jury per tafel pair)
    for jury_id in range(num_table_pairs):
        output["juryList"].append({"id": jury_id})
    
    # Genereer teams
    for team_id in all_teams:
        output["teamList"].append({"id": team_id})
    
    # Genereer tableTimeslots
    timeslot_id = 0
    for ts in all_timeslots:
        start_time_minutes = ts * match_duration
        for table_id in all_tables:
            pair_id = table_id // 2
            output["tableTimeslotList"].append({
                "id": timeslot_id,
                "startTime": start_time_minutes,
                "duration": match_duration,
                "table": {
                    "id": table_id,
                    "tablePair": {"id": pair_id}
                },
                "endTime": start_time_minutes + match_duration
            })
            timeslot_id += 1
    
    # Genereer juryTimeslots (voor elke jury, elk tijdslot)
    jury_timeslot_id = 0
    jury_duration = 42  # minuten per jury sessie
    for ts in all_timeslots:
        start_time_minutes = ts * jury_duration
        for jury_id in range(num_table_pairs):
            output["juryTimeslotList"].append({
                "id": jury_timeslot_id,
                "startTime": start_time_minutes,
                "duration": jury_duration,
                "endTime": start_time_minutes + jury_duration,
                "jury": {"id": jury_id}
            })
            jury_timeslot_id += 1
    
    # Bouw teamTableAllocationList - voor elke match
    for team in all_teams:
        for ts in all_timeslots:
            for table_id in all_tables:
                if solver.value(matches[(team, ts, table_id)]):
                    # Vind de juiste tableTimeslot id
                    table_timeslot_id = ts * NUM_TABLES + table_id
                    output["teamTableAllocationList"].append({
                        "team": {"id": team},
                        "timeslot": {"id": table_timeslot_id}
                    })
    
    return output


def save_json(output, filename=None):
    """Sla de output op als JSON bestand"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"schedule-{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Schema opgeslagen als: {filename}")
    return filename


def print_summary(output):
    """Print een samenvatting van het gegenereerde schema"""
    if output is None:
        print("\n❌ GEEN OPLOSSING GEVONDEN!")
        return
    
    num_teams = len(output["teamList"])
    num_tables = len(output["tableList"])
    num_allocations = len(output["teamTableAllocationList"])
    
    print("\n" + "=" * 70)
    print("📊 SCHEMA SAMENVATTING")
    print("=" * 70)
    print(f"Teams: {num_teams}")
    print(f"Tafels: {num_tables}")
    print(f"Tafel pairs: {len(output['tablePairList'])}")
    print(f"Jury's: {len(output['juryList'])}")
    print(f"Totaal wedstrijden: {num_allocations}")
    print(f"Wedstrijden per team: {num_allocations // num_teams}")
    print(f"Score: {output['score']}")
    
    # Analyse per team
    team_matches = {}
    team_tables = {}
    for allocation in output["teamTableAllocationList"]:
        team_id = allocation["team"]["id"]
        timeslot_id = allocation["timeslot"]["id"]
        
        # Zoek welke tafel dit is
        for table_ts in output["tableTimeslotList"]:
            if table_ts["id"] == timeslot_id:
                table_id = table_ts["table"]["id"]
                if team_id not in team_matches:
                    team_matches[team_id] = []
                    team_tables[team_id] = set()
                team_matches[team_id].append((table_ts["startTime"], table_id))
                team_tables[team_id].add(table_id)
                break
    
    print("\n" + "=" * 70)
    print("👥 TEAMS OVERZICHT")
    print("=" * 70)
    
    teams_on_one_table = 0
    teams_on_two_tables = 0
    teams_on_more = 0
    
    for team_id in sorted(team_matches.keys()):
        matches = sorted(team_matches[team_id])
        tables = sorted(team_tables[team_id])
        num_tables = len(tables)
        
        if num_tables == 1:
            teams_on_one_table += 1
        elif num_tables == 2:
            teams_on_two_tables += 1
        else:
            teams_on_more += 1
        
        emoji = "✅" if num_tables <= 2 else "⚠️"
        print(f"Team {team_id:2d}: {num_tables} tafel(s) {emoji} - {[t for t in tables]}")
    
    print(f"\nTeams op 1 tafel: {teams_on_one_table}")
    print(f"Teams op 2 tafels: {teams_on_two_tables}")
    if teams_on_more > 0:
        print(f"Teams op 3+ tafels: {teams_on_more} ⚠️")


if __name__ == "__main__":
    output = create_schedule_json()
    
    if output:
        print_summary(output)
        filename = save_json(output)
        print(f"\n✅ Schema succesvol gegenereerd!")
        print(f"   Bestand: {filename}")
    else:
        print("\n❌ Geen oplossing gevonden!")
        print("\n💡 Probeer:")
        print("   • Verhoog NUM_TIMESLOTS in config.py")
        print("   • Verlaag NUM_TEAMS")
        print("   • Verlaag MIN_GAP_BETWEEN_MATCHES")
