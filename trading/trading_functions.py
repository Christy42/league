import os
import yaml
import datetime

import create_team


def add_player_to_trade(player, min_bid):
    with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player + ".yaml", "r") as player_file:
        player_stats = yaml.safe_load(player_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_id.yaml") as team_file:
        team = yaml.safe_load(team_file)[player_stats["team"]]
    print_stats = {"current bid": {"team": team, "bid": max(min_bid - 1, 0)}, "create_time": datetime.datetime.now()}
    max_exp = 0
    exp_style = ""
    for stat in player_stats:
        if "max" not in stat and "exp" not in stat:
            print_stats[stat] = player_stats[stat]
        if "exp" in stat and player_stats[stat] > max_exp:
            max_exp = player_stats[stat]
            print_stats[stat] = player_stats[stat]
            if exp_style != "":
                print_stats.pop(exp_style)
            if exp_style != "":
                exp_style = stat
    # TODO:  Needs to look up positional stats and pick between them to avoid formation/route exp
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + player + ".yaml", "w") as trading_file:
        yaml.safe_dump(print_stats, trading_file)


def trade_decisions():
    for file in os.listdir(os.environ['FOOTBALL_HOME'] + "//trading//trades"):
        with open(os.environ['FOOTBALL_HOME'] + "//trading//" + file, "r") as trading_file:
            file_stats = yaml.safe_load(trading_file)
        if (datetime.datetime.now() - file_stats["create_time"]).days >= 2:
            new_team = file_stats["current bid"]["team"]
            old_team = file_stats["team"]
            if new_team != old_team:
                result = create_team.add_player_old(new_team, file[7:-5],
                                                    os.environ["MAX_TEAM"], os.environ["MAX_SALARY"])
                if result:
                    create_team.remove_player(file[7:-5], old_team, os.environ["MIN_TEAM"], force_trade=True)
                    with open(os.environ['FOOTBALL_HOME'] + "teams//teams//Team_" + old_team + ".yaml", "r") as \
                            team_file:
                        team_stats = yaml.safe_load(team_file)
                    for _ in range(file_stats["current bid"]["bid"] - 1):
                        team_stats["draft picks"].append(11)
                    with open(os.environ['FOOTBALL_HOME'] + "teams//teams//Team_" + old_team + ".yaml", "w") as \
                            team_file:
                        yaml.safe_dump(team_stats, team_file)

            os.remove(os.environ['FOOTBALL_HOME'] + "//trading//" + file)


def add_bid(player_id, team_id, bid):
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//Player_" + str(player_id) + ".yaml", "r") as \
            trading_file:
        trading_stats = yaml.safe_load(trading_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//Team_" + str(team_id) + ".yaml", "r") as team_file:
        team_stats = yaml.safe_load(team_file)
    old_team = trading_stats["current bid"]["team"]
    old_bid = trading_stats["current bid"]["bid"]
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + old_team + ".yaml", "r") as old_team_file:
        old_team_stats = yaml.safe_load(old_team_file)
    if len([picks for picks in team_stats["draft picks"] if picks == 11]) >= bid > trading_stats["current bid"]["bid"]:
        trading_stats["current bid"]["bid"] = bid
        trading_stats["current bid"]["team"] = team_id
        for _ in range(bid):
            team_stats["draft picks"].remove(11)
        for _ in range(old_bid):
            old_team_stats["draft picks"].append(11)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//Team_" + str(team_id) + ".yaml", "w") as team_file:
        yaml.safe_dump(team_stats, team_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + old_team + ".yaml", "w") as old_team_file:
        yaml.safe_dump(old_team_stats, old_team_file)
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//Player_" + str(player_id) + ".yaml", "w") as \
            trading_file:
        yaml.safe_dump(trading_stats, trading_file)


def view_all_bids(condition_stat, condition, greater_than):
    loading_details = {}
    for file in os.listdir(os.environ['FOOTBALL_HOME'] + "//trading//trades"):
        with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + file, "r") as trade_file:
            trade_details = yaml.safe_load(trade_file)
        if (trade_details[condition_stat] >= condition and greater_than) or \
                (not greater_than and trade_details[condition_stat] <= condition):
            loading_details[file[7: -5]] = {"name": trade_details["name"], "age": trade_details["age"],
                                            "team": trade_details["team"],
                                            "max bid": trade_details["current bid"]["bid"],
                                            "bid team": trade_details["current bid"]["team"]}
    return loading_details


