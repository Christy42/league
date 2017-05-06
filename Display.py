import os
import yaml
import league_structure


def display_team(team_name):
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_id.yaml") as file:
        result = yaml.safe_load(file)[team_name]
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + result + ".yaml") as team_file:
        team = yaml.safe_load(team_file)
    print("Team Name: " + team["team name"])
    print("Nationality: " + team["nationality"])
    print("Total Salary: " + str(team["salary"]))
    print("Draft Picks available: " + str(team["draft picks"]))
    for player in team["player"]:
        print(player + ": " + team["player"][player])
    print("trophies: " + str(team["trophies"]))
    print("current league: " + team["leagues name"])


def display_player(player_name):
    with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player_name + ".yaml") as player_file:
        player = yaml.safe_load(player_file)
    print("name: " + player["name"] + "  age: " + str(player["age"]) + "  nationality: " + player["nationality"] +
          " salary: " + str(player["contract_value"]) + "  years left: " + str(player["years_left"]) +
          "  guaranteed: " + str(player["guarantee"]) + "%")
    print("Height: " + str(player["height"]) + "  Weight: " + str(int(round(player["weight"], 0))) +
          " Team: " + player["team"])
    with open(os.environ['FOOTBALL_HOME'] + "//players//ref//player_stats.yaml") as stat_file:
        attributes = yaml.safe_load(stat_file)
    count = 0
    attribs = []
    colours = []
    for attribute in attributes["low attributes"]:
        if player[attribute + "_max"] > 900:
            colours.append(32)
        elif player[attribute + "_max"] > 800:
            colours.append(33)
        elif player[attribute + "_max"] > 700:
            colours.append(31)
        else:
            colours.append(37)
        attribs.append(attribute)
        if count == 3:
            print(attribs[0] + "\033[1;" + str(colours[0]) + ";0m " + str(int(round(player[attribs[0]] / 10, 0))) +
                  "\033[1;37;0m " +
                  attribs[1] + "\033[1;" + str(colours[1]) + ";0m " + str(int(round(player[attribs[1]] / 10, 0))) +
                  "\033[1;37;0m " +
                  attribs[2] + "\033[1;" + str(colours[2]) + ";0m " + str(int(round(player[attribs[2]] / 10, 0))) +
                  "\033[1;37;0m " +
                  attribs[3] + "\033[1;" + str(colours[3]) + ";0m " + str(int(round(player[attribs[3]] / 10, 0))) +
                  "\033[1;37;0m ")
            count = -1
            attribs = []
            colours = []
        count += 1
    exp_display = input("Do you want to display players positional and route experience? Y for yes.")
    if exp_display == "Y" or exp_display == "y":
        display_player_exp(player, attributes)


def display_player_exp(player, attributes):
    positions = []
    colours = []
    count = 0
    for position in attributes["positional attributes"]:
        positions.append(position)
        if player[position] > 400:
            colours.append(32)
        elif player[position] > 300:
            colours.append(33)
        elif player[position] > 200:
            colours.append(31)
        else:
            colours.append(37)
        if count == 5:
            count = -1
            print(positions[0] + ": " + "\033[1;" + str(colours[0]) + ";0m " +
                  str(int(round(player[positions[0]], 0))) + "  " + "\033[1;37;0m " +
                  positions[1] + ": " + "\033[1;" + str(colours[1]) + ";0m " +
                  str(int(round(player[positions[1]], 0))) + "  " + "\033[1;37;0m " +
                  positions[2] + ": " + "\033[1;" + str(colours[2]) + ";0m " +
                  str(int(round(player[positions[2]], 0))) + "  " + "\033[1;37;0m " +
                  positions[3] + ": " + "\033[1;" + str(colours[3]) + ";0m " +
                  str(int(round(player[positions[3]], 0))) + "  " + "\033[1;37;0m " +
                  positions[4] + ": " + "\033[1;" + str(colours[4]) + ";0m " +
                  str(int(round(player[positions[4]], 0))) + "  " + "\033[1;37;0m " +
                  positions[5] + ": " + "\033[1;" + str(colours[5]) + ";0m " +
                  str(int(round(player[positions[5]], 0))) + "  " + "\033[1;37;0m")
            positions = []
            colours = []
        count += 1


