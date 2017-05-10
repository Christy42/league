import csv
import yaml
import pandas
import os
from shutil import copyfile
from random import randint
import league_structure

from american_football import game


# reorder columns
def set_column_sequence(dataframe, seq, front=True):

    # Takes a dataframe and a subsequence of its columns,
    #  returns dataframe with seq as first columns if "front" is True,
    #  and seq as last columns if "front" is False.

    cols = seq[:] # copy so we don't mutate seq
    for x in dataframe.columns:
        if x not in cols:
            if front: # we want "seq" to be in the front
                # so append current column to the end of the list
                cols.append(x)
            else:
                # we want "seq" to be last, so insert this
                # column in the front of the new column list
                # "cols" we are building:
                cols.insert(0, x)
    return dataframe[cols]


class LeagueTable:
    def __init__(self, team_ids, yaml_file, csv_file, name):
        self._name = name
        self._yaml_file = yaml_file
        self._csv_file = csv_file
        self._team_ids = team_ids

    def create_schedule(self):
        """ Create a schedule for the teams in the list and return it"""
        s = []
        ids = list(self._team_ids.keys())
        if len(ids) % 2 == 1:
            ids = ids + ["BYE"]

        for i in range(len(ids)-1):
            mid = int(len(ids) / 2)
            l1 = ids[:mid]
            l2 = ids[mid:]
            l2.reverse()
            # Switch sides after each week
            if i % 2 == 1:
                s = s + [zip(l1, l2)]
            else:
                s = s + [zip(l2, l1)]
            ids.insert(1, ids.pop())

        week_count = 1
        fixtures = {}
        for week in s:
            match_count = 1
            fixtures[week_count] = {}
            for match in week:
                fixtures[week_count][match_count] = [match[0], match[1]]
                match_count += 1
            week_count += 1
        with open(self._yaml_file, "w") as file:
            yaml.safe_dump(fixtures, file)

    def play_week(self, week_number, team_folder, player_folder, season_no, league):
        with open(self._yaml_file, "r") as file:
            games = yaml.safe_load(file)[week_number]
        scores = []
        plays = {}
        for play_file in os.listdir(os.environ['FOOTBALL_HOME'] + "//plays_config//offense_plays"):
            with open(os.environ['FOOTBALL_HOME'] + "//plays_config//offense_plays//" + play_file, "r") as plays_file:
                plays.update(yaml.safe_load(plays_file))
        for play_file in os.listdir(os.environ['FOOTBALL_HOME'] + "//plays_config//defense_plays"):
            with open(os.environ['FOOTBALL_HOME'] + "//plays_config//defense_plays//" + play_file, "r") as plays_file:
                plays.update(yaml.safe_load(plays_file))
        for g in games:
            print(g)
            # Looking for player files, order files, formation files, team names
            name = [0, 0]
            formation = [0, 0]
            orders = ["", ""]
            for i in range(2):
                with open(team_folder + "//teams//" + games[g][i] + ".yaml") as team_file:
                    name[i] = yaml.safe_load(team_file)["team name"]
                if not os.path.isdir(os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_no)):
                    os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//formations//" + str(season_no))
                    os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_no))
                    os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//commentary//" + str(season_no))
                if not os.path.isdir(os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_no) +
                                     "//" + str(league)):
                    os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_no) + "//" + str(league))
                    os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//formations//" + str(season_no) + "//" +
                             str(league))
                    os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//commentary//" + str(season_no) + "//" +
                             str(league))
                if not os.path.isfile(os.environ['FOOTBALL_HOME'] + "//matches//orders//" +
                                      str(season_no) + "//" + str(league) + "//" + str(games[g][0]) +
                                      str(games[g][1]) + str(games[g][i]) + ".yaml"):
                    copyfile(team_folder + "//orders//" + str(games[g][i]) + "-formation.yaml",
                             os.environ['FOOTBALL_HOME'] + "//matches//formations//" + str(season_no) +
                             "//" + str(league) + "//" + str(games[g][0]) + str(games[g][1]) + str(games[g][i]) +
                             ".yaml")
                    copyfile(team_folder + "//orders//" + str(games[g][i]) + "-orders.yaml",
                             os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_no) +
                             "//" + str(league) + "//" + str(games[g][0]) + str(games[g][1]) + str(games[g][i]) +
                             ".yaml")

                formation[i] = os.environ['FOOTBALL_HOME'] + "//matches//formations//" + str(season_no) + \
                    "//" + str(league) + "//" + str(games[g][0]) + str(games[g][1]) + str(games[g][i]) + ".yaml"
                orders[i] = os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_no) + \
                    "//" + str(league) + "//" + str(games[g][0]) + str(games[g][1]) + str(games[g][i]) + ".yaml"
            comm_file = os.environ['FOOTBALL_HOME'] + "//matches//commentary//" + \
                str(season_no) + "//" + str(league) + "//" + str(games[g][0]) + str(games[g][1]) + ".yaml"
            stats_file = os.environ['FOOTBALL_HOME'] + "//matches//stats//" + \
                str(season_no) + str(league) + str(games[g][0]) + str(games[g][1]) + ".yaml"
            match = game.Game(player_folder + "//players", orders, formation, name, comm_file, stats_file)
            team_stats_folder = os.environ['FOOTBALL_HOME'] + "//teams//stats"
            player_stats_folder = os.environ['FOOTBALL_HOME'] + "//players//stats"
            match.play_game(season_no, team_stats_folder, player_stats_folder, [str(games[g][0]), str(games[g][1])])
            result = match.score
            # result = [randint(0, 30), randint(0, 30)]
            result_0 = [games[g][0], result[0]]
            result_1 = [games[g][1], result[1]]
            scores.append((result_0, result_1))

            league_structure.match_training_all(season_no, games[g], league, plays)
        # Amalgamate route data and formation data into per player, so create a dict with player_ids as keys,
        # accumulate the formations and routes run by going through the data and get it out for the match training
        # Need to actually play the above games
        self.update_scores(scores)

    @staticmethod
    def find_position(player_id, formation_amounts, formation_file):
        max_amount = 0
        position = "_exp"
        with open(os.environ['FOOTBALL_HOME'] + "//formations_config//test_yaml_defense_formation.yaml", "r") as form:
            formations = yaml.safe_load(form)
        with open(os.environ['FOOTBALL_HOME'] + "//formations_config//test_yaml_formation.yaml", "r") as form:
            formations.update(yaml.safe_load(form))
        for formation in formation_amounts:
            if formation_amounts[formation] > max_amount or \
                    (formation_amounts[formation] == max_amount and randint(0, 1) == 0):
                max_amount = formation_amounts[formation]
                with open(formation_file, "r") as form_file:
                    pos = yaml.safe_load(form_file)[formation].index(player_id)
                position = formations[formation]["positions"][pos]
        if position == "cb_sf_exp":
            if randint(0, 1) == 0:
                position = "cb_exp"
            else:
                position = "sf_exp"
        return position

    def change_name(self, team_id, new_name):
        with open(self._csv_file, "r") as file:
            data = yaml.safe_load(file)
        pass

    def update_scores(self, scores):
        # TODO: Read in the values as some sort of structure, ignore first line and column though
        with open(self._csv_file, "r") as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            stats = []
            for row in reader:
                stats.append(row)

        title_row = stats.pop(0)
        stats = pandas.DataFrame(stats, columns=title_row)
        # result_0 = [team id, score by team]
        for result_0, result_1 in scores:
            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "played"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "played"]) + 1
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "played"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "played"]) + 1

            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "for"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "for"]) + result_0[1]
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "for"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "for"]) + result_1[1]

            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "against"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "against"]) + result_1[1]
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "against"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "against"]) + result_0[1]

            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "wins"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "wins"]) + \
                (result_0[1] > result_1[1])
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "wins"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "wins"]) + \
                (result_1[1] > result_0[1])

            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "draws"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "draws"]) + \
                (result_0[1] == result_1[1])
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "draws"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "draws"]) + \
                (result_1[1] == result_0[1])

            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "losses"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "losses"]) + \
                (result_0[1] < result_1[1])
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "losses"] = \
                int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "losses"]) + \
                (result_1[1] < result_0[1])

            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "win%"] = \
                str(round(float(((int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1,
                                                "wins"]) +
                                  int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1,
                                                "draws"]) / 2) /
                                 int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1,
                                               "played"]))), 2) * 100) + "%"
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "win%"] = \
                str(round(float(((int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1,
                                                "wins"]) +
                                  int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1,
                                                "draws"]) / 2) /
                                 int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1,
                                               "played"]))), 2) * 100) + "%"

            stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "points difference"] = \
                (int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "for"]) -
                 int(stats.loc[int(stats.loc[stats["team id"] == result_0[0]]["position"]) - 1, "against"]))
            stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "points difference"] = \
                (int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "for"]) -
                 int(stats.loc[int(stats.loc[stats["team id"] == result_1[0]]["position"]) - 1, "against"]))
        # TODO: Sort the values
        cols = set_column_sequence(stats, ["position", "team name", "team id", "played", "wins", "draws", "losses",
                                           "win%", "for",
                                           "against", "points difference"])
        if '' in cols.columns:
            del cols['']
        with open(self._csv_file, "w") as file:
            file.write(cols.to_csv())

    def initialise_file(self):
        with open(self._csv_file, 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow(["position", "team id", "team name", "played", "wins", "draws", "losses",
                            "win%", "for", "against", "points difference"])
            position = 1
            for row in self._team_ids:
                writer.writerow([position, row, self._team_ids[row], '0', '0', '0', '0', '0', '0', '0', '0'])
                position += 1

    def display_file(self):
        # Will display the file in an easy to read format (maybe csv for the moment)
        pass

    def update_stats(self):
        pass


# TODO: Create set of leagues each with 12 teams.  Sets us a schedule and holds it ready to play

# TODO: Amend leagues files on the basis of the games

# TODO: Amend stat files on the basis of the games for both teams and players

# TODO: Figures out promotion and demotion
