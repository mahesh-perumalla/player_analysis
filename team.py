import pandas as pd
from enum import Enum
import matplotlib.pyplot as plt


# Read CSV files
batting_df = pd.read_csv("./output/bat output/batting_output.csv")
bowling_df = pd.read_csv("./output/bowl output/bowling_output.csv")

batting_df = batting_df.groupby(["Team", "Year"])[
    "Value for Money"].mean().reset_index()
bowling_df = bowling_df.groupby(["Team", "Year"])[
    "Value for Money"].mean().reset_index()


team_vfm = pd.DataFrame()
team_vfm["Team"] = batting_df["Team"]
team_vfm["Year"] = bowling_df["Year"]
team_vfm["Aggregate Value for Money"] = (batting_df["Value for Money"] +
                                         bowling_df["Value for Money"]).round(3)

team_vfm = team_vfm.sort_values(
    by="Year", ascending=False)


class TeamColor(Enum):
    MI = "blue"
    SRH = "orange"
    CSK = "gold"
    RR = "deeppink"
    KKR = "indigo"
    PWI = "dimgray"
    KXIP = "crimson"
    RCB = "firebrick"
    DC = "skyblue"
    GL = "darkgoldenrod"
    RPS = "mediumvioletred"


class TeamName(Enum):
    MI = "Mumbai Indians"
    SRH = "Sunrisers Hyderabad"
    CSK = "Chennai Super Kings"
    RR = "Rajasthan Royals"
    KKR = "Kolkata Knight Riders"
    PWI = "Pune Warriors India"
    KXIP = "Kings XI Punjab"
    RCB = "Royal Challengers Bangalore"
    DC = "Delhi Capitals"
    GL = "Gujarat Lions"
    RPS = "Rising Pune Supergiant"


def fixing(no_of_teams, teams_input):
    if no_of_teams > 1:
        teams = teams_input.split(',')
    else:
        teams = teams_input
    for i in range(no_of_teams):
        team = teams[i].strip()
        if team == "PWI":
            team_data = team_vfm[team_vfm["Team"] == team]
            plt.scatter(team_data["Year"], team_data["Aggregate Value for Money"],
                        label=team, color=TeamColor[team].value)
        else:
            team_data = team_vfm[team_vfm["Team"] == team]
            plt.plot(
                team_data["Year"], team_data["Aggregate Value for Money"], label=team, color=TeamColor[team].value)
    plt.xlabel("Year")
    plt.ylabel("Aggregate Value for Money")
    plt.title("Aggregate Value for Money Overtime")
    plt.legend(loc="upper right")
    plt.show()


print("MI = Mumbai Indians")
print("SRH = Sunrisers Hyderabad")
print("CSK = Chennai Super Kings")
print("RR = Rajasthan Royals")
print("KKR = Kolkata Knight Riders")
print("PWI = Pune Warriors India")
print("KXIP = Kings XI Punjab")
print("RCB = Royal Challengers Bangalore")
print("DC = Delhi Capitals")
print("GL = Gujarat Lions")
print("RPS = Rising Pune Supergiant")

no_of_teams = int(input("Enter the number of teams you want a graph for: "))
teams_input = input(
    "Enter the acronym for the team (split the acronyms with ','): ")

fixing(no_of_teams, teams_input)
