from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unittest
import pandas as pd
import time
import os

class CartTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_data = pd.read_excel("../data/data_test2.xlsx", sheet_name="Cart-web")
        cls.test_data = cls.test_data.fillna("")
        cls.test_data["Actual result"] = ""
        cls.test_data["Result"] = ""

    def setUp(self):
        # Chuyển log của ChromeDriver vào một file
        log_file = os.path.join(os.getcwd(), "chromedriver.log")
        self.service = Service(
            executable_path="E:\\chromeDriver\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe",
            log_output=log_file  # Chuyển log vào file chromedriver.log
        )
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.driver.get("http://localhost:5173/login")

    def tearDown(self):
        self.driver.quit()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.test_data.to_excel("../Result/test_cart_results.xlsx", index=False)
        except PermissionError as e:
            print(f"Permission denied while saving results: {str(e)}. Please close the Excel file and retry.")

    def login(self, username, password):
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(username)
            wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))).click()
            time.sleep(3)
            return True
        except TimeoutException as e:
            print(f"Login failed: {str(e)}")
            return False

    def add_to_cart(self):
        self.driver.get("http://localhost:5173/")
        try:
            wait = WebDriverWait(self.driver, 15)
            product = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "product-item")))
            add_to_cart_button = product.find_element(By.XPATH, ".//button[contains(text(), 'Add to Cart')]")
            add_to_cart_button.click()
            time.sleep(3)
            return True
        except TimeoutException as e:
            print(f"Add to cart failed: {str(e)}")
            return False

    def update_test_result(self, test_case_id, actual_result, result):
        index = self.test_data.index[self.test_data["Test Case ID"] == test_case_id].tolist()[0]
        self.test_data.at[index, "Actual result"] = actual_result
        self.test_data.at[index, "Result"] = result

    def test_adding_product_to_cart(self):
        print("Running test case: [Login-20] - Test adding a product to the cart")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-20]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 15)
            product_in_cart = wait.until(EC.presence_of_element_located((By.XPATH, "//td//h2")))
            actual_result = "Product displayed in cart"
            result = "Pass" if product_in_cart.is_displayed() else "Fail"
        except TimeoutException as e:
            actual_result = f"Product not displayed in cart: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-20]", actual_result, result)
        self.assertTrue(result == "Pass", "Product should be displayed in cart")

    def test_viewing_cart_contents(self):
        print("Running test case: [Login-21] - Test viewing cart contents")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-21]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 15)
            product_in_cart = wait.until(EC.presence_of_element_located((By.XPATH, "//td//h2")))
            actual_result = "Product displayed in cart"
            result = "Pass" if product_in_cart.is_displayed() else "Fail"
        except TimeoutException as e:
            actual_result = f"Product not displayed in cart: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-21]", actual_result, result)
        self.assertTrue(result == "Pass", "Product should be displayed in cart")

    def test_increasing_product_quantity(self):
        print("Running test case: [Login-22] - Test increasing product quantity")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-22]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 15)
            plus_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "quantity-increase")))
            plus_button.click()
            time.sleep(2)
            quantity_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            actual_quantity = int(quantity_input.get_attribute("value"))
            actual_result = f"Quantity increased to {actual_quantity}"
            result = "Pass" if actual_quantity == 2 else "Fail"
        except TimeoutException as e:
            actual_result = f"Failed to increase quantity: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-22]", actual_result, result)
        self.assertTrue(result == "Pass", "Quantity should increase to 2")

    def test_calculating_total_amount(self):
        print("Running test case: [Login-23] - Test calculating total amount")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-23]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 15)
            total_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "total-value")))
            total_text = total_element.text
            actual_result = f"Total amount displayed: {total_text}"
            result = "Pass" if total_element.is_displayed() and total_text else "Fail"
        except TimeoutException as e:
            actual_result = f"Total amount not displayed: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-23]", actual_result, result)
        self.assertTrue(result == "Pass", "Total amount should be displayed")

    def test_removing_product_from_cart(self):
        print("Running test case: [Login-24] - Test removing product from cart")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-24]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 20)
            remove_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "remove-button")))
            remove_button.click()
            time.sleep(2)
            success_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
            empty_message = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your cart is empty')]")))
            actual_result = "Displayed 'Deleted product successful' and cart is empty"
            result = "Pass" if success_message.is_displayed() and empty_message.is_displayed() else "Fail"
        except TimeoutException as e:
            actual_result = f"Failed to remove product or display message: {str(e)}. Check console logs for details."
            result = "Fail"
        self.update_test_result("[Login-24]", actual_result, result)
        self.assertTrue(result == "Pass", "Should display 'Deleted product successful' and cart empty")

    def test_adding_same_product_multiple_times(self):
        print("Running test case: [Login-25] - Test adding same product multiple times")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-25]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 15)
            quantity_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            actual_quantity = int(quantity_input.get_attribute("value"))
            actual_result = f"Quantity is {actual_quantity}"
            result = "Pass" if actual_quantity == 2 else "Fail"
        except TimeoutException as e:
            actual_result = f"Failed to verify quantity: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-25]", actual_result, result)
        self.assertTrue(result == "Pass", "Quantity should be 2")

    def test_checkout_with_empty_cart(self):
        print("Running test case: [Login-26] - Test checkout with empty cart")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-26]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 15)
            checkout_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Proceed to Checkout')]")))
            is_disabled = checkout_button.get_attribute("disabled") == "true"
            empty_message = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your cart is empty')]")))
            actual_result = "Displayed 'Your cart is empty' message; Checkout button disabled"
            result = "Pass" if empty_message.is_displayed() and is_disabled else "Fail"
        except TimeoutException as e:
            actual_result = f"Failed to display empty cart message or verify button state: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-26]", actual_result, result)
        self.assertTrue(result == "Pass", "Should display 'Your cart is empty' message")

    def test_add_products_to_cart_after_login(self):
        print("Running test case: [Login-27] - Test add products to cart after login")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-27]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 15)
            product_in_cart = wait.until(EC.presence_of_element_located((By.XPATH, "//td//h2")))
            quantity_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            actual_quantity = int(quantity_input.get_attribute("value"))
            actual_result = f"Product displayed in cart, quantity {actual_quantity}"
            result = "Pass" if product_in_cart.is_displayed() and actual_quantity == 1 else "Fail"
        except TimeoutException as e:
            actual_result = f"Product not displayed in cart or quantity incorrect: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-27]", actual_result, result)
        self.assertTrue(result == "Pass", "Cart should display the selected product, quantity 1")

    def test_product_quantity_reduction(self):
        print("Running test case: [Login-28] - Test product quantity reduction")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-28]"].iloc[0]
        self.login(test_case["Username"], test_case["Password"])
        self.add_to_cart()
        self.driver.get("http://localhost:5173/cart")
        try:
            wait = WebDriverWait(self.driver, 20)
            plus_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "quantity-increase")))
            plus_button.click()
            time.sleep(2)
            minus_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "quantity-decrease")))
            minus_button.click()
            time.sleep(2)
            quantity_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            actual_quantity = int(quantity_input.get_attribute("value"))
            actual_result = f"Quantity decreased to {actual_quantity}"
            if actual_quantity == 1:
                minus_button.click()
                time.sleep(2)
                empty_message = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your cart is empty')]")))
                success_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
                actual_result += "; Cart is empty"
                result = "Pass" if empty_message.is_displayed() and success_message.is_displayed() else "Fail"
            else:
                result = "Fail"
        except TimeoutException as e:
            actual_result = f"Failed to decrease quantity or verify empty cart: {str(e)}. Check console logs for details."
            result = "Fail"
        self.update_test_result("[Login-28]", actual_result, result)
        self.assertTrue(result == "Pass", "Quantity should decrease to 1 and show empty cart message if 0")

    def test_add_products_before_login(self):
        print("Running test case: [Login-29] - Test add products before login")
        test_case = self.test_data[self.test_data["Test Case ID"] == "[Login-29]"].iloc[0]
        self.driver.get("http://localhost:5173/")
        try:
            wait = WebDriverWait(self.driver, 15)
            product = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "product-item")))
            add_to_cart_button = product.find_element(By.XPATH, ".//button[contains(text(), 'Add to Cart')]")
            add_to_cart_button.click()
            self.driver.get("http://localhost:5173/cart")
            wait.until(EC.url_to_be("http://localhost:5173/login"))
            actual_result = "Redirected to login page"
            result = "Pass" if self.driver.current_url == "http://localhost:5173/login" else "Fail"
        except TimeoutException as e:
            actual_result = f"Failed to redirect to login page: {str(e)}"
            result = "Fail"
        self.update_test_result("[Login-29]", actual_result, result)
        self.assertTrue(result == "Pass", "Should redirect to login page")

if __name__ == "__main__":
    unittest.main()