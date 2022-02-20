from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv
import re

# Creating lists full of null if player never went to nba, playoffs or college
no_playoffs = ["NaN"] * 17
no_college = ["NaN"] * 11
no_nba = ["NaN"] * 18

# Draft counter
drafts = 0

driver = webdriver.Chrome()
driver.implicitly_wait(1.25)
driver.get("https://www.nba.com/history/draft")
assert "Draft" in driver.title
# Handling cookies pop-up while waiting for the accept button to be clickable
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
# Getting the desired draft class
draft_years = range(2019, 2020)
# Looping through all draft years
for y in draft_years:
    # driver.find_element_by_partial_link_text("{}".format(y)).click()
    driver.get("https://www.nba.com/stats/draft/history/?Season=2019")
    # Creating empty list to store the data of the draft class' first 50 players
    draft_class = []

    # Looping through the first 50 picks
    for x in range(1, 51):
        # Creating empty list to store the data for each player
        career_stats = []
        # Variables to check if playoffs/all-star/college missing stats already taken into account
        no_playoffs_dealt = True
        no_all_star_dealt = True
        no_college_dealt = True
        playoffs_table = False
        allstar_table = False
        college_table = False
        # Checking if player has a link to its profile page on nba.com
        try:
            # Adding player/drafting team/link to personal page/college/draft year/overall pick to previous list
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[1]/a'.format(x)).text)
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[2]/a'.format(x)).text)
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[1]/a'.format(x)).get_attribute("ng-href"))
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[3]'.format(x)).text)
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[4]'.format(x)).text)
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[7]'.format(x)).text)
            # Accessing player stats page
            driver.get("https://www.nba.com" + career_stats[2] + "career/")
            # Adding position
            # Handling possibility of a missing data
            try:
                # If team logo is present on the page, position data is displaced
                logo = 0
                # If shirt number is missing, position data is displaced
                shirt = 0
                try:
                    driver.find_element_by_class_name("stats-player-summary__bg")
                    logo += 1
                except NoSuchElementException:
                    logo = 0
                if "#" in driver.find_element_by_xpath('/html/body/main/div/div/div/div[2]/div[1]/div[1]/div[{}]/div/div[{}]/div[1]/div[1]/span/span[2]'.format(1 + logo, 2 + logo)).text:
                    shirt += 1
                data = driver.find_element_by_xpath('/html/body/main/div/div/div/div[2]/div[1]/div[1]/div[{}]/div/div[{}]/div[1]/div[1]/span/span[{}]'.format(1 + logo, 2 + logo, 2 + shirt))
                career_stats.append(data.text)
            except NoSuchElementException:
                career_stats.append("Pos Missing")
            # Adding nationality
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[5]/div[2]').text)
            # Adding birthdate
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div[3]/div[3]/div[2]').text)
            # Handling possibility of a player having his profile but no recorded stats
            try:
                # Adding games played
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[4]').text)
                # Adding games started
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[5]').text)
                # Adding minutes per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[6]').text)
                # Adding points per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[7]').text)
                # Adding field goal made per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[8]').text)
                # Adding field goal attempted per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[9]').text)
                # Adding field goal %
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[10]').text)
                # Adding 3-pointer made per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[11]').text)
                # Adding 3-pointer attempted per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[12]').text)
                # Adding 3-pointer %
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[13]').text)
                # Adding free-throw made per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[14]').text)
                # Adding free-throw attempted per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[15]').text)
                # Adding free-throw %
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[16]').text)
                # Adding rebounds per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[19]').text)
                # Adding assists per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[20]').text)
                # Adding steals per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[21]').text)
                # Adding blocks per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[22]').text)
                # Adding TO per game
                career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[7]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[23]').text)
            except NoSuchElementException:
                # Adding nba stats
                career_stats = career_stats + no_nba
                # Adding playoffs stats
                career_stats = career_stats + no_playoffs
                # Adding All-Star appearances
                career_stats.append(0)
                # Adding college stats
                career_stats = career_stats + no_college
                # Adding NBA awards
                career_stats.append(0)
                career_stats.append(0)
                career_stats.append(0)
                career_stats.append(0)
                career_stats.append(0)
                # Adding player to draft class
                draft_class.append(career_stats)
                # Going back to draft page
                driver.back()
                # Skipping to next iteration
                continue

            try:
                header = driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[2]/span')
                # Checking if there are playoffs stats for this player
                if header.text == "Career Playoffs Stats":
                    # Games played
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[4]').text)
                    # Minutes per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[6]').text)
                    # Points per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[7]').text)
                    # Adding field goal made per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[8]').text)
                    # Adding field goal attempted per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[9]').text)
                    # Field goal %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[10]').text)
                    # Adding 3-pointer made per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[11]').text)
                    # Adding 3-pointer attempted per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[12]').text)
                    # 3-pointer %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[13]').text)
                    # Adding free-throw made per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[14]').text)
                    # Adding free-throw attempted per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[15]').text)
                    # Free-throw %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[16]').text)
                    # Rebounds per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[19]').text)
                    # Assists per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[20]').text)
                    # Steals per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[21]').text)
                    # Blocks per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[22]').text)
                    # TO per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[23]').text)
                    no_playoffs_dealt = False
                    playoffs_table = True
                # Checking for All-Star appearances
                elif header.text == "Career All Star Stats":
                    # If All Star Stats are found here, it means the player never played in any playoffs games
                    career_stats = career_stats + no_playoffs
                    no_playoffs_dealt = False
                    # Adding number of All-Star games
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[4]').text)
                    no_all_star_dealt = False
                    allstar_table = True
                # Checking for college stats
                elif header.text == "Career College Stats":
                    # If College Stats are found here, it means the player never played in any playoffs or All Star games
                    career_stats = career_stats + no_playoffs
                    career_stats.append(0)
                    no_playoffs_dealt = False
                    no_all_star_dealt = False
                    # Retrieving data for last college season
                    # Games played
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[4]').text)
                    # Minutes per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[6]').text)
                    # Points per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[7]').text)
                    # Field Goal %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[10]').text)
                    # 3-pointer %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[13]').text)
                    # Free-throw %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[16]').text)
                    # Rebounds per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[19]').text)
                    # Assists per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[20]').text)
                    # Steals per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[21]').text)
                    # Blocks per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[22]').text)
                    # TO per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[8]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[23]').text)
                    no_college_dealt = False
                    college_table = True
                # If none of the above is true but another table is present on the page
                else:
                    # No Playoffs
                    career_stats = career_stats + no_playoffs
                    no_playoffs_dealt = False
                    # No All-Star
                    career_stats.append(0)
                    no_all_star_dealt = False
                    # No college
                    career_stats = career_stats + no_college
                    no_college_dealt = False
            # If no table found
            except NoSuchElementException:
                career_stats = career_stats + no_playoffs
                career_stats.append(0)
                career_stats = career_stats + no_college
                no_playoffs_dealt = False
                no_all_star_dealt = False
                no_college_dealt = False

            # If player has playoffs stats : checking next stats
            try:
                header = driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[2]/span')
                # Checking for All Star games
                if header.text == "Career All Star Stats":
                    # Adding number of All-Star games
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tfoot/tr/td[4]').text)
                    no_all_star_dealt = False
                    allstar_table = True
                elif header.text == "Career College Stats":
                    # If College Stats are found here, it means the player never played any All Star game
                    if no_all_star_dealt == True:
                        career_stats.append(0)
                        no_all_star_dealt += False
                    # Retrieving data for last college season
                    # Games played
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[4]').text)
                    # Minutes per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[6]').text)
                    # Points per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[7]').text)
                    # Field Goal %
                    career_stats.append(driver.find_element_by_xpath( '/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[10]').text)
                    # 3-pointer %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[13]').text)
                    # Free-throw %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[16]').text)
                    # Rebounds per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[19]').text)
                    # Assists per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[20]').text)
                    # Steals per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[21]').text)
                    # Blocks per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[22]').text)
                    # TO per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[9]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[23]').text)
                    no_college_dealt = False
                    college_table = True
                # If none of the above is true but another table is present on the page
                else:
                    # No All-Star
                    if no_all_star_dealt == True:
                        career_stats.append(0)
                        no_all_star_dealt = False
                    # No college
                    if no_college_dealt == True:
                        career_stats = career_stats + no_college
                        no_college_dealt = False
            # If no table found
            except NoSuchElementException:
                if no_all_star_dealt == True:
                    career_stats.append(0)
                    no_all_star_dealt = False
                if no_college_dealt == True:
                    career_stats = career_stats + no_college
                    no_college_dealt = False

            # If player has playoffs & All Star stats : checking for college stats
            try:
                header = driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[2]/span')
                if header.text == "Career College Stats":
                    # Retrieving data for last college season
                    # Games played
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[4]').text)
                    # Minutes per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[6]').text)
                    # Points per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[7]').text)
                    # Field Goal %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[10]').text)
                    # 3-pointer %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[13]').text)
                    # Free-throw %
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[16]').text)
                    # Rebounds per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[19]').text)
                    # Assists per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[20]').text)
                    # Steals per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[21]').text)
                    # Blocks per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[22]').text)
                    # TO per game
                    career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div/div[4]/div/div/div/div/div[10]/nba-stat-table/div[3]/div[1]/table/tbody/tr/td[23]').text)
                    no_college_dealt = False
                    college_table = True
                # If another table is detected
                else:
                    if no_college_dealt == True:
                        career_stats = career_stats + no_college
                        no_college_dealt = False
            # If no table is found
            except NoSuchElementException:
                if no_college_dealt == True:
                    career_stats = career_stats + no_college
                    no_college_dealt = False

            # Checking for awards
            mvp = 0
            all_nba = 0
            defensive_team = 0
            finals_mvp = 0
            hof = 0
            # Getting the correct table position depends on the number of previous existing tables (playoffs, all-star, college), base position without any of them is 9
            pos = 9
            if playoffs_table == True:
                pos += 1
            if allstar_table == True:
                pos += 1
            if college_table == True:
                pos += 1
            for i in range(2, 23):
                try:
                    award = driver.find_element_by_xpath("/html/body/main/div/div/div/div[4]/div/div/div/div/div[{}]/div[2]/div/div[{}]/span[2]".format(pos, i))
                    # Checking for awards using RegEx
                    pattern_mvp = "[0-9]+ NBA Most Valuable Player"
                    pattern_all_nba = "[0-9]+ All-NBA"
                    pattern_defensive_team = "[0-9]+ All-Defensive Team"
                    pattern_finals_mvp = "[0-9]+ NBA Finals Most Valuable Player"
                    pattern_hof = "[0-9] Hall of Fame Inductee"
                    result_mvp = re.match(pattern_mvp, award.text)
                    result_all_nba = re.match(pattern_all_nba, award.text)
                    result_defensive_team = re.match(pattern_defensive_team, award.text)
                    result_finals_mvp = re.match(pattern_finals_mvp, award.text)
                    result_hof = re.match(pattern_hof, award.text)
                    if result_mvp:
                        career_stats.append(award.text)
                        mvp += 1
                    # Checking for All-NBA selections
                    elif result_all_nba:
                        career_stats.append(award.text)
                        all_nba += 1
                    # Checking for All-Defensive Team selections
                    elif result_defensive_team:
                        career_stats.append(award.text)
                        defensive_team += 1
                    # Checking for Finals MVP
                    elif result_finals_mvp:
                        career_stats.append(award.text)
                        finals_mvp += 1
                    # Checking for Hall of Fame induction
                    elif result_hof:
                        career_stats.append(award.text)
                        hof += 1
                except NoSuchElementException:
                    break

            # Checking if the player has won at least once each award, if not adding 0 to the list
            if mvp == 0:
                career_stats.append(0)
            if all_nba == 0:
                career_stats.append(0)
            if defensive_team == 0:
                career_stats.append(0)
            if finals_mvp == 0:
                career_stats.append(0)
            if hof == 0:
                career_stats.append(0)

            # Add player to draft class
            draft_class.append(career_stats)
            # Return to draft page
            driver.back()

        # Handling possibility that the player never played in the NBA and therefore has no profile on nba.com
        except NoSuchElementException:
            # Adding player/drafting team/link to personal page/college/draft year/overall pick to previous list
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[1]/span'.format(x)).text)
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[2]/a'.format(x)).text)
            career_stats.append("No NBA profile")
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[3]'.format(x)).text)
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[4]'.format(x)).text)
            career_stats.append(driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]/td[7]'.format(x)).text)
            # Adding missing pos
            career_stats.append("Pos Missing")
            # Adding nationality
            career_stats.append("Nationality unknown")
            # Adding birthdate
            career_stats.append("Birthdate unknown")
            # Adding nba stats
            career_stats = career_stats + no_nba
            # Adding playoffs stats
            career_stats = career_stats + no_playoffs
            # Adding All-Star appearances
            career_stats.append(0)
            # Adding college stats
            career_stats = career_stats + no_college
            # Adding NBA awards
            career_stats.append(0)
            career_stats.append(0)
            career_stats.append(0)
            career_stats.append(0)
            career_stats.append(0)

            # Add player to draft class
            draft_class.append(career_stats)

    # Going back to draft's history
    driver.get("https://www.nba.com/history/draft")

    # For each player, append his characteristics and stats to a csv file
    with open("Webscrapping_Draft_NBA.csv", mode = 'a', newline='') as draft_file:
        draft_writer = csv.writer(draft_file, delimiter= ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for j in draft_class:
            draft_writer.writerow(j)
        drafts += 1

    # Closing driver and reopening it after two draft classes to prevent loading issues later
    if drafts % 2 == 0:
        driver.close()
        driver = webdriver.Chrome()
        driver.implicitly_wait(1.25)
        driver.get("https://www.nba.com/history/draft")
        assert "Draft" in driver.title
        # Handling cookies pop-up while waiting for the accept button to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
        drafts = 0


driver.close()


