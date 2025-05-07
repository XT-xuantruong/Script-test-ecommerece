import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import requests

# Đường dẫn đến ChromeDriver
CHROMEDRIVER_PATH = "E:\\chromeDriver\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# URL của trang đăng ký
REGISTER_URL = "http://localhost:5173/register"
SUCCESS_URL = "http://localhost:5173/"  # URL của trang sau khi đăng ký thành công

# Đường dẫn file Excel
INPUT_FILE = "../data/data_test2.xlsx"
OUTPUT_FILE = "../Result/test_register_results.xlsx"

# Kiểm tra file ChromeDriver
if not os.path.isfile(CHROMEDRIVER_PATH):
    print(f"ChromeDriver not found at: {CHROMEDRIVER_PATH}")
    print("Please check the path or download ChromeDriver from https://chromedriver.chromium.org/downloads")
    exit(1)

# Kiểm tra file Excel đầu vào
if not os.path.isfile(INPUT_FILE):
    print(f"Input file not found: {INPUT_FILE}")
    print("Please check the Excel file path.")
    exit(1)

# Kiểm tra xem trang web có đang chạy không
try:
    response = requests.get(REGISTER_URL, timeout=5)
    if response.status_code != 200:
        print(f"Cannot access {REGISTER_URL}. Status code: {response.status_code}")
        print("Please ensure the server is running (npm run dev) and the URL is correct.")
        exit(1)
except requests.exceptions.RequestException as e:
    print(f"Cannot connect to {REGISTER_URL}: {str(e)}")
    print("Please check if the server is running (npm run dev).")
    exit(1)

# Đọc file Excel chứa test cases
try:
    df = pd.read_excel(INPUT_FILE, sheet_name="Register-web")
    # Drop rows where 'Test Case ID' is NaN
    df = df.dropna(subset=['Test Case ID'])
    # Filter only the register test cases
    df = df[df['Test Case ID'].str.startswith('[Register-')]
except Exception as e:
    print(f"Error reading Excel file: {str(e)}")
    exit(1)

# Kiểm tra các cột cần thiết
required_columns = ['Test Case ID', 'Test Case Description', 'Lastname', 'Firstname', 'Email', 'Phone', 'Address', 'Password', 'Confirm password', 'Platform', 'Expected Result', 'Actual result', 'Result']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"Excel file is missing columns: {missing_columns}")
    exit(1)

# Kiểm tra cột "Expected Result" có trống không
if df['Expected Result'].isna().any() or (df['Expected Result'] == '').any():
    print("The 'Expected Result' column contains empty values. Please fill in all expected results before running the script.")
    exit(1)

# Đảm bảo cột "Actual result" và "Result" rỗng trước khi chạy
df['Actual result'] = ''
df['Result'] = ''

# Khởi tạo WebDriver
try:
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)
except Exception as e:
    print(f"Cannot initialize ChromeDriver: {str(e)}")
    print("Please check if ChromeDriver and Chrome versions are compatible.")
    exit(1)

