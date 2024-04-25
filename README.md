### Prerequisites:
1. Make sure you have Python installed on your system. You can download and install Python from the official website: [Python Downloads](https://www.python.org/downloads/).

2. Install the required Python packages using pip. Open a terminal or command prompt and run the following commands:
   ```
   pip install pandas numpy matplotlib requests beautifulsoup4
   ```

### Instructions:
1. Download the provided Python scripts (`bat.py`, `bowl.py`, `team.py`) and the sample CSV files (`2013.csv`, `2014.csv`, `2015.csv`, `2016.csv`, `2017.csv`, `2018.csv`, `2019.csv`, `2020.csv`) to your local machine to a folder named `stats`.

2. Open a terminal or command prompt and navigate to the directory containing the scripts and CSV files.

3. Run the following command to execute the `bat.py` script:
   ```
   python bat.py
   ```
4. It displays the Batsmen Class Table (ranking) and a line graph showing realization of a batsman's potential.
   
5. After the execution of `bat.py`, run the following command to execute the `bowl.py` script:
   ```
   python bowl.py
   ```
6. It displays the Bowler Class Table (ranking) and a line graph showing realization of a bowler's potential.

7. Finally, execute the `team.py` script by running the following command:
   ```
   python team.py
   ```

8. Follow the on-screen prompts to input the number of teams and their acronyms for which you want to generate a multi-line graph.

9. After providing the inputs, the script will display the graph showing the aggregate value for money over time for the selected teams.

### Note:
- Make sure you have an active internet connection while running the scripts as they scrape data from the web using URLs.
- Ensure that you have the necessary permissions to read and write files in the directory where the scripts are located, as the scripts generate CSV files as output.
