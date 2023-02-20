# neoshop_ap
Autopricer for neopets shop.

To_Shop
La clase To_Shop contiene métodos para hacer búsquedas en el sitio web www.neopets.com y obtener información de inventarios, precios y otros detalles relacionados con el comercio de artículos en dicho sitio.

Instalación
Este módulo depende de las siguientes librerías de Python:

selenium
beautifulsoup4
Puede instalarlas usando pip con el siguiente comando:

Copy code
pip install selenium beautifulsoup4
Además, se requiere descargar el controlador del navegador ChromeDriver correspondiente a la versión de Google Chrome que esté utilizando.

Uso
A continuación se describen los métodos principales de la clase To_Shop:

login(username, password): inicia sesión en www.neopets.com utilizando las credenciales proporcionadas en los argumentos username y password.
get_inventory_html(): accede a la página de inventario y devuelve el HTML de la tabla de artículos del inventario en una variable.
convert_html_list(inventory_html): convierte el HTML de la tabla de artículos del inventario en una lista de Python.
submit_shopitems(): marca todos los artículos del inventario para ponerlos en venta y envía el formulario correspondiente.
shopwiz_search(item): busca un artículo en el sitio web utilizando la función de búsqueda del "Shop Wizard".
get_cheapest_price(): devuelve el precio más bajo encontrado por el "Shop Wizard" para el artículo buscado.
price_avg(): calcula el precio mínimo y descuenta el 10% de un artículo buscando su precio en el "Shop Wizard" varias veces.


Para utilizar esta aplicación, es necesario modificar la parte del código donde se encuentra la llamada al método "run" con los datos de inicio de sesión del usuario. En la línea correspondiente, se deben reemplazar los valores "username" y "password" por el nombre de usuario y contraseña correspondientes.

Por otro lado, para ejecutar la aplicación exitosamente, es suficiente con abrir una terminal y escribir el comando "python to_shop.py" en el directorio donde se encuentra el archivo de la aplicación. De esta forma, se iniciará el programa y se podrá utilizar según las instrucciones correspondientes.