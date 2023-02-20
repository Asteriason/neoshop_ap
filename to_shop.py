from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import csv
import pandas as pd
from selenium.webdriver.support.ui import Select
import re

class To_Shop:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def login(self, username, password):
        self.driver.get("https://www.neopets.com/login/")
        time.sleep(3)

        # Esperar a que se cargue el elemento para escribir el usuario
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginUsername"))
        )
        username_input.send_keys(username)

        # Esperar a que se cargue el elemento para escribir la contraseña
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginPassword"))
        )
        password_input.send_keys(password)

        # Esperar a que se cargue el botón de login y hacer clic en él
        login_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginButton"))
        )
        login_button.click()
        print("Se inició sesión con éxito")
        time.sleep(3)

    def get_inventory_html(self):
        self.driver.get("https://www.neopets.com/quickstock.phtml?r=")
        time.sleep(8)
        # Find the select element by name attribute
        select_element = Select(self.driver.find_element(by='xpath', value='//select[@name="lang"]'))
        time.sleep(2)
        # Select the option with value "en for English
        select_element.select_by_value("en")
        time.sleep(3)
        # find the "Go!" button by class name
        go_button = self.driver.find_element(By.XPATH, "//td[@valign='top']//input[@type='submit']")

        # click the "Go!" button
        go_button.click()
        time.sleep(6)

        html_code = self.driver.page_source

        # Find the table in the HTML code
        start_text = '''<tr bgcolor="#FFFFFF">'''
        end_text = '''<tr bgcolor="#ffffff"><td colspan="7">&nbsp'''
        start_index = html_code.find(start_text)
        end_index = html_code.find(end_text)
        tabla_html = html_code[start_index:end_index]
        with open("inventorytemplisthtml.txt", "w") as inventorytemplist:
            inventorytemplist.write(html_code)
        return tabla_html

    def convert_html_list(self, inventory_html):
        # Parse the HTML code using Beautiful Soup
        soup = BeautifulSoup(inventory_html, 'html.parser')

        # Extract the table data
        td_tags = soup.find_all('td', {'align': 'left'})
        item_list = [tag.text for tag in td_tags]
        item_list = list(set(item_list))

        print(item_list)
        return item_list

    def submit_shopitems(self):

        checkbox_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//tr[@bgcolor="#eeeebb"]//input[@name="checkall" and @type="radio" and @onclick="check_all(1); this.checked = true;"]')))
        time.sleep(3)
        checkbox_button.click()
        time.sleep(3)
        submit_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Submit"][@onclick=" if (!check_discard()) { return false; } "]')))
        time.sleep(3)
        submit_button.click()
        time.sleep(3)


    def shopwiz_search(self, item):
        item = item.replace(" ", "+")
        self.driver.get(f"https://www.neopets.com/shops/wizard.phtml?string={item}")
        self.driver.refresh()
        time.sleep(3)
        #search_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@id="shopwizard"]')))
        #search_input.send_keys(text)
        time.sleep(3)

        search_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="button-search-white"]')))
        self.driver.execute_script("arguments[0].click();", search_button)

        #search_input.send_keys(Keys.RETURN)
        time.sleep(5)

    def get_cheapest_price(self):

        swresults_html = self.driver.page_source
        with open("shopwiztemp.txt", "w") as shopwiztemp:
            shopwiztemp.write(swresults_html)
        time.sleep(5)
        start_text = '''<div class="wizard-results-price">'''
        end_text = '''</div></li>'''
        start_index = swresults_html.find(start_text)
        end_index = swresults_html.find(end_text)
        precio_min = swresults_html[start_index:end_index]
        precio_str = precio_min
        if not precio_min:
            precio_min = ""
            return precio_min
        else:
            precio_digitos = re.sub('\D', '', precio_str)  # remove non-digit characters
            precio_int  = int(precio_digitos)  # convert to integer
            print("Precio:")
            print(precio_int)
            return precio_int

    def price_avg(self):
        #preciotemp = self.get_cheapest_price()
        preciotemp_list = []
        #preciotemp_list.append(preciotemp)
        i = 0
        while i < 8:
            refreshwiz = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@id="resubmitWizard"]')))
            refreshwiz.click()
            time.sleep(1)
            preciotemp = self.get_cheapest_price()
            preciotemp_list.append(preciotemp)
            i+=1

        df = pd.DataFrame(preciotemp_list, columns=['price'])
        print(df)
        minprice = df['price'].min()
        buyprice = minprice - minprice*0.1
        buyprice = round(buyprice)

        print(preciotemp_list)
        print(buyprice)
        return buyprice


    def get_price_list(self, item_list):
        price_list = []
        for item in item_list:
            self.shopwiz_search(item)
            precio_min = self.get_cheapest_price()
            while not precio_min:
                print("Price not found. Running shopwiz search again...")
                time.sleep(1)
                self.get_inventory_html()
                self.shopwiz_search(item)
                precio_min = self.get_cheapest_price()
            precio_tienda =  self.price_avg()
            price_list.append(precio_tienda)
        print(price_list)
        return price_list


    def go_store(self):
        self.driver.get("https://www.neopets.com/market.phtml?type=your&view=&obj_name=&lim=30&order_by=")
        time.sleep(4)

        # Find the select element by name attribute
        select_element = Select(self.driver.find_element(by='xpath', value='//select[@name="lang"]'))

        # Select the option with value "en for English
        select_element.select_by_value("en")

        # find the "Go!" button by class name
        go_button = self.driver.find_element(By.XPATH, "//td[@valign='top']//input[@type='submit']")
        go_button.click()
        time.sleep(3)
        stock_html = self.driver.page_source
        time.sleep(2)
        # Find the table in the HTML code
        start_text = '''<form action="process_market.phtml" method="post">'''
        end_text = '''</tr></tbody></table><center></center>'''
        start_index = stock_html.find(start_text)
        end_index = stock_html.find(end_text)
        stock_html = stock_html[start_index:end_index]

        with open("testin.txt", "w") as inventorytemplist:
            inventorytemplist.write(stock_html)

        return stock_html

    def get_shop_numbers(self, stock_html):
        # Parse the HTML with Beautiful Soup
        soup = BeautifulSoup(stock_html, "html.parser")
        
        # Find the table with the relevant information
        table = soup.find("table", {"cellspacing": "0", "cellpadding": "3", "border": "0"})

        # Extract the column names from the table
        headers = [th.get_text() for th in table.find_all("th")]

        # Extract the data rows from the table
        data = []
        for tr in table.find_all("tr")[1:]:
            row = []
            for td in tr.find_all("td"):
                row.append(td.get_text())
            data.append(row)
        # Add column names
        column_names = ['Item_Name', 'Quantity', 'Quantity', 'Type', 'Type', 'Type', 'Type']
        data.insert(0, column_names)
        # Create a Pandas DataFrame with the data
        df = pd.DataFrame(data[1:-1], columns=data[0])
        #df = df.drop(df.index[-1])

        # Save the DataFrame to a CSV file
        df.to_csv("testin.csv", index=False)
        stock_list = df['Item_Name'].tolist()
        print(stock_list)
        return stock_list

    def get_item_dict(self, item_list, shop_index_list):
        matching_indices = []
        for item in item_list:
            if item in shop_index_list:
                matching_indices.append(shop_index_list.index(item))
        item_index_tuple = []
        for i, item in enumerate(item_list):
            item_index_tuple.append((item, matching_indices[i] + 1))

        print(item_index_tuple)
        return item_index_tuple

    def get_price_dict(self, price_list, item_tuple):

        print("price_list")
        print(price_list)
        print("item_tuple")
        print(item_tuple)
        
        price_tuple = tuple((str(num), item_tuple[i][1]) for i, num in enumerate(price_list))
        
        print("price_tuple")
        print(price_tuple)
        return price_tuple

    def set_prices(self, price_tuple):
        for item in price_tuple:
            index_num = str(item[1])
            print(index_num)
            input_elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//input[@name='cost_{index_num}']")))
            input_elem.clear() # clear the field in case there is an existing value
            time.sleep(1)
            input_elem.send_keys(str(item[0]))
            time.sleep(1)
        # Wait for the element to be clickable
        update_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Update"]')))
        time.sleep(3)
        # Click the element
        update_button.click()
        time.sleep(2)

    def run(self, username, password):
        self.login(username, password)
        inventory_html = self.get_inventory_html()
        item_list = self.convert_html_list(inventory_html)
        self.submit_shopitems()
        price_list = self.get_price_list(item_list)
        stock_html = self.go_store()
        shop_index_list = self.get_shop_numbers(stock_html)
        item_tuple = self.get_item_dict(item_list, shop_index_list)
        price_tuple = self.get_price_dict(price_list, item_tuple)
        self.set_prices(price_tuple)
        time.sleep(3)
        self.driver.quit()



To_Shop = To_Shop()
To_Shop.run("username", "password")
