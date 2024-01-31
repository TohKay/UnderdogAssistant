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

"""
def get_html_content(request):
    import requests
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    
    #city = city.replace(' ', '+')
    #html_content = session.get(f'https://www.google.com/search?q=weather+{player_name}').text
    return None
"""
def home(request):
    player_name = request.GET.get('player_name')
    print(player_name)
    df = pd.DataFrame({

    })
    df2 = pd.DataFrame({

    })
    opponent_full = ""
    # Clear CSV files
    df.to_csv(r"C:\Users\sapic\Desktop\underdog_assistant\underdog\df.csv", mode='w+')
    df2.to_csv(r"C:\Users\sapic\Desktop\underdog_assistant\underdog\df2.csv", mode='w+')
        
    if 'player_name' in request.GET:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--disable-dev-shm-usage')
        image_preferences = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", image_preferences)
        driver = webdriver.Chrome(options=options)
        # time.sleep(0.5)
        driver.get("https://www.pro-football-reference.com/")
        # time.sleep(0.5)

        # Search for player
        search = driver.find_element(By.NAME, "search")
        search.send_keys(player_name)
        #search.send_keys("josh allen")
        search.send_keys(Keys.TAB)
        current_page = driver.current_url
        time.sleep(4)

        # Setup for BeautifulSoup parsing
        page = requests.get(current_page)
        soup = BeautifulSoup(page.text, 'html.parser')

        # Scrapes team name
        team = soup.find(name='div', id="meta")
        team_name = team.find('a').get_text()
        #print(team_name)

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

        if position == 'K': # Create DataFrame for Kicker
            # Loop for Column Titles
            for title in column_titles[12:32]:
                info.append(title.text.strip())

            # Create pandas DataFrame
            df = pd.DataFrame(columns=info[:20])

            df.columns = ["Team", "", "Opp", "Result", "0-19 A", "0-19 M", "20-29 A", "20-29 M", "30-39 A", "30-39 M", "40-49 A", "40-49 M", "50+ A", "50+ M", "Total FGA", "Total FGM", "FG%", "XPA", "XPM", "XP%"]

            # Loop to fill Rows
            column_info = table.find_all('tr')
            for row in column_info[2:]:
                row_data = row.find_all('td')
                individual_row_data = [data.text.strip() for data in row_data[:20]]
                length = len(df)
                df.loc[length] = individual_row_data
        elif position == 'QB': # Create DataFrame for Quarterback
            # Loop for Column Titles
            for title in column_titles[5:33]:
                info.append(title.text.strip())

            # Create pandas DataFrame
            df = pd.DataFrame(columns=info[:28])
            # TODO: Add text into columns to clarify stats
            # Pass Yards vs Rush Yards
            #df.columns = [str(col) + '_x' for col in df.columns]
            #df.columns = 'Passing ' + df.columns[8:14]
            #df = df.add_prefix('Passing')
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
        else: # Create DataFrame for any other position
            # Loop for Column Titles
            for title in column_titles[8:30]:
                info.append(title.text.strip())

            # Create pandas DataFrame
            df = pd.DataFrame(columns=info[:22])

            # Rename columns
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

        # Find next_opponents injury report
        for i in team_data:
            # Following two lines use next_opponent
            if next_opponent == (i['abbr']):
                injury_report = i['reportUrl']
                # time.sleep(0.5)
                driver.get(injury_report)
                time.sleep(5)
                # resets page request for new page
                page = requests.get(injury_report)
                soup = BeautifulSoup(page.text, 'html.parser')

                # should scrape the injury reports to clean up
                # injury_scrape = soup.find_all("div", {"class": "d3-l-col__col-12 nfl-o-injury-report__container"})

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
                        # no data in row_data
                        individual_row_data2 = []
                        for data2 in row_data2[:7]:
                            individual_row_data2.append(data2.text.strip())
                        #print(real_data2)
                        #individual_row_data2 = [data2.text.strip() for data2 in row_data2[:7]]
                        length2 = len(df2)
                        df2.loc[length2] = individual_row_data2

                    # Adjusts index to start at 1 instead of 0
                    df2.index = np.arange(1, len(df2) + 1)
                    df2 = df2.style.set_table_attributes('class="table table-hover text-center w-50 h-25"')
                    print(opponent_full + " Injury Report")
                    print(df2)
                    driver.quit()
        
        print(player_name)
        print(df)
        # TODO: Clean up all the dead code lol
        #df.to_csv(r"C:\Users\sapic\Desktop\weather_project\weatherapp\core\df.csv", mode='w+')
        #df2.to_csv(r"C:\Users\sapic\Desktop\weather_project\weatherapp\core\df2.csv", mode='w+')
        #html_content = get_html_content(request)
        #from bs4 import BeautifulSoup
        #soup = BeautifulSoup(html_content, 'html.parser')
        #result = dict()
        #result['location'] = soup.find("span", attrs={"class": "BNeawe tAd8D AP7Wnd"}).text
        #result['temp_now'] = soup.find("div", attrs={"class": "BNeawe iBp4i AP7Wnd"}).text
        #result['localtime'], result['weather_condition'] = soup.find("div", attrs={"class": "BNeawe tAd8D AP7Wnd"}).text.split('\n')
        #result['forecast'] = soup.find("div", attrs={"class": "R3Y3ec rr3bxd"}).text
        # {'result': result}

    #df = pd.read_csv("C:/Users/sapic/Desktop/weather_project/weatherapp/core/df.csv")
    #df2 = pd.read_csv("C:/Users/sapic/Desktop/weather_project/weatherapp/core/df2.csv")

    #df.rename( columns={'Unnamed: 0':'', 'Unnamed: 1':'', 'Unnamed: 2':''}, inplace=True )
    #df2.rename( columns={'Unnamed: 0':'', 'Unnamed: 1':'', 'Unnamed: 2':''}, inplace=True )
    df = df.fillna('')
    df = df.style.set_table_attributes('class="table table-hover text-center w-75 h-25"')

    mydict = {
        "df": df.to_html(),
        "df2": df2.to_html(),
        #"df": df.to_html(index=False),
        #"df2": df2.to_html(index=False),
        "player": player_name,
        "opponent": opponent_full
    }

    return render(request, 'underdog/home.html', context=mydict)