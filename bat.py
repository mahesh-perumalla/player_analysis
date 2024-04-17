import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup


def web_scrape_batting(urls: list) -> list:
    batting_data = pd.DataFrame()

    for url in urls:
        response = requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the data
        table = soup.find('table')

        # Extract data from the table
        data = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all('td'):
                row_data.append(cell.text.strip())
            if row_data:
                data.append(row_data)

        # Convert data to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])

        df = df.drop(columns=["Mat", "Inns", "NO", "HS",
                              "BF", "100", "50", "0", "4s", "6s"])

        # filtering player name and creating a new column for teams
        df["Team"] = df["Player"].str.extract(r'\((.*?)\)')
        df.insert(1, "Team", df.pop("Team"))
        df["Player"] = df["Player"].str.replace(r'\s*\(.*\)', '', regex=True)

        # dropping unnecessary data
        df["Year"] = df["Span"].str[:4]
        df.insert(2, "Year", df.pop("Year"))
        df = df.drop(columns=["Span"])

        if batting_data.empty:
            batting_data = df
        else:
            batting_data = pd.concat([batting_data, df])

    # replacing missing values with 0
    batting_data.loc[:, "Runs"] = batting_data["Runs"].replace("-", 0)

    # reassigning value to correct datatype
    batting_data["Year"] = batting_data["Year"].astype(int)
    batting_data["Runs"] = batting_data["Runs"].astype(int)
    batting_data["Ave"] = batting_data["Ave"].astype(float)
    batting_data["SR"] = batting_data["SR"].astype(float)

    # reordering data and resetting index
    batting_data = batting_data.sort_values(
        by=["Player", "Year"]).reset_index(drop=True)

    # renaming columns for readability
    batting_data.rename(columns={'Player': 'Player Name',
                                 "Ave": "Batting Average",
                                 "SR": "Strike Rate"}, inplace=True)

    return batting_data


# URLs for webs craping
batting_urls = ["https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2013-7720", "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/pepsi-indian-premier-league-2014-8827", "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/pepsi-indian-premier-league-2015-9657", "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2016-11001",
                "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2017-11701", "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2018-12210", "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2019-12741", "https://www.espncricinfo.com/records/tournament/batting-most-runs-career/indian-premier-league-2020-21-13533"]

batting_data = web_scrape_batting(batting_urls)

# getting salary of players
temp_2013 = pd.read_csv(".\\stats\\2013.csv")
temp_2013["Year"] = 2013
temp_2014 = pd.read_csv(".\\stats\\2014.csv")
temp_2014["Year"] = 2014
temp_2015 = pd.read_csv(".\\stats\\2015.csv")
temp_2015["Year"] = 2015
temp_2016 = pd.read_csv(".\\stats\\2016.csv")
temp_2016["Year"] = 2016
temp_2017 = pd.read_csv(".\\stats\\2017.csv")
temp_2017["Year"] = 2017
temp_2018 = pd.read_csv(".\\stats\\2018.csv")
temp_2018["Year"] = 2018
temp_2019 = pd.read_csv(".\\stats\\2019.csv")
temp_2019["Year"] = 2019
temp_2020 = pd.read_csv(".\\stats\\2020.csv")
temp_2020["Year"] = 2020
salary = pd.concat([temp_2013, temp_2014, temp_2015, temp_2016,
                   temp_2017, temp_2018, temp_2019, temp_2020])

# dropping unnecessary data
salary = salary.drop(
    columns=['Rank', 'Team', 'RAA', 'Wins', 'EFscore', 'Value',])
salary["Salary"] = salary["Salary"].str[1:].str.replace(',', '')

# reordering data and resetting index
salary = salary.sort_values(by=["Player", "Year"])

# dropping empty data
salary = salary.dropna().reset_index(drop=True)

# reassigning value to correct datatype
salary["Salary"] = salary["Salary"].astype(int)

# renaming column for readability
salary = salary.rename(columns={"Player": "Player Name",
                                "Salary": "Salary ($)"})

# merging datasets to include salary
batting_df = pd.merge(batting_data, salary, on=['Player Name', 'Year'])