def amend_player_training(player):
    display_player(player)
    with open(os.environ['FOOTBALL_HOME'] + "//players//ref//player_stats.yaml", "r") as stat_file:
        attributes = yaml.safe_load(stat_file)
    with open(os.environ['FOOTBALL_HOME'] + "//players//training//" + player + ".yaml", "r") as training_file:
        training = yaml.safe_load(training_file)
    print("focus: " + training["focus"] + "route assignment: " + training["route assignment"] +
          " weight direction: " + training["weight direction"])
    change = input("Hit Y if you wish to change the training regime for this player?")
    focus = weight_direction = route_assignment = "b"
    if change == "Y" or change == "y":
        while focus not in attributes["low attributes"] + [""]:
            print(attributes["low attributes"] + [""])
            focus = input("Enter a new focus for this players training")
        while weight_direction not in ["up", "down", ""]:
            print(["up", "down", ""])
            weight_direction = input("Enter in the direction you want this players weight to go")
        while route_assignment not in attributes["routeFormation attributes"] + [""]:
            print(attributes["routeFormation attributes"] + [""])
            route_assignment = input("Enter in the route you wish this player to train with")
        training["focus"] = focus
        training["weight_direction"] = weight_direction
        training["route_assignment"] = route_assignment
        with open(os.environ['FOOTBALL_HOME'] + "//players//training//" + player + ".yaml", "w") as training_file:
            yaml.safe_dump(training, training_file)


