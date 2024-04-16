import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup


def web_scrape_bowling(urls: list) -> list:
    bowling_data = pd.DataFrame()

    for url in urls:
        response = requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the data
        table = soup.find('table')

        # Extract data from the table
        data2 = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all('td'):
                row_data.append(cell.text.strip())
            if row_data:
                data2.append(row_data)

        # Convert data to DataFrame
        df = pd.DataFrame(data2[1:], columns=data2[0])
        df = df.drop(columns=["Mat", "Inns", "Balls", "Overs",
                              "Mdns", "Runs", "BBI", "SR", "4", "5"])

        # filtering player name and creating a new column for teams
        df["Team"] = df["Player"].str.extract(r'\((.*?)\)')
        df.insert(1, "Team", df.pop("Team"))
        df["Player"] = df["Player"].str.replace(r'\s*\(.*\)', '', regex=True)

        # dropping unnecessary data
        df["Year"] = df["Span"].str[:4]
        df.insert(2, "Year", df.pop("Year"))
        df = df.drop(columns=["Span"])

        if bowling_data.empty:
            bowling_data = df
        else:
            bowling_data = pd.concat([bowling_data, df])

    # reassigning value to correct datatype
    bowling_data["Year"] = bowling_data["Year"].astype(int)
    bowling_data["Wkts"] = bowling_data["Wkts"].astype(int)
    bowling_data["Ave"] = bowling_data["Ave"].astype(float)
    bowling_data["Econ"] = bowling_data["Econ"].astype(float)

    # reordering data and resetting index
    bowling_data = bowling_data.sort_values(
        by=["Player", "Year"]).reset_index(drop=True)

    # renaming columns for readability
    bowling_data.rename(columns={'Player': 'Player Name',
                                 'Wkts': 'Wickets',
                                 "Ave": "Bowling Average",
                                 "Econ": "Economy"}, inplace=True)
    return bowling_data


bowling_urls = ["https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/indian-premier-league-2013-7720", "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/pepsi-indian-premier-league-2014-8827", "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/pepsi-indian-premier-league-2015-9657", "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/indian-premier-league-2016-11001",
                "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/indian-premier-league-2017-11701", "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/indian-premier-league-2018-12210", "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/indian-premier-league-2019-12741", "https://www.espncricinfo.com/records/tournament/bowling-most-wickets-career/indian-premier-league-2020-21-13533"]

bowling_data = web_scrape_bowling(bowling_urls)

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
bowling_df = pd.merge(bowling_data, salary, on=['Player Name', 'Year'])

# VFM =
weight = 100/3
bowling_df["Value for Money"] = ((bowling_df["Wickets"]*weight) * (weight/bowling_df["Bowling Average"])
                                 * (weight/bowling_df["Economy"])) / (bowling_df["Salary ($)"]/100)

# grouping and averaging data for players who have played for multiple seasons
temp_df = bowling_df[bowling_df.duplicated(
    subset=["Player Name"], keep=False)]
grouped_df = temp_df.groupby(["Player Name"])[
    "Value for Money"].mean().reset_index()
new_bowling_df = grouped_df[["Player Name", "Value for Money"]]

# renaming column for better readability
new_bowling_df = new_bowling_df.rename(
    columns={'Value for Money': 'Overall Value for Money'})

# sorting data in descending order
new_bowling_df = new_bowling_df.sort_values(
    by="Overall Value for Money", ascending=False)

# removing insignificant players (pure bowlers)
new_bowling_df = new_bowling_df[new_bowling_df["Overall Value for Money"] > 0.1].reset_index(
    drop=True)

# rounding-off for conciseness
new_bowling_df["Overall Value for Money"] = new_bowling_df["Overall Value for Money"].round(
    3)

# calculating statistical values
bowling_std = new_bowling_df["Overall Value for Money"].std()
bowling_mean = new_bowling_df["Overall Value for Money"].mean()
bowling_vfm_max = new_bowling_df["Overall Value for Money"].max()

# analysis of batting data
conditions = [new_bowling_df['Overall Value for Money'].between(0, bowling_mean),
              new_bowling_df['Overall Value for Money'].between(
                  bowling_mean, bowling_mean+bowling_std),
              new_bowling_df['Overall Value for Money'].between(
                  bowling_mean+bowling_std, bowling_mean+bowling_std*2),
              new_bowling_df['Overall Value for Money'].between(
                  bowling_mean+bowling_std*2, bowling_mean+bowling_std*3),
              new_bowling_df['Overall Value for Money'].between(bowling_mean+bowling_std*3, bowling_vfm_max)]
labels = ['Poor', 'Satisfactory', 'Good', 'Very Good', 'Outstanding']

# Create the 'class' column based on the conditions and labels
new_bowling_df['Class'] = pd.cut(
    new_bowling_df['Overall Value for Money'], bins=[0, bowling_mean, bowling_mean+bowling_std, bowling_mean +
                                                     bowling_std*2, bowling_mean+bowling_std*3, bowling_vfm_max], labels=labels)

# adding Team column
temp_data_frame = bowling_df.sort_values(by="Year", ascending=False)
last_team_each_player = temp_data_frame.groupby(
    "Player Name").first().reset_index()
new_bowling_df = pd.merge(new_bowling_df, last_team_each_player[[
                          "Player Name", "Team"]], on="Player Name")
team_column = new_bowling_df.pop("Team")
new_bowling_df.insert(1, "Team", team_column)

# showing the player class in output
class_legend = {
    'Poor': "0 - " + str(bowling_mean),
    'Satisfactory': str(bowling_mean)+" - "+str(bowling_mean+bowling_std),
    'Good': str(bowling_mean+bowling_std)+" - "+str(bowling_mean+bowling_std*2),
    'Very Good': str(bowling_mean+bowling_std*2)+" - "+str(bowling_mean+bowling_std*3),
    'Outstanding': str(bowling_mean+bowling_std*3)+" - "+str(bowling_vfm_max)
}
# Print the legend
print("Player-Class Legend:")
for label, description in class_legend.items():
    print(f"- {label}: {description}")

print("\t\t↓ Bowler-Class Table ↓")
print(new_bowling_df)

top_bowler_list = new_bowling_df.loc[(new_bowling_df['Class'] == 'Very Good') | (
    new_bowling_df['Class'] == 'Outstanding'), 'Player Name'].tolist()

top_bowler_df = bowling_df.loc[(
    bowling_df["Player Name"].isin(top_bowler_list)), ["Player Name", "Year", "Value for Money"]].reset_index(drop=True)

# Plot line graphs for each player
for bowler in top_bowler_list:
    player_data = bowling_df[bowling_df["Player Name"] == bowler]
    plt.plot(player_data["Year"], player_data["Value for Money"], label=bowler)

# Add labels and legend
plt.xlabel("Year")
plt.ylabel("Value for Money")
plt.title("Realisation of Player Potential")
plt.legend()

# Show the plot
plt.show()