def view_bid(player_id):
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//Player_" + str(player_id) + ".yaml", "r") as trade_file:
        trade = yaml.safe_load(trade_file)
    print(trade)


def trade_picks(number, type_traded, type_desired, team_id):
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trade_values.yaml", "r") as value_file:
        trade_value = yaml.safe_load(value_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//Team_" + str(team_id) + ".yaml", "r") as team_file:
        team_stats = yaml.safe_load(team_file)
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trade_count.yaml", "r") as count_file:
        count = yaml.safe_load(count_file)
    value = 0
    for j in range(len(type_traded)):
        number[j] = min(number[j], len([pick for pick in team_stats["draft picks"] if pick == type_traded[j]]))
        value += number[j] * trade_value[type_traded[j]]
        for i in range(number[j]):
            team_stats["draft picks"].remove(type_traded[j])
        count[type_traded[j]]["sold"] += number[j]
    amount_gained = int(value / trade_value[type_desired])
    print("Do you want to trade")
    for i in range(len(type_traded)):
        print("{} Week {} draft picks".format(number[i], type_traded[i]))
    print("for {} Week {} draft picks?".format(amount_gained, type_desired))
    for i in range(amount_gained):
        team_stats["draft picks"].append(type_desired)

    count[type_desired]["bought"] += amount_gained
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trade_count.yaml", "w") as count_file:
        yaml.safe_dump(count, count_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//Team_" + str(team_id) + ".yaml", "w") as team_file:
        yaml.safe_dump(team_stats, team_file)


def update_prices():
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trade_values.yaml", "r") as value_file:
        trade_value = yaml.safe_load(value_file)
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trade_count.yaml", "r") as count_file:
        count = yaml.safe_load(count_file)
    count_reset = {1: {"bought": 0, "sold": 0}, 2: {"bought": 0, "sold": 0}, 3: {"bought": 0, "sold": 0},
                   4: {"bought": 0, "sold": 0}, 5: {"bought": 0, "sold": 0}, 6: {"bought": 0, "sold": 0},
                   7: {"bought": 0, "sold": 0}, 8: {"bought": 0, "sold": 0}, 9: {"bought": 0, "sold": 0},
                   10: {"bought": 0, "sold": 0}, 11: {"bought": 0, "sold": 0}}
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trade_count.yaml", "w") as count_file:
        yaml.safe_dump(count_reset, count_file)
    for val in count:
        if count[val]["bought"] != count[val]["sold"]:
            max_up = min(500, 10 * abs(count["bought"] - count["sold"]))
            change = min(count[val]["bought"] / (count[val]["bought"] + count[val]["sold"]) + 0.5, max_up)
            change = count[val] - int(max(change, -max_up)) * count[val]
            trade_value[val] -= change
    # =INT(MAX(MIN(B3-B3*(D3/(D3+E3)+0.5); 500;ABS(D3-E3)*10);-500;-ABS(D3-E3)*10))
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trade_values.yaml", "2") as value_file:
        yaml.safe_dump(trade_value, value_file)


def sort_active_bids(minimum_team, maximum_team, salary_limit):
    for file in os.listdir(os.environ["FOOTBALL_HOME"] + "//trading//trades"):
        with open(os.environ["FOOTBALL_HOME"] + "//trading//trades//" + file, "r") as trade_file:
            trade = yaml.safe_load(trade_file)
        if "current bid" not in trade.keys():
            continue
        if (datetime.datetime.now() - trade["create_time"]).days > 2:
            team_win = trade["current bid"]["team"]
            current_team = trade["team_id"]
            with open(os.environ["FOOTBALL_HOME"] + "//teams//teams//" + current_team + ".yaml", "r") as cur_team_file:
                cur_team = yaml.safe_load(cur_team_file)
            cur_team["draft picks"] += [11] * int(trade["current bid"]["bid"])
            os.remove(os.environ["FOOTBALL_HOME"] + "//trading//trades//" + file)
            create_team.remove_player(file[:-5], current_team, minimum_team, True)
            create_team.add_player_old(team_win, file[:-5], maximum_team, salary_limit)
            with open(os.environ["FOOTBALL_HOME"] + "//teams//teams//" + current_team + ".yaml", "w") as cur_team_file:
                yaml.safe_dump(cur_team, cur_team_file)
            # TODO: Remove player from old team
            # TODO: Add player to new team


# trade_picks([1, 1], [6, 5], 11, 40)

# add_player_to_trade("Player_1076", 2)

# add_bid("1076", "40", 3)
# view_bid(1076)
sort_active_bids(18, 80, 130000000)