def amend_team_formation(team_name):
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_id.yaml", "r") as file:
        result = yaml.safe_load(file)[team_name]
    with open(os.environ['FOOTBALL_HOME'] + "//formations_config//test_yaml_formation.yaml", "r") as formation_file:
        offense_formations = yaml.safe_load(formation_file)
    with open(os.environ['FOOTBALL_HOME'] + "//formations_config//test_yaml_defense_formation.yaml", "r") as \
            formation_file:
        defense_formations = yaml.safe_load(formation_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//orders//" + str(result) + "-formation.yaml") as formation_file:
        team_formation = yaml.safe_load(formation_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + str(result) + ".yaml") as team_file:
        team = yaml.safe_load(team_file)

    formation = "b"
    while formation != "":
        print(list(offense_formations.keys()))
        print(list(defense_formations.keys()))
        formation = "b"
        while formation not in list(offense_formations.keys()) + [""] + list(defense_formations.keys()):
            formation = input("Enter the formation you wish to change or hit enter to move on")
        if formation != "":
            if formation in list(offense_formations.keys()):
                position_list = [offense_formations[formation]["positions"][i].replace("_exp", "") + " " + str(i + 1)
                                 for i in range(11)]
            else:
                position_list = [defense_formations[formation]["positions"][i].replace("_exp", "") + " " + str(i + 1)
                                 for i in range(11)]

            position = "b"
            while position != "":
                position = "b"
                for i in range(11):
                    print(position_list[i] + " " + team["player"][team_formation[formation][i]])

                while position not in position_list + [""]:
                    position = input("Enter the position you wish to replace")  # This method won't work
                player = position
                while player not in list(team["player"].keys()) + [""]:
                    print(list(team["player"].keys()))
                    player = input("Enter player id to replace him")
                team_formation[formation] = [player if position == position_list[i] else team_formation[formation][i]
                                             for i in range(11)]
    with open(os.environ['FOOTBALL_HOME'] + "//teams//orders//" + str(result) + "-formation.yaml", "w") as \
            formation_file:
        yaml.safe_dump(team_formation, formation_file)
        # TODO: Need to ensure we don't end up with duplicates
        # TODO: Have kick return referred to twice
        # TODO: Potentially allow to change all formations at once


def amend_team_draft_aims(team_name):
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_id.yaml", "r") as file:
        result = yaml.safe_load(file)[team_name]
    with open(os.environ['FOOTBALL_HOME'] + "//teams//scouting//scouts-" + str(result) + ".yaml", "r") as team_file:
        scouts = yaml.safe_load(team_file)
    if scouts["ideal_height"] < 0:
        scouts["ideal_height"] = ""
    if scouts["ideal_weight"] < 0:
        scouts["ideal_weight"] = ""
    ideal_height = input("Enter in what height you wish your scouts to aim for, if you don't care hit enter")
    ideal_weight = input("Enter in what weight you wish your scouts to aim for, if you don't care hit enter")
    attributes = []
    for _ in range(3):
        attributes.append(input("Enter the next attribute you want the scouts to search for, enter for no opinion"))
    # TODO: Ask if you want to amend and if so get in values
    scouts["ideal_height"] = ideal_height
    scouts["ideal_weight"] = ideal_weight
    scouts["attributes"] = attributes
    with open(os.environ['FOOTBALL_HOME'] + "//teams//scouting//scouts-" + str(result) + ".yaml", "w") as team_file:
        yaml.safe_dump(scouts, team_file)


def amend_team_orders_offense(team):
    pass


def amend_team_orders_defense(team):
    pass


def show_game_schedule(team_name, week=1):
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_id.yaml", "r") as file:
        result = yaml.safe_load(file)[team_name]
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + str(result) + ".yaml") as team_file:
        team = yaml.safe_load(team_file)
    league = team["leagues name"]
    with open(os.environ['FOOTBALL_HOME'] + "//leagues//season_number.yaml", "r") as season_file:
        season_number = yaml.safe_load(season_file)
    with open(os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number) + "//" +
              str(ord(league[0]) - 96) + "//" + league + "//" + "schedule.yaml", "r") as league_file:
        matches = yaml.safe_load(league_file)
    team_matches = []
    for rounds in matches:
        for match in matches[rounds]:
            if result in matches[rounds][match] and rounds >= week:
                team_matches.append(matches[rounds][match])
    with open(os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number) + "//cup_fixtures.yaml", "r") \
            as cup_file:
        cup_matches = yaml.safe_load(cup_file)
    if result in cup_matches:
        cup_round = cup_matches[0]
        with open(os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number) + "//round_" + str(cup_round) +
                  ".yaml", "r") as round_file:
            round_matches = yaml.safe_load(round_file)
        for match in round_matches:
            if result in match:
                team_matches.append(match)
    final_matches = []
    for i in range(len(team_matches)):
        name = []
        for team in team_matches[i]:
            if team == "BYE":
                name.append("BYE")
            else:
                with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + team + ".yaml", "r") as team_file:
                    name.append(yaml.safe_load(team_file)["team name"])
        final_matches.append([name])
    for i in range(len(final_matches)):
        print(final_matches[i][0][0] + "  vs  " + final_matches[i][0][1])
    # TODO: order them properly (how could I possibly get dates and times in)?


