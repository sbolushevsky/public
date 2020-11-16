from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import pygsheets
import pandas as pd
from datetime import datetime

import subprocess
import email_send


def upload():
    global driver

    class element_has_css_class(object):
        """An expectation for checking that an element has a particular css class.

        locator - used to find the element
        returns the WebElement once it has the particular css class
        """

        def __init__(self, locator, css_class):
            self.locator = locator
            self.css_class = css_class

        def __call__(self, driver):
            element = driver.find_element(*self.locator)  # Finding the referenced element
            if self.css_class in element.get_attribute("class"):
                return element
            else:
                return False

    username = "NONE"
    # password=getpass("Enter your password: ")
    password = "NONE"

    chrome_options = Options()
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome("C:\\Users\\sbolushevsky\\Documents\\chemicals\\WebDriver\\chromedriver.exe",
                              options=chrome_options)
    driver.get("https://access.cheminventory.net/")

    # username_textbox = driver.find_element_by_name("username")
    # username_textbox.send_keys(username)

    # password_textbox = driver.find_element_by_name("password")
    # password_textbox.send_keys(password)

    driver.maximize_window()
    username_textbox = driver.find_element_by_name("username")
    username_textbox.send_keys(username, Keys.ARROW_DOWN)

    password_textbox = driver.find_element_by_name("password")
    password_textbox.send_keys(password, Keys.ARROW_DOWN)

    js = "document.getElementById('signinbutton').click()"
    driver.execute_script(js)

    select = ""
    while not select:
        try:
            select = driver.find_element_by_xpath("//li[6]/a[@class='expand level-closed']")
            driver.execute_script("arguments[0].setAttribute('class', 'expand level-opened')", select)
            driver.get("https://access.cheminventory.net/groupmanagement.php")
        except:
            continue

    select = ""
    while not select:
        try:
            select = driver.find_element_by_xpath(
                "//html/body/div[2]/div[5]/div[1]/div/div/div[2]/div/div[1]/div[@class='btn-group']")
            driver.execute_script("arguments[0].setAttribute('class', 'btn-group open')", select)
            driver.get("https://access.cheminventory.net/groupmanagement.php")
        except:
            continue

    js = "document.querySelector('a[onclick*=importmodal2]').click()"
    driver.execute_script(js)

    js = "document.querySelector('button[onclick*=importstep1]').click()"
    driver.execute_script(js)

    file_input = driver.find_element_by_xpath("//div[1]/div/div[1]/input[@type='file']")
    file_input.send_keys(r"C:\Users\sbolushevsky\Documents\chemicals\Chemical_Inventory_Import.xlsx")

    js = "document.querySelector('button[onclick*=beginfileupload]').click()"
    driver.execute_script(js)

    # Wait until an element with id='myNewInput' has class 'myCSSClass'
    wait = WebDriverWait(driver, 10)
    wait.until(element_has_css_class((By.ID, 'importheaderitems'), "ui-sortable"))

    js = "document.querySelector('button[onclick*=importstartimport]').click()"
    driver.execute_script(js)

    return print("\nChemInventory is being updated...")


def generate_files(sheet1, sheet2, list):
    """Generates Exel files for printer and ChemInventory
    """

    cas_list = list

    df = pd.DataFrame(Pygsheets.sh1[0].get_all_records())
    df_g = df.loc[cas_list, :]

    df2_g = pd.DataFrame(Pygsheets.sh2[0].get_all_records())

    df_g.to_excel(r"c:\Users\sbolushevsky\Documents\chemicals\Chemical_Orders_Receiving.xlsx", index=False)

    names = ['Chemical Name', 'CAS # (N/A if no CAS)', 'Amount', 'Units', 'Barcode', 'Supplier', 'Comments',
             'Destination', 'Date Received (Use Ctrl+;)', 'Container type', 'Physical State',
             'Segregation Category', 'Hazard Designation']
    new_names = ["Container Name", "CAS", "Container Size", "Size Units", "Barcode", "Supplier",
                 "Container Comments",
                 "Location", "Date Acquired", "Container Type", "Physical State", "Segregation Category",
                 "Hazard Designation"]

    d = dict(zip(names, new_names))

    df2_g.rename(columns=d, inplace=True)
    df2_import = df2_g.loc[cas_list, new_names]
    a, _ = df2_import.shape
    print(f"\n{a} NEW item(s) is being updated")
    print(df2_import)
    df2_import.to_excel(r"c:\Users\sbolushevsky\Documents\chemicals\Chemical_Inventory_Import.xlsx",
                        columns=new_names, index=False)

    # Hiding rows
    l2 = [i for i in df_g["Barcode"].index]

    for i in l2:
        sheet1[0].hide_dimensions(i + 2, dimension="ROWS")
        sheet2[0].hide_dimensions(i + 2, dimension="ROWS")

    #os.startfile(r"c:\Users\sbolushevsky\Documents\chemicals\reagent label_lbx", "open")
    subprocess.run('reagent_label.lbx', shell=True)
    upload()
    print("_" * 130)

    #return df_g["Person Ordering", "Chemical Name", "Hazard Designation"]


