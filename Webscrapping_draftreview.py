from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import csv

# Creating count checker
players = []

# Creating empty list that will store the players' name
missing_college = []


# Opening the CSV file and appending the players to the list
with open("Webscrapping_Draft_NBA2.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        # Removing the column's name
        if line_count > 0:
            missing_college.append(row)
        line_count += 1

missing_college = missing_college[2100:2151]

driver = webdriver.Chrome()
driver.implicitly_wait(0.75)
driver.get("https://www.thedraftreview.com/index.php?option=com_search&view=search&Itemid=344")
for i in missing_college:
    # Locate the search box
    search_box = driver.find_element_by_xpath("//*[@id=\"search-searchword\"]")
    # Clearing the field then typing the name in the box and starting the search
    search_box.clear()
    search_box.send_keys(i[1])
    search_box.send_keys(Keys.ENTER)
    # Looping through the first 20 displayed results to check if there's a match
    for j in range(1, 21):
        try:
            # Retrieving text from each result
            name = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/dl/dt[{}]/a".format(j)).text
            # Formatting it to match the player's name
            name = name[:-4]
            # Convert to lower to avoid non matching issues
            name = name.lower()
            lower_name = i[1].lower()
            # Handling possibility for a player to be known by only one name or pseudonym
            if " " not in lower_name:
                split_name = []
                split_name.append(lower_name)
                split_name.append(lower_name)
            # Split name & surname to avoid non matching issues from potential pseudonyms
            else:
                split_name = lower_name.split()
            # Making sure the name is the same and the draft year as well
            if (split_name[0] in name and split_name[1] in name) and (i[5] in driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/dl/dd[{}]/span".format(j + (j - 1) * 2)).text):
                # Get the URL of the player's profile
                url = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/dl/dt[{}]/a".format(j)).get_attribute("href")
                # Access player's profile
                driver.get(url)
                # If no NBA profile, adding draft review profile
                if i[3] == "No NBA profile":
                    i[3] = url
                # Handling possibility of table formatting which changes the xpath
                column = 1
                try:
                    if driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[1]/table/tbody/tr").get_attribute("align") != "center" and driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[1]/table/tbody/tr").get_attribute("align") != "middle":
                        column += 1
                except NoSuchElementException:
                    column += 1
                # Looping through available info
                for k in range(1, 11):
                    try:
                        # Web element string
                        info = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[{}]/table/tbody/tr/td[2]/ul/li[{}]".format(column, k)).text
                        # Retrieving year before draft team info
                        if "HS." in info:
                            i.append("High School")
                        elif "College" in info:
                            i.append("College")
                        elif "Team:" in info:
                            i.append("International League")
                        # Checking for missing data
                        # String formatting
                        physicals = info[:6]
                        # Looking for height intel
                        if physicals == "Height":
                            # If height is missing or null, adding it
                            height = info[-7:]
                            i.append(height)
                        elif physicals == "Weight":
                            # If weight is missing or null, adding it
                            weight = info[12:]
                            i.append(weight)
                        if i[7] == "Pos Missing" or i[8] == "Nationality unknown" or i[8] == "" or i[9] == "Birthdate unknown":
                            # Looking for position intel
                            # String formatting
                            pos = info[:8]
                            physicals = info[:6]
                            nationality = info[:11]
                            birthdate = info[:9]
                            if pos == "Position":
                                # If position is missing, adding it
                                if i[7] == "Pos Missing":
                                    position = info[10:]
                                    i[7] = position
                            # Looking for nationality intel
                            if nationality == "Nationality":
                                # If nationality missing, adding it
                                if i[8] == "Nationality unknown" or i[8] == "":
                                    national = info[13:]
                                    i[8] = national
                            # Looking for birthdate intel
                            if birthdate == "Birthdate":
                                # If birthdate missing, adding it
                                if i[9] == "Birthdate unknown":
                                    birth = info[11:]
                                    i[9] = birth
                        else:
                            continue
                    except NoSuchElementException:
                        break
                # Retrieving year before draft stats
                # As for data above, possibility of a change in xpath must be taken into account
                line = 0
                table = 0
                if column == 2:
                    column += 2
                    line += 1
                elif column == 1:
                    column += 1
                try:
                    driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[4]/table/tbody[1]/tr").get_attribute("align")
                    table = 2
                    line = 0
                    try:
                        driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[4]/table/tbody[2]/tr").get_attribute("align")
                        pass
                    except NoSuchElementException:
                        column += 1
                        table = 1
                        try:
                            driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[5]")
                            pass
                        except NoSuchElementException:
                            column -= 1
                            line += 1
                except NoSuchElementException:
                    table = 1

                # Looping through all years to find the correct one
                for m in range(3, 9):
                    # Web element string
                    string = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[{}]/table/tbody[{}]/tr[{}]/td[1]/p".format(column, table, m + line)).text
                    # String formatting to keep only the last year
                    string = string[:7]
                    string = string[-2:]
                    # Check if the two digits are in the draft year
                    if string == i[5][-2:]:
                        # Adding all the stats
                        # Looping through all stats columns
                        for n in range(2, 11):
                            try:
                                # Web element string
                                data = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[{}]/table/tbody[{}]/tr[{}]/td[{}]".format(column, table, 2 + line, n)).text
                                result = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[{}]/table/tbody[{}]/tr[{}]/td[{}]".format(column, table, m + line, n)).text
                                # Checking for DNP
                                if "Did Not Play" in result:
                                    m -= 1
                                    # Updating the strings
                                    data = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[{}]/table/tbody[{}]/tr[{}]/td[{}]".format(column, table, 2 + line, n)).text
                                    result = driver.find_element_by_xpath("//*[@id=\"content\"]/div[2]/div[2]/article/div[{}]/table/tbody[{}]/tr[{}]/td[{}]".format(column, table, m + line, n)).text
                                    # Appending info to the player
                                    i.append("Did Not Play / Stats Y-1")
                                # Games played
                                if data == "GP":
                                    i[46] = result
                                # FG%
                                elif data == "FG%":
                                    i[49] = result
                                # 3P%
                                elif data == "3PT%":
                                    i[50] = result
                                # FT%
                                elif data == "FT%":
                                    i[51] = result
                                # SPG
                                elif data == "SPG":
                                    i[54] = result
                                # BPG
                                elif data == "BPG":
                                    i[55] = result
                                # RPG
                                elif data == "RPG":
                                    i[52] = result
                                # APG
                                elif data == "APG":
                                    i[53] = result
                                # PPG
                                elif data == "PPG":
                                    i[48] = result
                            except NoSuchElementException:
                                break
                        break
                    else:
                        continue
            else:
                continue
        except NoSuchElementException:
            break
    players.append(i)
    # Saving to csv file every 5 players checked
    if len(players) % 5 == 0:
        with open("Webscrapping_college.csv", mode='a', newline='') as file:
            draft_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for j in players:
                draft_writer.writerow(j)
        players.clear()
    driver.back()

driver.close()
