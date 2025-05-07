import pandas as pd
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import requests

# Paths and URLs
CHROMEDRIVER_PATH = "E:\\chromeDriver\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
BASE_URL = "http://localhost:5173/"
INPUT_FILE = "../data/data_test2.xlsx"
OUTPUT_FILE = "../Result/test_search_results.xlsx"

# Validate ChromeDriver
if not os.path.isfile(CHROMEDRIVER_PATH):
    print(f"ChromeDriver not found at: {CHROMEDRIVER_PATH}")
    print("Please check the path or download ChromeDriver from https://chromedriver.chromium.org/downloads")
    exit(1)

# Validate input Excel file
if not os.path.isfile(INPUT_FILE):
    print(f"Input file not found: {INPUT_FILE}")
    print("Please check the Excel file path.")
    exit(1)

# Check if the server is running
try:
    response = requests.get(BASE_URL, timeout=5)
    if response.status_code != 200:
        print(f"Cannot access {BASE_URL}. Status code: {response.status_code}")
        print("Please ensure the server is running (npm run dev) and the URL is correct.")
        exit(1)
except requests.exceptions.RequestException as e:
    print(f"Cannot connect to {BASE_URL}: {str(e)}")
    print("Please check if the server is running (npm run dev).")
    exit(1)

# Read test data
try:
    df = pd.read_excel(INPUT_FILE, sheet_name="Search-web")
except Exception as e:
    print(f"Error reading Excel file: {str(e)}")
    exit(1)

# Validate required columns
required_columns = ['Test Case ID', 'Test Case Description', 'SearchQuery', 'Platform', 'Expected Result', 'Actual result', 'Result']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"Excel file is missing columns: {missing_columns}")
    exit(1)

# Validate Expected Result column
if df['Expected Result'].isna().any() or (df['Expected Result'] == '').any():
    print("The 'Expected Result' column contains empty values. Please fill in all expected results.")
    exit(1)

# Initialize result columns
df['Actual result'] = ''
df['Result'] = ''

# Initialize WebDriver
try:
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
except Exception as e:
    print(f"Cannot initialize ChromeDriver: {str(e)}")
    print("Please check if ChromeDriver and Chrome versions are compatible.")
    exit(1)

# Test function for search operations
def test_search(test_id, description, search_query, platform, expected_result):
    try:
        # Navigate to home page
        driver.get(BASE_URL)
        time.sleep(2)

        # Find search input
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Tìm kiếm sản phẩm...']"))
        )

        # Ensure input is visible and focused
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
        search_input.click()
        search_input.clear()
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.ENTER)

        # Wait for search results page
        WebDriverWait(driver, 15).until(
            EC.url_contains("/search?q=")
        )
        time.sleep(5)  # Increased wait for Vue.js to render results

        # Check for products or no results
        try:
            products = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
            )
            if expected_result == "Products found":
                # Normalize query to match Header.vue logic
                normalized_query = re.sub(r'\s+', ' ', search_query.strip().lower())
                found_products = []
                for product in products:
                    name_element = None
                    for selector in [
                        "[data-testid='product-name']",
                        ".name",
                        "h3",
                        ".title",
                        "span"
                    ]:
                        try:
                            name_element = product.find_element(By.CSS_SELECTOR, selector)
                            product_name = name_element.text.lower()
                            found_products.append(product_name)
                            if normalized_query in product_name:
                                return "Passed", f"Product '{product_name}' matches query '{normalized_query}'"
                        except NoSuchElementException:
                            continue
                return "Failed", f"No matching product name found for query '{normalized_query}'. Found products: {found_products}"
            else:
                # Products found when none expected
                found_products = []
                for product in products:
                    for selector in [
                        "[data-testid='product-name']",
                        ".name",
                        "h3",
                        ".title",
                        "span"
                    ]:
                        try:
                            name_element = product.find_element(By.CSS_SELECTOR, selector)
                            found_products.append(name_element.text)
                        except NoSuchElementException:
                            continue
                return "Failed", f"Products found when none expected: {found_products}"
        except TimeoutException:
            # Check for "No products found" message or empty list
            try:
                error_message = driver.find_element(By.CSS_SELECTOR, ".text-red-500").text
                if expected_result == "No products found" and "Failed to fetch products" in error_message:
                    return "Passed", "No products found (error message displayed)"
                return "Failed", f"Unexpected error message: {error_message}"
            except NoSuchElementException:
                # Empty list (no products and no error message)
                if expected_result == "No products found":
                    return "Passed", "No products found (empty list)"
                return "Failed", "No products found when products expected"

    except Exception as e:
        # Save screenshot for debugging
        driver.save_screenshot(f"error_{test_id}.png")
        return "Failed", f"Error during testing: {str(e)}"

# Run tests
for index, row in df.iterrows():
    test_id = row['Test Case ID']
    description = row['Test Case Description']
    search_query = str(row['SearchQuery'])
    platform = row['Platform']
    expected_result = str(row['Expected Result']).strip()

    print(f"Running test case: {test_id} - {description}")

    if platform == "WEB":
        result, actual_result = test_search(test_id, description, search_query, platform, expected_result)
        df.at[index, 'Result'] = result
        df.at[index, 'Actual result'] = actual_result
    else:
        df.at[index, 'Result'] = 'Skipped'
        df.at[index, 'Actual result'] = 'Only testing on WEB'

# Close browser
driver.quit()

# Save results
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
try:
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Results have been written to file: {OUTPUT_FILE}")
except Exception as e:
    print(f"Error writing to Excel file: {str(e)}")