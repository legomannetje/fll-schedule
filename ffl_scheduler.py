"""First Lego League Tournament Scheduling Problem."""
from ortools.sat.python import cp_model


def main() -> None:
    # Data - configureerbaar voor jouw situatie
    num_teams = 12  # Pas aan: 10-40 teams
    num_tables = 6  # Pas aan: 4-10 tafels
    num_timeslots = 8  # Pas aan: 4-10 tijdsloten
    matches_per_team = 4  # Elk team speelt 4 wedstrijden
    min_gap_between_matches = 1  # Minimaal 1 tijdslot tussen wedstrijden
    
    all_teams = range(num_teams)
    all_tables = range(num_tables)
    all_timeslots = range(num_timeslots)
    
    print(f"Planning {num_teams} teams op {num_tables} tafels gedurende {num_timeslots} tijdsloten")
    print(f"Elk team speelt {matches_per_team} wedstrijden\n")

    # Creates the model.
    model = cp_model.CpModel()

    # Creates scheduling variables.
    # matches[(team, timeslot, table)]: team speelt op timeslot op table
    matches = {}
    for team in all_teams:
        for timeslot in all_timeslots:
            for table in all_tables:
                matches[(team, timeslot, table)] = model.new_bool_var(
                    f"team_{team}_t{timeslot}_table{table}"
                )

    # Constraint 1: Elk team speelt precies matches_per_team wedstrijden
    for team in all_teams:
        team_matches = []
        for timeslot in all_timeslots:
            for table in all_tables:
                team_matches.append(matches[(team, timeslot, table)])
        model.add(sum(team_matches) == matches_per_team)

    # Constraint 2: Elke tafel heeft maximaal 1 team per tijdslot
    for timeslot in all_timeslots:
        for table in all_tables:
            model.add_at_most_one(
                matches[(team, timeslot, table)] for team in all_teams
            )

    # Constraint 3: Elk team speelt maximaal 1 wedstrijd per tijdslot
    for team in all_teams:
        for timeslot in all_timeslots:
            model.add_at_most_one(
                matches[(team, timeslot, table)] for table in all_tables
            )

    # Constraint 4: Minimale tijd tussen wedstrijden van hetzelfde team
    # Als een team speelt in tijdslot t, mag het niet spelen in de volgende min_gap tijdsloten
    for team in all_teams:
        for timeslot in range(num_timeslots):
            for next_timeslot in range(timeslot + 1, min(timeslot + 1 + min_gap_between_matches, num_timeslots)):
                # Team mag niet in beide tijdsloten spelen
                plays_at_t = []
                plays_at_next = []
                for table in all_tables:
                    plays_at_t.append(matches[(team, timeslot, table)])
                    plays_at_next.append(matches[(team, next_timeslot, table)])
                # Als team speelt in timeslot, mag het niet spelen in next_timeslot
                model.add(sum(plays_at_t) + sum(plays_at_next) <= 1)

    # Soft constraint: Teams spelen bij voorkeur op dezelfde tafel (of maximaal 2 tafels)
    # We maken variabelen die bijhouden hoeveel verschillende tafels elk team gebruikt
    tables_used = {}
    for team in all_teams:
        for table in all_tables:
            tables_used[(team, table)] = model.new_bool_var(
                f"team_{team}_uses_table{table}"
            )
            # Een tafel wordt gebruikt als het team er minstens 1 wedstrijd speelt
            team_matches_on_table = []
            for timeslot in all_timeslots:
                team_matches_on_table.append(matches[(team, timeslot, table)])
            # tables_used is 1 als er minstens 1 wedstrijd is op deze tafel
            model.add(sum(team_matches_on_table) >= 1).only_enforce_if(
                tables_used[(team, table)]
            )
            model.add(sum(team_matches_on_table) == 0).only_enforce_if(
                tables_used[(team, table)].Not()
            )

    # Aantal verschillende tafels per team
    num_tables_per_team = {}
    for team in all_teams:
        num_tables_per_team[team] = model.new_int_var(
            1, num_tables, f"num_tables_team_{team}"
        )
        model.add(
            num_tables_per_team[team]
            == sum(tables_used[(team, table)] for table in all_tables)
        )
        # Preferentie: maximaal 2 tafels per team (zachte constraint via minimalisatie)
        # We kunnen dit afdwingen als harde constraint of als te minimaliseren doelfunctie

    # Objectieve functie: minimaliseer het totaal aantal verschillende tafels gebruikt door alle teams
    total_table_changes = sum(num_tables_per_team[team] for team in all_teams)
    model.minimize(total_table_changes)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0  # Geef het 30 seconden
    
    status = solver.solve(model)

    # Display solution
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("=" * 80)
        print("SCHEMA GEVONDEN!")
        print("=" * 80)
        
        # Print per tijdslot
        for timeslot in all_timeslots:
            print(f"\nTijdslot {timeslot + 1}:")
            print("-" * 40)
            for table in all_tables:
                for team in all_teams:
                    if solver.value(matches[(team, timeslot, table)]):
                        print(f"  Tafel {table + 1}: Team {team + 1}")
        
        print("\n" + "=" * 80)
        print("OVERZICHT PER TEAM")
        print("=" * 80)
        
        # Print per team
        for team in all_teams:
            print(f"\nTeam {team + 1}:")
            team_schedule = []
            tables_for_team = set()
            for timeslot in all_timeslots:
                for table in all_tables:
                    if solver.value(matches[(team, timeslot, table)]):
                        team_schedule.append((timeslot + 1, table + 1))
                        tables_for_team.add(table + 1)
            
            team_schedule.sort()
            for timeslot, table in team_schedule:
                print(f"  Tijdslot {timeslot}: Tafel {table}")
            print(f"  → Gebruikt {len(tables_for_team)} tafel(s): {sorted(tables_for_team)}")
        
        print("\n" + "=" * 80)
        print("STATISTIEKEN")
        print("=" * 80)
        print(f"Status: {'OPTIMAAL' if status == cp_model.OPTIMAL else 'HAALBAAR'}")
        print(f"Totaal aantal tafelwisselingen: {solver.objective_value}")
        print(f"Oplos tijd: {solver.wall_time:.2f} seconden")
        print(f"Conflicten: {solver.num_conflicts}")
        print(f"Branches: {solver.num_branches}")
        
    else:
        print("Geen oplossing gevonden!")
        print("Probeer:")
        print("  - Meer tijdsloten toe te voegen")
        print("  - Minder teams")
        print("  - De gap tussen wedstrijden te verkleinen")


if __name__ == "__main__":
    main()
