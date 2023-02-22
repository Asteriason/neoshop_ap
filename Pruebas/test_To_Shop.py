from unittest import TestCase
from to_shop import To_Shop
from unittest.mock import patch, MagicMock
from io import StringIO


class TestToShop(TestCase):
    def setUp(self):
        self.username = "username"
        self.password = "password"
        self.to_shop = To_Shop()

    def test_login_success(self):
        self.to_shop.login(self.username, self.password)
        self.assertEqual(self.to_shop.driver.current_url, "https://www.neopets.com/index.phtml")
        self.assertEqual(self.to_shop.driver.title, "¡Bienvenido a Neopets!")

    def test_get_inventory_html(self):
        self.to_shop.login(self.username, self.password)
        inventory_html = self.to_shop.get_inventory_html()
        self.assertTrue('''<td align="left">''' in inventory_html)
    def test_convert_html_list(self):
            html = '''
            <tr bgcolor="#ffffff"><td align="left"><input name="discard_4725_5" type="checkbox" value="on"><b>Item Name Here</b><br><input name="count_4725_5" type="hidden" value="5"></td><td>2023<br><input name="price_4725_5" type="hidden" value="2023"></td><td>shops<br><input name="shop_name_4725_5" type="hidden" value="shops"></td></tr>
            <tr bgcolor="#ffffff"><td align="left"><input name="discard_25002_1" type="checkbox" value="on"><b>Another Item Name</b><br><input name="count_25002_1" type="hidden" value="1"></td><td>5050<br><input name="price_25002_1" type="hidden" value="5050"></td><td>shops<br><input name="shop_name_25002_1" type="hidden" value="shops"></td></tr>
            '''
            expected_output = ['Item Name Here', 'Another Item Name']
            expected_output2 = ['Another Item Name', 'Item Name Here']
            output = self.to_shop.convert_html_list(html)
            self.assertIn(output, [expected_output, expected_output2])


    def test_submit_shopitems(self):
        self.to_shop.login('username', 'password')
        self.to_shop.get_inventory_html()
        self.to_shop.submit_shopitems()
        self.assertNotIn('''<input type="radio" name="radio_arr[1]" value="deposit" ondblclick="this.checked = false; checkall[1]''', self.to_shop.driver.page_source)

    def test_shopwiz_search(self):
        # Test that shopwiz_search function navigates to the correct search results page
        with patch('builtins.input', return_value='item name'):
            self.to_shop.login('username', 'password')
            self.to_shop.shopwiz_search('item name')
            expected_url = f"https://www.neopets.com/shops/wizard.phtml?string=item+name"
            self.assertEqual(self.to_shop.driver.current_url, expected_url)

    def test_price_min(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            temprice_list = [500,300,100]
            self.to_shop.price_min(temprice_list)
            expected_output = "Precio mínimo -10%: 90\n"
            self.assertEqual(fake_out.getvalue(), expected_output)


    def test_get_shop_numbers(self):
        with open('testin.txt', 'r') as file:
            stock_html = file.read()
        # Call the get_price_list method
        price_list = self.to_shop.get_shop_numbers(stock_html)
        print(price_list)
        # Check that the price list returned by the method is correct
        expected_price_list = ['Lightning Wand', 'Mau Codestone','Catamara','Pant Devil Punch Bag','Splime','Reject Curly Shaped Sand','Biyako']
        self.assertEqual(price_list, expected_price_list)


    def test_get_item_dict(self):
        item_list = ["apple", "banana", "orange"]
        shop_index_list = ["orange", "banana", "pear", "apple"]
        expected_output = [("apple", 4), ("banana", 2), ("orange", 1)]
        assert self.to_shop.get_item_dict(item_list, shop_index_list) == expected_output


    def test_get_price_dict(self):
        price_list = [33, 250, 375]
        item_tuple = [('apple', 1), ('banana', 2), ('orange', 3)]
        expected_output = (('33', 1), ('250', 2), ('375', 3))
        self.assertEqual(self.to_shop.get_price_dict(price_list, item_tuple), expected_output)