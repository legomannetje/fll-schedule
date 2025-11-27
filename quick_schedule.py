"""
FLL Scheduler - Quick Run Script
Gebruik dit script om snel een schema te genereren met command-line parameters
"""
import argparse
from ortools.sat.python import cp_model
import json
from datetime import datetime


def create_schedule(num_teams, num_tables, num_timeslots, matches_per_team=4, min_gap=1, max_time=60):
    """Maakt een FLL wedstrijdschema"""
    
    all_teams = range(num_teams)
    all_tables = range(num_tables)
    all_timeslots = range(num_timeslots)
    
    print(f"\n🏆 FLL TOURNAMENT SCHEDULER")
    print(f"=" * 70)
    print(f"Teams: {num_teams} | Tafels: {num_tables} | Tijdsloten: {num_timeslots}")
    print(f"Wedstrijden per team: {matches_per_team}")
    print(f"Minimale gap tussen wedstrijden: {min_gap} tijdslot(en)")
    print(f"=" * 70 + "\n")

    # Controle
    total_matches_needed = num_teams * matches_per_team
    max_matches_available = num_timeslots * num_tables
    
    if total_matches_needed > max_matches_available:
        print(f"⚠️  FOUT: Onvoldoende capaciteit!")
        print(f"   {total_matches_needed} wedstrijden nodig, maar slechts {max_matches_available} slots beschikbaar")
        print(f"   Verhoog tijdsloten naar minimaal {(total_matches_needed + num_tables - 1) // num_tables}")
        return None

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
    for team in all_teams:
        model.add(sum(matches[(team, ts, tb)] 
                     for ts in all_timeslots 
                     for tb in all_tables) == matches_per_team)

    for timeslot in all_timeslots:
        for table in all_tables:
            model.add_at_most_one(matches[(team, timeslot, table)] 
                                 for team in all_teams)

    for team in all_teams:
        for timeslot in all_timeslots:
            model.add_at_most_one(matches[(team, timeslot, table)] 
                                 for table in all_tables)

    for team in all_teams:
        for ts in range(num_timeslots):
            for next_ts in range(ts + 1, min(ts + 1 + min_gap, num_timeslots)):
                model.add(sum(matches[(team, ts, tb)] for tb in all_tables) +
                         sum(matches[(team, next_ts, tb)] for tb in all_tables) <= 1)

    # Optimalisatie
    tables_used = {}
    for team in all_teams:
        for table in all_tables:
            tables_used[(team, table)] = model.new_bool_var(f"t{team}_uses_tb{table}")
            team_matches_on_table = [matches[(team, ts, table)] for ts in all_timeslots]
            model.add(sum(team_matches_on_table) >= 1).only_enforce_if(tables_used[(team, table)])
            model.add(sum(team_matches_on_table) == 0).only_enforce_if(tables_used[(team, table)].Not())

    model.minimize(sum(tables_used[(team, table)] for team in all_teams for table in all_tables))

    # Oplossen
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time
    
    print("🔍 Bezig met zoeken naar optimale oplossing...")
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return {
            'solver': solver,
            'matches': matches,
            'status': status,
            'num_teams': num_teams,
            'num_tables': num_tables,
            'num_timeslots': num_timeslots,
            'matches_per_team': matches_per_team
        }
    return None


