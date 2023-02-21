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
        # Iniciar sesión en neopets
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
        # Acceder a la página de "Quick Stock" en neopets para ver el inventario
        self.driver.get("https://www.neopets.com/quickstock.phtml?r=")
        time.sleep(8)

        # Seleccionar el lenguaje inglés en la página
        select_element = Select(self.driver.find_element(by='xpath', value='//select[@name="lang"]'))
        time.sleep(2)
        select_element.select_by_value("en")
        time.sleep(3)

        # Buscar el botón "Go!"
        go_button = self.driver.find_element(By.XPATH, "//td[@valign='top']//input[@type='submit']")

        # Clickear el botón "Go!"
        go_button.click()
        time.sleep(6)

        html_code = self.driver.page_source

        # Buscar la tabla en el código HTML
        start_text = '''<tr bgcolor="#FFFFFF">'''
        end_text = '''<tr bgcolor="#ffffff"><td colspan="7">&nbsp'''
        start_index = html_code.find(start_text)
        end_index = html_code.find(end_text)
        tabla_html = html_code[start_index:end_index]
        with open("inventorytemplisthtml.txt", "w") as inventorytemplist:
            inventorytemplist.write(html_code)
        return tabla_html

    def convert_html_list(self, inventory_html):
        # Convertir el código HTML en una lista de objetos
        soup = BeautifulSoup(inventory_html, 'html.parser')

        # Extraer los elementos de la tabla
        td_tags = soup.find_all('td', {'align': 'left'})
        item_list = [tag.text for tag in td_tags]
        item_list = list(set(item_list))

        print(item_list)
        return item_list


    def submit_shopitems(self):
        # Esperamos a que el botón de selección esté listo
        checkbox_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//tr[@bgcolor="#eeeebb"]//input[@name="checkall" and @type="radio" and @onclick="check_all(1); this.checked = true;"]')))
        time.sleep(3)
        # Hacemos clic en el botón de selección
        checkbox_button.click()
        time.sleep(3)
        # Esperamos a que el botón de envío esté listo
        submit_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Submit"][@onclick=" if (!check_discard()) { return false; } "]')))
        time.sleep(3)
        # Hacemos clic en el botón de envío
        submit_button.click()
        time.sleep(3)

    def shopwiz_search(self, item):
        # Reemplazamos los espacios en blanco por símbolos "+" para la búsqueda
        item = item.replace(" ", "+")
        self.driver.get(f"https://www.neopets.com/shops/wizard.phtml?string={item}")
        self.driver.refresh()
        time.sleep(3)
        # Esperamos a que esté listo el botón de búsqueda y hacemos clic en él usando JS
        search_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="button-search-white"]')))
        self.driver.execute_script("arguments[0].click();", search_button)
        time.sleep(5)

    def get_cheapest_price(self):
        # Obtenemos el código fuente de la página de resultados de búsqueda
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
            # Eliminamos los caracteres no numéricos y convertimos a entero
            precio_digitos = re.sub('\D', '', precio_str)  # remove non-digit characters
            precio_int  = int(precio_digitos)  # convert to integer
            print(precio_int)
            return precio_int

    def price_min(self):
        preciotemp_list = []
        i = 0
        # Realizamos 8 búsquedas
        while i < 8:
            refreshwiz = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@id="resubmitWizard"]')))
            # Refrescamos la página del Shop Wizard para obtener nuevos resultados
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
        print("Precio mínimo -10%: " + str(buyprice))
        return buyprice


    def get_price_list(self, item_list):
        price_list = []
        for item in item_list:
            # Realiza la busqueda en el wizard de la tienda
            self.shopwiz_search(item)
            print("Precio de " + item)
            # Obtiene el precio mas bajo del item
            precio_min = self.get_cheapest_price()
            while not precio_min:
                # Si no se encuentra el precio, ejecuta la busqueda de nuevo
                print("Precio no encontrado. Ejecutando búsqueda de Shop Wizard de nuevo...")
                time.sleep(1)
                self.get_inventory_html()
                self.shopwiz_search(item)
                print("Precio de " + item)
                precio_min = self.get_cheapest_price()
            # Obtiene el precio minimo de compra
            precio_tienda =  self.price_min()
            price_list.append(precio_tienda)
        print(price_list)
        return price_list


    def go_store(self):
        self.driver.get("https://www.neopets.com/market.phtml?type=your&view=&obj_name=&lim=30&order_by=")
        time.sleep(4)

        # Encuentra el elemento select por atributo name
        select_element = Select(self.driver.find_element(by='xpath', value='//select[@name="lang"]'))

        # Selecciona la opción con el valor "en" para inglés
        select_element.select_by_value("en")

        # Encuentra el botón "¡Ir!" por nombre de clase
        go_button = self.driver.find_element(By.XPATH, "//td[@valign='top']//input[@type='submit']")
        go_button.click()
        time.sleep(3)
        stock_html = self.driver.page_source
        time.sleep(2)
        
        # Encuentra la tabla en el código HTML
        start_text = '''<form action="process_market.phtml" method="post">'''
        end_text = '''</tr></tbody></table><center></center>'''
        start_index = stock_html.find(start_text)
        end_index = stock_html.find(end_text)
        stock_html = stock_html[start_index:end_index]

        # Escribe el código HTML en un archivo
        with open("testin.txt", "w") as inventorytemplist:
            inventorytemplist.write(stock_html)

        return stock_html

    def get_shop_numbers(self, stock_html):
        # Parsear el HTML con Beautiful Soup
        soup = BeautifulSoup(stock_html, "html.parser")

        # Encontrar la tabla con la información relevante
        table = soup.find("table", {"cellspacing": "0", "cellpadding": "3", "border": "0"})

        # Extraer los nombres de las columnas de la tabla
        headers = [th.get_text() for th in table.find_all("th")]

        # Extraer las filas de datos de la tabla
        data = []
        for tr in table.find_all("tr")[1:]:
            row = []
            for td in tr.find_all("td"):
                row.append(td.get_text())
            data.append(row)
        # Añadir nombres de columna
        column_names = ['Item_Name', 'Quantity', 'Quantity', 'Type', 'Type', 'Type', 'Type']
        data.insert(0, column_names)
        # Crear un DataFrame de Pandas con los datos
        df = pd.DataFrame(data[1:-1], columns=data[0])

        # Guardar el DataFrame en un archivo CSV
        df.to_csv("testin.csv", index=False)
        stock_list = df['Item_Name'].tolist()
        print(stock_list)
        return stock_list

    def get_item_dict(self, item_list, shop_index_list):
        matching_indices = []
        # Crea una lista de los índices donde se encuentran los ítems de la lista de la tienda
        for item in item_list:
            if item in shop_index_list:
                matching_indices.append(shop_index_list.index(item))
        item_index_tuple = []
        # Crea una tupla con cada ítem y su respectivo índice en la lista de la tienda
        for i, item in enumerate(item_list):
            item_index_tuple.append((item, matching_indices[i] + 1))

        return item_index_tuple

    def get_price_dict(self, price_list, item_tuple):
        # Crea una tupla con el precio de cada ítem y su respectivo índice en la lista de la tienda
        price_tuple = tuple((str(num), item_tuple[i][1]) for i, num in enumerate(price_list))
        return price_tuple

    def set_prices(self, price_tuple):
        for item in price_tuple:
            index_num = str(item[1])
            input_elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//input[@name='cost_{index_num}']")))
            input_elem.clear() # Borra lo que haya en este campo si hay un valor existente
            time.sleep(1)
            input_elem.send_keys(str(item[0]))
            time.sleep(1)
        # Espera a que el elemento se pueda clickear
        update_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Update"]')))
        time.sleep(3)
        # Click en el elemento
        update_button.click()
        print("Success!")
        time.sleep(5)

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


while True:
    try:
        To_Shop = To_Shop()
        To_Shop.run("username", "password")
        break  # Sal del bucle si el código se ejecuta correctamente
    except WebDriverException:
        driver.quit()  # Cierra el driver si un error ocurre
#To_Shop = To_Shop()
#To_Shop.run("username", "password")
