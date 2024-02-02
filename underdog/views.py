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
    player_name = request.GET.get('player_name')
    df = pd.DataFrame({

    })
    df2 = pd.DataFrame({

    })
    opponent_full = ""
    next_opponent = ""
    team_abbr = ""

    if 'player_name' in request.GET:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--disable-dev-shm-usage')
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
        f = open('C:/Users/sapic/Desktop/underdog_assistant/underdog/team_names.json')
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

                    # Adjusts index to start at 1 instead of 0
                    df2.index = np.arange(1, len(df2) + 1)
                    df2 = df2.style.set_table_attributes('class="table table-sm table-bordered border-dark table-hover text-center w-50 h-25"')
                    driver.quit()
        
    df = df.fillna('')
    df = df.reindex(index=df.index[::-1])
    df.columns.name = "Week #"
    df = df.style.set_table_attributes('class="table table-bordered border-dark table-hover text-center w-100 h-25"')

    mydict = {
        "df": df.to_html(),
        "df2": df2.to_html(),
        "player": player_name,
        "opponent": opponent_full,
        "injury_color": next_opponent,
        "team_abbr": team_abbr
    }

    return render(request, 'underdog/home.html', context=mydict)