def amend_team_order(team_name):
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_id.yaml", "r") as file:
        result = yaml.safe_load(file)[team_name]
    with open(os.environ['FOOTBALL_HOME'] + "//teams//orders//" + result + "-orders.yaml", "r") as order_file:
        orders = yaml.safe_load(order_file)
    time_between_plays = 45
    field_goal_range = -1
    while int(time_between_plays) not in range(10, 40):
        time_between_plays = input("please enter how long you want your team to take between plays")

    while int(field_goal_range) < 0:
        field_goal_range = input("please enter how far away you want to take field goals from on 4th down")
    special = {"field goal range": field_goal_range, "time between plays": time_between_plays}
    orders_to_change = "b"
    while orders_to_change != "":
        orders_to_change = input("Do you wish change offense or defense?  Hit enter to finish")
        while orders_to_change not in ["offense", "defense", ""]:
            orders_to_change = input("Do you wish change offense or defense?  Hit enter to finish")
        if orders_to_change != "":
            style = "defense_" if orders_to_change == "defense" else ""
            base_folder = os.environ['FOOTBALL_HOME'] + "//plays_config//" + orders_to_change + "_plays"

            with open(os.environ['FOOTBALL_HOME'] + "//formations_config//test_yaml_" + style + "formation.yaml") \
                    as file:
                formations = list(yaml.safe_load(file).keys())
            current_formation = {}
            formation_amount = {}
            if "punting" in formations:
                formations.remove("punting")
                formations.remove("kick off")
                formations.remove("kick return")
            for formation in formations:
                current_formation[formation.lower().replace(" ", "_").replace("-", "_")] = []
                formation_amount[formation.lower().replace(" ", "_").replace("-", "_")] = {}
            for file in os.listdir(base_folder):
                with open(base_folder + "//" + file) as play_file:
                    plays = list(yaml.safe_load(play_file).keys())
                formation = file[:-5]
                formation = formation[15 + len(style):]
                current_formation[formation].append(plays)
            play_form = "f"
            if orders_to_change == "offense":
                skip = 2
            else:
                skip = 0
            print(orders[orders_to_change])
            for play in orders[orders_to_change]:
                print(play)
                for form in current_formation:
                    print(form)
                    if play[skip:] in current_formation[form][0] or play[skip + 1:] in current_formation[form][0]:
                        print("here")
                        play_form = form
                for element in orders[orders_to_change][play]:
                    if element not in list(formation_amount[play_form].keys()):
                        formation_amount[play_form][element] = 0
                    formation_amount[play_form][element] += orders[orders_to_change][play][element] * (not element == 4)
            # for form in formation_amount:
            #     formation_amount[form] /= (len(orders[orders_to_change][play]) -
            #                                (4 in list(orders[orders_to_change][play].keys())))
            for formation in formation_amount:
                print(formation + ": " + str(formation_amount[formation]))
            new_amounts = formation_amount
            sum_play = {}
            while True:
                for formation in new_amounts:
                    for part in new_amounts[formation]:
                        new_amounts[formation][part] = int(input("Please enter new % of plays to be run from " +
                                                                 formation + " for down " + str(part)))
                        if part in list(sum_play.keys()):
                            sum_play[part] += new_amounts[formation][part]
                        else:
                            sum_play[part] = new_amounts[formation][part]
                if list(sum_play.values()) == [100 for _ in range(len(sum_play))]:
                    break
            play_amounts = orders
            for formation_change in list(formation_amount.keys()):
                formation_amount = dict(new_amounts[formation_change])
                for element in formation_amount:
                    formation_amount[element] = 0
                list_of_plays = []
                print(current_formation[formation_change])
                for play in orders[orders_to_change]:

                    if play[skip:] in current_formation[formation_change][0] and \
                                    play[skip:] not in ["kicking", "punting", "kick off", "kick return"]:\
                            # and play[skip:] not in list_of_plays and \

                        print(play + ": " + str(orders[orders_to_change][play]))
                        print("total for formation = " + str(new_amounts[formation_change]))
                        list_of_plays.append(play[skip:])
                        print("current: " + str(formation_amount))
                        for down in orders[orders_to_change][play]:
                            play_amounts[orders_to_change][play][down] = 999
                            while play_amounts[orders_to_change][play][down] > new_amounts[formation_change][down] - \
                                    formation_amount[down]:
                                if str(formation_amount) == str(new_amounts[formation_change]):
                                    play_amounts[orders_to_change][play][down] = 0
                                else:
                                    play_amounts[orders_to_change][play][down] = \
                                        int(input("output how often you want to be for play {} and down {}"
                                                  .format(play, down)))
                                if play_amounts[orders_to_change][play][down] == '':
                                    play_amounts[orders_to_change][play][down] = 0
                            # if play_amounts[orders_to_change][play][down] < 0:
                            #     break
                            formation_amount[down] = int(formation_amount[down]) + \
                                int(play_amounts[orders_to_change][play][down])
                    # if str(formation_amount) == str(new_amounts[formation_change]):
                    #     break
                # write plays
                orders["special"] = special
                orders[orders_to_change] = play_amounts[orders_to_change]
                with open(os.environ['FOOTBALL_HOME'] + "//teams//orders//" + result + "-orders.yaml", "w") as file:
                    yaml.safe_dump(orders, file)


def play_week(week, season_no):
    league_structure.play_week(week + 1, str(season_no))
play_week(0, 0)
