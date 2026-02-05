# CSC 510 Portfolio Milestone
#### By Jonathan Sweeney

This project is designed to showcase skills learned in the course. The project allows users to use this tool to draft Fantasy Football players. The program leverages Random Forest Regression (supervised learning), First Order Logic (FOL), and the AI Recommendation feature combines the ML model, analytics, and FOL to adapt to the Draft changing state (other team's picks).

### Data Sources
1. Most of the raw data used in the project came from Kaggle, collected by Hyde in dataset [NFL Stats 2012-2024](https://www.kaggle.com/datasets/philiphyde1/nfl-stats-1999-2022) 
2. Team defense data was manually collected and entered from [NFLverse](https://www.footballdb.com/statistics/nfl/team-stats/defense-totals/2024/regular-season?sort=ydsgm)
3. Kicker data was collected from [The Football Database](https://www.footballdb.com/statistics/nfl/team-stats/defense-totals/2024/regular-season?sort=ydsgm)

### Environment Setup
1. Install Python
2. Navigate to project directory in a terminal window
3. Install necessary libraries `py -m pip install -r requirements.txt`

### Instructions to Train Model
* In the terminal, execute: `py Step4TrainModel.py`

Note: Training the model only uses the consolidate_player_data file to generate the player_rankings file used by the 
draft recommender. Other data not included due to size restraints.

### Instructions to Run
* In the terminal, execute:```py main.py```

### Directions to Use Program
* Select `1` to view detailed position analysis
* Select `2` to run draft (main part of the program)
* Select `3` to exit program or press `ctrl c`

##### Draft
1. Enter your draft position. The draft is a snake, so if you select 1, then you will draft first in odd rounds and second in even rounds
2. Select a recommended selection by position (e.g. QB, RB, WR) or press `ENTER` to select top recommendation
3. Draft all positions until roster is full

#### Known bugs
* Recommender - Does not limit options to necessary positons left or exclude backups when starting positions open

#### Future Improvements
* Add individual player data to track player's performance, age, and injuries
* Add a feature to display a positions health rating (e.g. 87% based on avg player's age and injury frequency)
* Add an ability to actually draft live where user enters the positions drafted by other players
* Add NFL APIs for player updates
* Build out tests