# Hàm kiểm tra đăng ký
def test_register(lastname, firstname, email, phone, address, password, confirm_password, platform, expected_result):
    try:
        # Mở trang đăng ký
        driver.get(REGISTER_URL)
        time.sleep(3)  # Wait for the page to load

        # Tìm các trường nhập liệu
        try:
            first_name_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "first_name"))
            )
        except TimeoutException:
            return "Failed", "First name field not found (ID: first_name). Please check the HTML."

        try:
            last_name_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "last_name"))
            )
        except TimeoutException:
            return "Failed", "Last name field not found (ID: last_name). Please check the HTML."

        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
        except TimeoutException:
            return "Failed", "Email field not found (ID: email). Please check the HTML."

        try:
            phone_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "phone"))
            )
        except TimeoutException:
            return "Failed", "Phone field not found (ID: phone). Please check the HTML."

        try:
            address_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "address"))
            )
        except TimeoutException:
            return "Failed", "Address field not found (ID: address). Please check the HTML."

        try:
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
        except TimeoutException:
            return "Failed", "Password field not found (ID: password). Please check the HTML."

        try:
            confirm_password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "confirmPassword"))
            )
        except TimeoutException:
            return "Failed", "Confirm password field not found (ID: confirmPassword). Please check the HTML."

        try:
            accept_terms_checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "acceptTerms"))
            )
        except TimeoutException:
            return "Failed", "Accept terms checkbox not found (ID: acceptTerms). Please check the HTML."

        # Nhập dữ liệu
        first_name_field.clear()
        last_name_field.clear()
        email_field.clear()
        phone_field.clear()
        address_field.clear()
        password_field.clear()
        confirm_password_field.clear()

        if firstname:
            first_name_field.send_keys(firstname)
        if lastname:
            last_name_field.send_keys(lastname)
        if email:
            email_field.send_keys(email)
        if phone:
            phone_field.send_keys(str(phone))
        if address:
            address_field.send_keys(address)
        if password:
            password_field.send_keys(password)
        if confirm_password:
            confirm_password_field.send_keys(confirm_password)

        # Tích chọn checkbox "Accept Terms" using JavaScript for reliability
        driver.execute_script("arguments[0].scrollIntoView(true);", accept_terms_checkbox)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "acceptTerms")))
        if not accept_terms_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", accept_terms_checkbox)

        # Tìm nút đăng ký
        try:
            register_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "register_button"))
            )
        except TimeoutException:
            driver.save_screenshot("error_screenshot.png")  # Debug screenshot
            print("Page source:", driver.page_source)  # Debug page source
            return "Failed", "Register button not found (ID: register_button). Please check the HTML."

        # Kiểm tra trạng thái của nút
        is_button_enabled = register_button.is_enabled()
        print(f"Button enabled status: {is_button_enabled}")  # Debug log

        if not is_button_enabled:
            # Nếu nút bị vô hiệu hóa, kiểm tra lỗi validation ngay lập tức
            try:
                error_elements = driver.find_elements(By.CLASS_NAME, "text-red-500")
                if error_elements:
                    error_message = error_elements[0].text
                    actual_result = f"Register failed"
                else:
                    error_elements = driver.find_elements(By.CLASS_NAME, "text-red-700")
                    if error_elements:
                        error_message = error_elements[0].text
                        actual_result = f"Register failed"
                    else:
                        actual_result = "Register failed"
                if "failed" in expected_result.lower():
                    return "Passed", actual_result
                else:
                    return "Failed", actual_result
            except NoSuchElementException:
                actual_result = "Register failed"
                return "Failed", actual_result

        # Nếu nút không bị vô hiệu hóa, nhấn nút đăng ký
        driver.execute_script("arguments[0].scrollIntoView(true);", register_button)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "register_button")))
        driver.execute_script("arguments[0].click();", register_button)
        time.sleep(3)  # Đợi phản hồi
        # Kiểm tra kết quả
        try:
            # Normalize URLs by removing trailing slashes for comparison
            WebDriverWait(driver, 10).until(
                lambda driver: driver.current_url.rstrip('/') == SUCCESS_URL.rstrip('/')
            )
            actual_result = "Register successfully"
        except TimeoutException:
            # Kiểm tra lỗi về độ dài mật khẩu trước
            try:
                error_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "text-red-700"))
                )
                if "must not exceed 20 characters" in error_element.text.lower():
                    actual_result = f"Register failed"
                else:
                    actual_result = "Register failed - No specific error found"
            except TimeoutException:
                actual_result = "Register failed - No error message found"

        if actual_result.lower() == expected_result.lower():
            return "Passed", actual_result
        else:
            return "Failed", actual_result

    except Exception as e:
        return "Failed", f"Error during testing: {str(e)}"

# Duyệt qua từng test case và thực hiện kiểm thử
for index, row in df.iterrows():
    test_id = row['Test Case ID']
    description = row['Test Case Description']
    lastname = row['Lastname']
    firstname = row['Firstname']
    email = row['Email']
    phone = row['Phone']
    address = row['Address']
    password = row['Password']
    confirm_password = row['Confirm password']
    platform = row['Platform']
    expected_result = str(row['Expected Result']).strip()

    print(f"Running test case: {test_id} - {description}")

    if platform == "WEB":
        result, actual_result = test_register(lastname, firstname, email, phone, address, password, confirm_password, platform, expected_result)
        df.at[index, 'Actual result'] = actual_result
        df.at[index, 'Result'] = result
    else:
        df.at[index, 'Actual result'] = 'Only testing on WEB'
        df.at[index, 'Result'] = 'Skipped'

# Đóng trình duyệt
driver.quit()

# Tạo thư mục đầu ra nếu chưa tồn tại
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Ghi kết quả ra file Excel
try:
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Results have been written to file: {OUTPUT_FILE}")
except Exception as e:
    print(f"Error writing to Excel file: {str(e)}")