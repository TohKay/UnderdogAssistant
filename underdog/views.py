from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import time
import json

# Create your views here.

def home(request):
    player = request.GET.get('player_name')
    df = pd.DataFrame({

    })
    df2 = pd.DataFrame({

    })
    df3 = pd.DataFrame({

    })
    df4 = pd.DataFrame({

    })
    df5 = pd.DataFrame({

    })
    df5 = pd.DataFrame({

    })
    df6 = pd.DataFrame({

    })
    opponent_full = ""
    next_opponent = ""
    team_abbr = ""
    injury = ""
    player_name = ""
    total_d = ""
    pass_d = ""
    rush_d = ""
    scoring_d = ""
    if 'player_name' in request.GET:
        player_name = player
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--no-sandbox")
        image_preferences = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", image_preferences)
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.pro-football-reference.com/")

        # Search for player
        search = driver.find_element(By.NAME, "search")
        search.send_keys(player_name)
        search.send_keys(Keys.TAB)
        current_page = driver.current_url
        time.sleep(5)
        # Setup for BeautifulSoup parsing
        page = requests.get(current_page)
        soup = BeautifulSoup(page.text, 'html.parser')

        # Scrapes team name
        team = soup.find(name='div', id="meta")
        team_name = team.find('a').get_text()

        # Scrape player position
        position = soup.find("td", {'data-stat': "pos"}).get_text()

        # Grab next opponent
        opponent = soup.find(name='div', id="tfooter_last5")
        next_opponent = opponent.find('a').get_text()
        
        # Beginning setup for pandas dataframe
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2000)
        table = soup.find('table', id="last5")
        column_titles = table.find_all('th')
        info = []

        # Create DataFrame for Kicker
        if position == 'K': 
            # Loop for Column Titles
            for title in column_titles[12:32]:
                info.append(title.text.strip())
            # Create pandas DataFrame
            df = pd.DataFrame(columns=info[:20])
            # Rename Columns
            df.columns = ["Team", "", "Opp", "Result", "0-19 A", "0-19 M", "20-29 A", "20-29 M", "30-39 A", "30-39 M", "40-49 A", "40-49 M", "50+ A", "50+ M", "Total FGA", "Total FGM", "FG%", "XPA", "XPM", "XP%"]
            # Loop to fill Rows
            column_info = table.find_all('tr')
            for row in column_info[2:]:
                row_data = row.find_all('td')
                individual_row_data = [data.text.strip() for data in row_data[:20]]
                length = len(df)
                df.loc[length] = individual_row_data
        
        # Create DataFrame for Quarterback
        elif position == 'QB': 
            # Loop for Column Titles
            for title in column_titles[5:33]:
                info.append(title.text.strip())
            # Create pandas DataFrame
            df = pd.DataFrame(columns=info[:28])
            # Rename Columns
            df.columns = ["Team", "", "Opp", "Result", "Cmp", "Pass Att", "Cmp %", "Pass Yds", "Pass TD", "TD %", "Int", "Int %", "Lng", "Y/A", "AY/A", "Y/C", "Rate", "Sacks", "Sack Yds", "Sk %", "NY/A", "ANY/A", "Rush Att", "Rush Yds", "Rush TD", "Lng", "Y/A", "Fmb"]
            # Loop to fill Rows
            column_info = table.find_all('tr')
            for row in column_info[2:]:
                row_data = row.find_all('td')
                individual_row_data = [data.text.strip() for data in row_data]
                length = len(df)
                df.loc[length] = individual_row_data
            # Drop unwanted columns / Clean up Data
            df = df.drop(columns=['TD %', 'Int %', 'Y/A', 'AY/A', 'Y/C', 'Rate', 'Sk %', 'NY/A', 'ANY/A', 'Lng', 'Cmp %'], axis=1)
        
        # Create DataFrame for any other position
        else: 
            # Loop for Column Titles
            for title in column_titles[8:30]:
                info.append(title.text.strip())
            # Create pandas DataFrame
            df = pd.DataFrame(columns=info[:22])
            # Rename Columns
            df.columns = ["Team", "", "Opp", "Result", "Tgt", "Rec", "Rec Yds", "Y/R", "Rec TD", "Lng", "Catch%", "Y/Tgt", "Rush Att", "Rush Yds", "Rush TD", "Lng", "Y/A", "Touches", "Y/Tch", "YScm", "RRTD", "Fmb"]
            # Loop to fill Rows
            column_info = table.find_all('tr')
            for row in column_info[2:]:
                row_data = row.find_all('td')
                individual_row_data = [data.text.strip() for data in row_data]
                length = len(df)
                df.loc[length] = individual_row_data
            # Drop unwanted columns
            df = df.drop(columns=['Y/R', 'Y/Tgt', 'Y/A', 'Y/Tch', 'YScm', 'RRTD', 'Lng', 'Catch%'], axis=1)
            
        # Adjusts index to start at 1 instead of 0
        df.index = np.arange(1, len(df) + 1)

        # test json data
        f = open('./underdog/team_names.json')
        data = json.load(f)
        team_data = data['team_names']
        for i in team_data:
            if next_opponent == (i['abbr']):
                opponent_full = i['name']

        for i in team_data:
            if team_name == i['name']:
                team_abbr = i['abbr']
        # Find next_opponents injury report
        for i in team_data:

            # Following two lines use next_opponent
            if next_opponent == (i['abbr']):
                injury_report = i['reportUrl']
                driver.get(injury_report)
                time.sleep(5)

                # resets page request for new page
                page = requests.get(injury_report)
                soup = BeautifulSoup(page.text, 'html.parser')

                # Maybe use findAll to grab both tables before iterating through them
                injury_table = soup.find('table', {"class": "d3-o-table d3-o-table--row-striping"})
                if injury_table == None:
                    print("No injury report available. Please check back later in the week")
                else:

                    column_titles2 = injury_table.find_all('th')
                    info2 = []
                    for title in column_titles2:
                        info2.append(title.text.strip())

                    # Create pandas DataFrame
                    df2 = pd.DataFrame(columns=info2)

                    column_info2 = injury_table.find_all('tr')
                    for row2 in column_info2[1:]:
                        row_data2 = row2.find_all('td')
                        individual_row_data2 = []
                        for data2 in row_data2[:7]:
                            individual_row_data2.append(data2.text.strip())
                        length2 = len(df2)
                        df2.loc[length2] = individual_row_data2
                    injury = " Injury Report"
                    # Adjusts index to start at 1 instead of 0
                    df2.index = np.arange(1, len(df2) + 1)

                    team_stats = "https://www.foxsports.com/articles/nfl/2023-nfl-defense-rankings-team-pass-and-rush-stats"
                    df3 = pd.read_html(team_stats)[0]
                    df4 = pd.read_html(team_stats)[1]
                    df5 = pd.read_html(team_stats)[2]
                    df6 = pd.read_html(team_stats)[3]
                    df3.columns = ["#", "Team", "Defense Yards Avg", "Playoff Avg", "TD Allowed", "Playoff TD"]
                    df4.columns = ["#", "Team", "Pass Yards Avg", "Playoff Avg", "Pass TD", "Playoff TD"]
                    df5.columns = ["#", "Team", "Rush Yards Avg", "Playoff Avg", "Rush TD", "Playoff TD"]
                    df6.columns = ["#", "Team", "Points Avg", "Playoff Avg", "Total TD", "Playoff TD"]
                    total_d = "Total Defense"
                    pass_d = "Pass Defense"
                    rush_d = "Rush Defense"
                    scoring_d = "Scoring D"

                    # Cleaning up Column data
                    df3['Defense Yards Avg'] = df3['Defense Yards Avg'].astype(int)
                    df3['Playoff Avg'] = df3['Playoff Avg'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    df3['Playoff TD'] = df3['Playoff TD'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    df4['Pass Yards Avg'] = df4['Pass Yards Avg'].astype(int)
                    df4['Playoff Avg'] = df4['Playoff Avg'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    df4['Playoff TD'] = df4['Playoff TD'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    df5['Rush Yards Avg'] = df5['Rush Yards Avg'].astype(int)
                    df5['Playoff Avg'] = df5['Playoff Avg'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    df5['Playoff TD'] = df5['Playoff TD'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    #df6['Points Avg'] = df6['Points Avg'].round(1)
                    # .apply(lambda x: round(x, 0))
                    #df6['Playoff Avg'] = df6['Playoff Avg'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    df6['Playoff TD'] = df6['Playoff TD'].str.extract('(\d+)', expand=False).fillna(0).astype(int)
                    # Dropping Unnecessary rows for now
                    df3.drop([0,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], inplace=True)
                    df4.drop([0,1,2,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], inplace=True)
                    df5.drop([0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], inplace=True)
                    df6.drop([0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], inplace=True)
                    driver.quit()
    
    df = df.fillna('')
    df.index = df.index.values[::-1]
    df.columns.name = "Week #"

    
    df = df.style.set_table_styles(
        [{"selector": "tr th", "props": "background-color: #3D3D3D; color: white;"}]
    ).set_table_attributes(
        'class="table table-bordered border-dark table-hover text-center w-100 h-25"'
    )
    df2 = df2.style.hide(
        axis="index"
    ).set_table_styles(
        [{"selector": "th", "props": "background-color: #3D3D3D; color: white;"}]
    ).set_table_attributes(
        'class="table table-sm table-bordered border-dark table-hover text-center w-50 h-25"'
    )
    df3 = df3.style.hide(
        axis="index"
    ).set_table_styles(
        [{"selector": "tr th", "props": "background-color: #3D3D3D; color: white;"}]
    ).set_table_attributes(
        'class="table table-sm table-bordered border-dark table-hover text-center w-25 h-25"'
    )
    df4 = df4.style.hide(
        axis="index"
    ).set_table_styles(
        [{"selector": "tr th", "props": "background-color: #3D3D3D; color: white;"}]
    ).set_table_attributes(
        'class="table table-sm table-bordered border-dark table-hover text-center w-25 h-25"'
    )
    df5 = df5.style.hide(
        axis="index"
    ).set_table_styles(
        [{"selector": "tr th", "props": "background-color: #3D3D3D; color: white;"}]
    ).set_table_attributes(
        'class="table table-sm table-bordered border-dark table-hover text-center w-25 h-25"'
    )
    df6 = df6.style.format({'Points Avg': '{:.1f}'}
    ).hide(
        axis="index"
    ).set_table_styles(
        [{"selector": "tr th", "props": "background-color: #3D3D3D; color: white;"}]
    ).set_table_attributes(
        'class="table table-sm table-bordered border-dark table-hover text-center w-25 h-25"'
    )
    

    mydict = {
        "df": df.to_html(),
        "df2": df2.to_html(),
        "df3": df3.to_html(),
        "df4": df4.to_html(),
        "df5": df5.to_html(),
        "df6": df6.to_html(),
        "player": player_name,
        "opponent": opponent_full,
        "injury_color": next_opponent,
        "team_abbr": team_abbr,
        "injury": injury,
        "total_d": total_d,
        "pass_d": pass_d,
        "rush_d": rush_d,
        "scoring_d": scoring_d
    }

    return render(request, 'underdog/home.html', context=mydict)