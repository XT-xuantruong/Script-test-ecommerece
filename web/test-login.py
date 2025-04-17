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

# URL của trang đăng nhập
LOGIN_URL = "http://localhost:5173/login"
SUCCESS_URL = "http://localhost:5173/"  # URL của trang sau khi đăng nhập thành công

# Đường dẫn file Excel
INPUT_FILE = "../data/data_test2.xlsx"
OUTPUT_FILE = "../Result/test_login_results.xlsx"

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
    response = requests.get(LOGIN_URL, timeout=5)
    if response.status_code != 200:
        print(f"Cannot access {LOGIN_URL}. Status code: {response.status_code}")
        print("Please ensure the server is running (npm run dev) and the URL is correct.")
        exit(1)
except requests.exceptions.RequestException as e:
    print(f"Cannot connect to {LOGIN_URL}: {str(e)}")
    print("Please check if the server is running (npm run dev).")
    exit(1)

# Đọc file Excel chứa test cases
try:
    df = pd.read_excel(INPUT_FILE, sheet_name="Login")  # Assuming login test cases are in Sheet1
except Exception as e:
    print(f"Error reading Excel file: {str(e)}")
    exit(1)

# Kiểm tra các cột cần thiết
required_columns = ['Test Case ID', 'Test Case Description', 'Username', 'Password', 'Platform', 'Expected Result', 'Actual result', 'Result']
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

# Hàm kiểm tra đăng nhập
def test_login(username, password, platform, expected_result):
    try:
        # Mở trang đăng nhập
        driver.get(LOGIN_URL)
        time.sleep(3)  # Wait for the page to load

        # Tìm các trường nhập liệu và nút đăng nhập
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
        except TimeoutException:
            return "Failed", "Email field not found (ID: email). Please check the HTML."

        try:
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
        except TimeoutException:
            return "Failed", "Password field not found (ID: password). Please check the HTML."

        try:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login_button"))
            )
        except TimeoutException:
            return "Failed", "Login button not found (ID: login_button). Please check the HTML."

        # Nhập dữ liệu
        email_field.clear()
        password_field.clear()

        if username:  # Chỉ nhập nếu username không rỗng
            email_field.send_keys(username)
        if password:  # Chỉ nhập nếu password không rỗng
            password_field.send_keys(password)

        # Nhấn nút đăng nhập
        login_button.click()
        time.sleep(3)  # Đợi phản hồi

        # Kiểm tra kết quả
        # Nếu đăng nhập thành công, trang sẽ chuyển hướng đến SUCCESS_URL
        try:
            WebDriverWait(driver, 5).until(
                EC.url_to_be(SUCCESS_URL)
            )
            actual_result = "Login successfully"
            # So sánh với Expected Result
            if actual_result.lower() == expected_result.lower():
                return "Passed", actual_result
            else:
                return "Failed", actual_result
        except TimeoutException:
            # Nếu không chuyển hướng, kiểm tra thông báo lỗi
            try:
                error_elements = driver.find_elements(By.CLASS_NAME, "text-red-500")
                if not error_elements:
                    error_elements = driver.find_elements(By.CLASS_NAME, "text-red-700")
                if error_elements:
                    error_message = error_elements[0].text
                    actual_result = f"Login failed (Error: {error_message})"
                else:
                    actual_result = "Login failed"
                # So sánh với Expected Result
                # For comparison, strip any additional error message details
                actual_result_base = "Login failed"
                if actual_result_base.lower() == expected_result.lower():
                    return "Passed", actual_result
                else:
                    return "Failed", actual_result
            except NoSuchElementException:
                actual_result = "Login failed"
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
    username = row['Username']
    password = row['Password']
    platform = row['Platform']
    expected_result = str(row['Expected Result']).strip()

    print(f"Running test case: {test_id} - {description}")

    if platform == "WEB":
        result, actual_result = test_login(username, password, platform, expected_result)
        df.at[index, 'Result'] = result
        df.at[index, 'Actual result'] = actual_result
    else:
        df.at[index, 'Result'] = 'Skipped'
        df.at[index, 'Actual result'] = 'Only testing on WEB'

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