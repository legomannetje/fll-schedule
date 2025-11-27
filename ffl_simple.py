"""Eenvoudige versie - First Lego League Tournament Scheduler
Experimenteer met deze versie voor kleinere toernooien.
"""
from ortools.sat.python import cp_model


def create_schedule(num_teams=12, num_tables=6, num_timeslots=8, min_gap=1):
    """
    Maakt een FLL wedstrijdschema.
    
    Args:
        num_teams: Aantal teams (10-40)
        num_tables: Aantal tafels (4-10)
        num_timeslots: Aantal tijdsloten (4-10)
        min_gap: Minimaal aantal tijdsloten tussen wedstrijden (standaard 1)
    
    Returns:
        Dictionary met het schema of None als geen oplossing gevonden
    """
    matches_per_team = 4
    
    all_teams = range(num_teams)
    all_tables = range(num_tables)
    all_timeslots = range(num_timeslots)
    
    print(f"\n🏆 Planning {num_teams} teams op {num_tables} tafels")
    print(f"   {num_timeslots} tijdsloten, elk team speelt {matches_per_team}x\n")

    model = cp_model.CpModel()

    # Variabelen: matches[(team, timeslot, table)]
    matches = {}
    for team in all_teams:
        for timeslot in all_timeslots:
            for table in all_tables:
                matches[(team, timeslot, table)] = model.new_bool_var(
                    f"t{team}_ts{timeslot}_tb{table}"
                )

    # 1. Elk team speelt precies 4 wedstrijden
    for team in all_teams:
        model.add(sum(matches[(team, ts, tb)] 
                     for ts in all_timeslots 
                     for tb in all_tables) == matches_per_team)

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
        for ts in range(num_timeslots):
            for next_ts in range(ts + 1, min(ts + 1 + min_gap, num_timeslots)):
                model.add(sum(matches[(team, ts, tb)] for tb in all_tables) +
                         sum(matches[(team, next_ts, tb)] for tb in all_tables) <= 1)

    # 5. Soft: Teams bij voorkeur op dezelfde tafel
    tables_used = {}
    for team in all_teams:
        for table in all_tables:
            tables_used[(team, table)] = model.new_bool_var(f"t{team}_uses_tb{table}")
            team_matches_on_table = [matches[(team, ts, table)] for ts in all_timeslots]
            model.add(sum(team_matches_on_table) >= 1).only_enforce_if(
                tables_used[(team, table)])
            model.add(sum(team_matches_on_table) == 0).only_enforce_if(
                tables_used[(team, table)].Not())

    # Minimaliseer totaal aantal gebruikte tafels per team
    model.minimize(sum(tables_used[(team, table)] 
                      for team in all_teams 
                      for table in all_tables))

    # Oplossen
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Bouw het schema
        schedule = {}
        team_info = {}
        
        for timeslot in all_timeslots:
            schedule[timeslot] = {}
            for table in all_tables:
                for team in all_teams:
                    if solver.value(matches[(team, timeslot, table)]):
                        schedule[timeslot][table] = team
        
        for team in all_teams:
            team_matches = []
            team_tables = set()
            for ts in all_timeslots:
                for tb in all_tables:
                    if solver.value(matches[(team, ts, tb)]):
                        team_matches.append((ts, tb))
                        team_tables.add(tb)
            team_info[team] = {
                'matches': sorted(team_matches),
                'tables': sorted(team_tables)
            }
        
        return {
            'schedule': schedule,
            'team_info': team_info,
            'optimal': status == cp_model.OPTIMAL,
            'solve_time': solver.wall_time
        }
    else:
        return None


def print_schedule(result):
    """Print het schema op een overzichtelijke manier."""
    if result is None:
        print("❌ Geen oplossing gevonden!")
        print("\nProbeer:")
        print("  • Meer tijdsloten")
        print("  • Minder teams")
        print("  • Kleinere gap tussen wedstrijden")
        return
    
    schedule = result['schedule']
    team_info = result['team_info']
    
    print("=" * 70)
    print("📅 WEDSTRIJDSCHEMA PER TIJDSLOT")
    print("=" * 70)
    
    for timeslot in sorted(schedule.keys()):
        print(f"\n⏰ Tijdslot {timeslot + 1}:")
        tables_with_teams = schedule[timeslot]
        if tables_with_teams:
            for table in sorted(tables_with_teams.keys()):
                team = tables_with_teams[table]
                print(f"   Tafel {table + 1:2d} → Team {team + 1:2d}")
        else:
            print("   (geen wedstrijden)")
    
    print("\n" + "=" * 70)
    print("👥 PLANNING PER TEAM")
    print("=" * 70)
    
    for team in sorted(team_info.keys()):
        info = team_info[team]
        print(f"\n🏁 Team {team + 1}:")
        for ts, tb in info['matches']:
            print(f"   Tijdslot {ts + 1:2d} → Tafel {tb + 1:2d}")
        num_tables = len(info['tables'])
        tables_list = [tb + 1 for tb in info['tables']]
        emoji = "✅" if num_tables <= 2 else "⚠️"
        print(f"   {emoji} Gebruikt {num_tables} tafel(s): {tables_list}")
    
    print("\n" + "=" * 70)
    print("📊 STATISTIEKEN")
    print("=" * 70)
    status_text = "OPTIMAAL ✅" if result['optimal'] else "HAALBAAR ⚠️"
    print(f"Status: {status_text}")
    print(f"Oplostijd: {result['solve_time']:.2f} seconden")
    
    # Bereken gemiddeld aantal tafels per team
    avg_tables = sum(len(info['tables']) for info in team_info.values()) / len(team_info)
    print(f"Gemiddeld aantal tafels per team: {avg_tables:.2f}")
    
    teams_on_one_table = sum(1 for info in team_info.values() if len(info['tables']) == 1)
    teams_on_two_tables = sum(1 for info in team_info.values() if len(info['tables']) == 2)
    print(f"Teams op 1 tafel: {teams_on_one_table}")
    print(f"Teams op 2 tafels: {teams_on_two_tables}")
    print(f"Teams op 3+ tafels: {len(team_info) - teams_on_one_table - teams_on_two_tables}")


if __name__ == "__main__":
    # Pas deze waarden aan voor jouw toernooi!
    result = create_schedule(
        num_teams=12,      # 10-40 teams
        num_tables=6,      # 4-10 tafels
        num_timeslots=8,   # 4-10 tijdsloten
        min_gap=1          # Minimaal 1 tijdslot tussen wedstrijden
    )
    
    print_schedule(result)