def export_json(result, filename=None):
    """Exporteer naar JSON formaat"""
    if result is None:
        return None
    
    solver = result['solver']
    matches = result['matches']
    num_teams = result['num_teams']
    num_tables = result['num_tables']
    num_timeslots = result['num_timeslots']
    
    output = {
        "constraintConfiguration": {
            "constraintWeight": "1hard/0medium/0soft",
            "minimumBreakDuration": 27,
            "startTime": "09:30",
            "breakStartTime": 168,
            "breakDuration": 30,
            "matchDuration": 7,
            "juryDuration": 42
        },
        "tableList": [],
        "tablePairList": [],
        "juryList": [],
        "teamList": [],
        "tableTimeslotList": [],
        "juryTimeslotList": [],
        "teamTableAllocationList": [],
        "score": "0hard/0medium/0soft" if result['status'] == cp_model.OPTIMAL else "1hard/0medium/0soft"
    }
    
    num_table_pairs = (num_tables + 1) // 2
    for pair_id in range(num_table_pairs):
        output["tablePairList"].append({"id": pair_id})
    
    for table_id in range(num_tables):
        pair_id = table_id // 2
        output["tableList"].append({"id": table_id, "tablePair": {"id": pair_id}})
    
    for jury_id in range(num_table_pairs):
        output["juryList"].append({"id": jury_id})
    
    for team_id in range(num_teams):
        output["teamList"].append({"id": team_id})
    
    timeslot_id = 0
    for ts in range(num_timeslots):
        start_time = ts * 7
        for table_id in range(num_tables):
            output["tableTimeslotList"].append({
                "id": timeslot_id,
                "startTime": start_time,
                "duration": 7,
                "table": {"id": table_id, "tablePair": {"id": table_id // 2}},
                "endTime": start_time + 7
            })
            timeslot_id += 1
    
    jury_timeslot_id = 0
    for ts in range(num_timeslots):
        start_time = ts * 42
        for jury_id in range(num_table_pairs):
            output["juryTimeslotList"].append({
                "id": jury_timeslot_id,
                "startTime": start_time,
                "duration": 42,
                "endTime": start_time + 42,
                "jury": {"id": jury_id}
            })
            jury_timeslot_id += 1
    
    for team in range(num_teams):
        for ts in range(num_timeslots):
            for table_id in range(num_tables):
                if solver.value(matches[(team, ts, table_id)]):
                    table_timeslot_id = ts * num_tables + table_id
                    output["teamTableAllocationList"].append({
                        "team": {"id": team},
                        "timeslot": {"id": table_timeslot_id}
                    })
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"schedule-{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    return filename


def print_summary(result):
    """Print samenvatting"""
    if result is None:
        print("\n❌ GEEN OPLOSSING GEVONDEN!")
        return
    
    solver = result['solver']
    matches = result['matches']
    num_teams = result['num_teams']
    num_tables = result['num_tables']
    num_timeslots = result['num_timeslots']
    
    team_tables = {}
    for team in range(num_teams):
        team_tables[team] = set()
        for ts in range(num_timeslots):
            for table in range(num_tables):
                if solver.value(matches[(team, ts, table)]):
                    team_tables[team].add(table)
    
    print("\n" + "=" * 70)
    print("📊 RESULTAAT")
    print("=" * 70)
    print(f"Status: {'OPTIMAAL ✅' if result['status'] == cp_model.OPTIMAL else 'HAALBAAR ⚠️'}")
    print(f"Oplostijd: {solver.wall_time:.2f} seconden")
    
    teams_1_table = sum(1 for tables in team_tables.values() if len(tables) == 1)
    teams_2_tables = sum(1 for tables in team_tables.values() if len(tables) == 2)
    teams_more = num_teams - teams_1_table - teams_2_tables
    
    print(f"\nTeams op 1 tafel: {teams_1_table}")
    print(f"Teams op 2 tafels: {teams_2_tables}")
    if teams_more > 0:
        print(f"Teams op 3+ tafels: {teams_more} ⚠️")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FLL Tournament Scheduler')
    parser.add_argument('--teams', type=int, default=12, help='Aantal teams (10-40)')
    parser.add_argument('--tables', type=int, default=6, help='Aantal tafels (4-10)')
    parser.add_argument('--timeslots', type=int, default=8, help='Aantal tijdsloten (4-20)')
    parser.add_argument('--matches', type=int, default=4, help='Wedstrijden per team')
    parser.add_argument('--gap', type=int, default=1, help='Min. tijdsloten tussen wedstrijden')
    parser.add_argument('--time', type=int, default=60, help='Max. oplostijd in seconden')
    parser.add_argument('--output', type=str, help='Output bestandsnaam')
    parser.add_argument('--json', action='store_true', help='Genereer JSON output')
    
    args = parser.parse_args()
    
    result = create_schedule(
        args.teams,
        args.tables,
        args.timeslots,
        args.matches,
        args.gap,
        args.time
    )
    
    if result:
        print_summary(result)
        if args.json:
            filename = export_json(result, args.output)
            print(f"\n💾 JSON opgeslagen als: {filename}")
    else:
        print("\n💡 Probeer:")
        print("   • --timeslots verhogen")
        print("   • --teams verlagen")
        print("   • --gap verkleinen")