# VFM = (runs * bat_avg * sr)/(salary)
batting_df["Value for Money"] = (batting_df["Runs"] * batting_df["Batting Average"]
                                 * batting_df["Strike Rate"]) / (batting_df["Salary ($)"])

# exporting bowling data for team analysis
batting_df.to_csv("./output/batting_output.csv", index=False, header=True)

# grouping and averaging data for players who have played for multiple seasons
temp_df = batting_df[batting_df.duplicated(
    subset=["Player Name"], keep=False)]
grouped_df = temp_df.groupby(["Player Name"])[
    "Value for Money"].mean().reset_index()
new_batting_df = grouped_df[["Player Name", "Value for Money"]]

# renaming column for better readability
new_batting_df = new_batting_df.rename(
    columns={'Value for Money': 'Overall Value for Money'})

# sorting data in descending order
new_batting_df = new_batting_df.sort_values(
    by="Overall Value for Money", ascending=False)

# removing insignificant players (pure bowlers)
new_batting_df = new_batting_df[new_batting_df["Overall Value for Money"] > 0.1].reset_index(
    drop=True)

# rounding-off for conciseness
new_batting_df["Overall Value for Money"] = new_batting_df["Overall Value for Money"].round(
    3)

# calculating statistical values
batting_std = new_batting_df["Overall Value for Money"].std()
batting_mean = new_batting_df["Overall Value for Money"].mean()
batting_vfm_max = new_batting_df["Overall Value for Money"].max()

# analysis of batting data
conditions = [new_batting_df['Overall Value for Money'].between(0, batting_mean),
              new_batting_df['Overall Value for Money'].between(
                  batting_mean, batting_mean+batting_std),
              new_batting_df['Overall Value for Money'].between(
                  batting_mean+batting_std, batting_mean+batting_std*2),
              new_batting_df['Overall Value for Money'].between(
                  batting_mean+batting_std*2, batting_mean+batting_std*3),
              new_batting_df['Overall Value for Money'].between(batting_mean+batting_std*3, batting_vfm_max)]
labels = ['Poor', 'Satisfactory', 'Good', 'Very Good', 'Outstanding']

# Create the 'class' column based on the conditions and labels
new_batting_df['Class'] = pd.cut(
    new_batting_df['Overall Value for Money'], bins=[0, batting_mean, batting_mean+batting_std, batting_mean +
                                                     batting_std*2, batting_mean+batting_std*3, batting_vfm_max], labels=labels)

# adding Team column
temp_data_frame = batting_df.sort_values(by="Year", ascending=False)
last_team_each_player = temp_data_frame.groupby(
    "Player Name").first().reset_index()
new_batting_df = pd.merge(new_batting_df, last_team_each_player[[
                          "Player Name", "Team"]], on="Player Name")
team_column = new_batting_df.pop("Team")
new_batting_df.insert(1, "Team", team_column)

# showing the player class in output
class_legend = {
    'Poor': "0 - " + str(batting_mean),
    'Satisfactory': str(batting_mean)+" - "+str(batting_mean+batting_std),
    'Good': str(batting_mean+batting_std)+" - "+str(batting_mean+batting_std*2),
    'Very Good': str(batting_mean+batting_std*2)+" - "+str(batting_mean+batting_std*3),
    'Outstanding': str(batting_mean+batting_std*3)+" - "+str(batting_vfm_max)
}
# Print the legend
print("Batsman-Class Legend:")
for label, description in class_legend.items():

    print(f"- {label}: {description}")
print("\t\t↓ Player-Class Table ↓")
print(new_batting_df)

top_batters_list = new_batting_df.loc[(new_batting_df['Class'] == 'Very Good') | (
    new_batting_df['Class'] == 'Outstanding'), 'Player Name'].tolist()

top_batters_df = batting_df.loc[(
    batting_df["Player Name"].isin(top_batters_list)), ["Player Name", "Year", "Value for Money"]].reset_index(drop=True)

# Plot line graphs for each player
for batter in top_batters_list:
    player_data = batting_df[batting_df["Player Name"] == batter]
    plt.plot(player_data["Year"], player_data["Value for Money"], label=batter)

# Add labels and legend
plt.xlabel("Year")
plt.ylabel("Value for Money")
plt.title("Realisation of Player Potential")
plt.legend()

# Show the plot
plt.show()