class Pygsheets:
    now = datetime.now()
    current_date = now.strftime("%m/%d/%Y")
    gc = pygsheets.authorize(service_file="C:/Users/sbolushevsky/AppData/Roaming/pygsheets/service_account.json")

    sh1 = gc.open("Chemical Orders Receiving")
    sh2 = gc.open("Chemical Inventory Import Template")

    df = pd.DataFrame(sh1[0].get_all_records())
    df2 = pd.DataFrame(sh2[0].get_all_records())


class Chemicals(Pygsheets):

    def __init__(self, cas):
        Pygsheets.df = pd.DataFrame(Pygsheets.sh1[0].get_all_records())
        self.cas = cas
        self.index = Pygsheets.df[Pygsheets.df.iloc[:, 9].str.contains(self.cas.strip(), na=False)].index
        self.L = [self.index[i] for i in range(len(self.index)) if Pygsheets.df2.iloc[self.index[i], 13] == "FALSE"]
        self.number = len(self.L)
        super().__init__()

    def show(self):
        # len(self.index)

        print(f"Found: {self.number}")
        print(Pygsheets.df.iloc[self.L, 0:11])

    def cas_list(self):
        return list(Pygsheets.df.iloc[self.L, 0:11].index.values)


class Locations(Pygsheets):

    def __init__(self):
        self.df_2 = pd.DataFrame(Pygsheets.sh1[1].get_all_records())
        self.containers = self.df_2.loc[0:9, "Containers"]
        self.locations = self.df_2.iloc[0:59, 2]
        self.locations2 = self.df_2.iloc[0:59, 3]

    def show_containers(self):
        print(self.containers)


def search():
    cas = input("\nPut in CAS: ")

    chemicals = Chemicals(cas)
    chemicals.show()
    locations = Locations()
    cas_list = []

    if chemicals.number > 0:

        question = input("\nPut in ALL? (y/n): ")
        if question == "y":

            cas_list.extend(chemicals.cas_list())
            locations.show_containers()
            container_index = int(input("\nChoose container's index: "))

            for i in range(chemicals.number):
                Pygsheets.sh1[0].update_value((chemicals.L[i] + 2, 13), Pygsheets.current_date)
                Pygsheets.sh2[0].update_value((chemicals.L[i] + 2, 14), 'TRUE')
                Pygsheets.sh1[0].update_value((chemicals.L[i] + 2, 14), locations.containers[int(container_index)])

            location_q = input("\nMove everything to one location? (y/n): ")

            if location_q == "y":
                print(locations.locations2)
                location_index = input("\nChoose location's index: ")

                for i in range(chemicals.number):
                    Pygsheets.sh1[0].update_value((int(chemicals.L[i]) + 2, 15),
                                                  locations.locations[int(location_index)])
            else:
                for i in range(chemicals.number):
                    chemical_index = int(input(f"\nChoose chemical's index {chemicals.L}: "))
                    location_index = int(input("\nChoose location's index: "))
                    Pygsheets.sh1[0].update_value((int(chemical_index) + 2, 15),
                                                  locations.locations[int(location_index)])
                    chemicals.L.remove(chemical_index)
        else:
            chemical_index = int(input(f"\nChoose chemical's index {chemicals.L}: "))
            Pygsheets.sh1[0].update_value((chemical_index + 2, 13), Pygsheets.current_date)
            Pygsheets.sh2[0].update_value((chemical_index + 2, 14), 'TRUE')

            locations.show_containers()
            container_index = int(input("\nChoose container's index: "))

            Pygsheets.sh1[0].update_value((chemical_index + 2, 14), locations.containers[int(container_index)])

            print(locations.locations2)
            location_index = input("\nChoose location's index: ")

            Pygsheets.sh1[0].update_value((chemical_index + 2, 15), locations.locations[int(location_index)])

            cas_list.append(chemical_index)

    elif chemicals.number == 0:
        print("\nChemical was not found")

    df_today = Pygsheets.df[Pygsheets.df["Date Received (Use Ctrl+;)"] == Pygsheets.current_date]
    a, _ = df_today.shape

    print(f"\nSo far {a} chemicals were registered today")

    return list(set(cas_list))


def main():
    cas_list = []
    while True:

        cas_list.extend(search())
        files = input("Generate files/hide rows/update inventory/send email? (y/n): ")

        if files == "y":

            # df2 = Pygsheets.df2[Pygsheets.df2["Date Received (Use Ctrl+;)"] == Pygsheets.current_date]

            generate_files(Pygsheets.sh1, Pygsheets.sh2, cas_list)
            email_send.main()
            cas_list.clear()

        else:
            print("Files were not generated")
            continue


if __name__ == "__main__":
    main()
