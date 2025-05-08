import unittest
import time
import re
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from test_data_manager import TestDataManager   


class TestRegisterApp(unittest.TestCase):
    # Khởi tạo các thuộc tính chung cho class
    capabilities = {
        "platformName": "Android",
        "automationName": "uiautomator2",
        "deviceName": "ce0917192499191c027e",
        "app": "D:/nam3/KTPM2/application-8bd28935-27e6-428e-9b9e-109d07ab30c4.apk",

    }
    appium_server_url = "http://127.0.0.1:4723/wd/hub"

    @classmethod
    def setUpClass(cls):
        """Khởi tạo TestDataManager và đọc dữ liệu kiểm thử"""
        cls.data_manager = TestDataManager("D:/nam3/KTPM2/Script-test-ecommerece/data/data_test2.xlsx")
        cls.test_cases = cls.data_manager.read_register_test_data()
        print(f"🔍 Đọc {len(cls.test_cases)} test case đăng ký.")

    def setUp(self):
        """Khởi động Appium và mở ứng dụng trước mỗi test"""
        self.driver = webdriver.Remote(
            self.appium_server_url,
            options=UiAutomator2Options().load_capabilities(self.capabilities),
        )
        self.wait = WebDriverWait(self.driver, 15)
        print("✅ Driver đã khởi động.")

    def tearDown(self):
        """Đóng ứng dụng sau mỗi test"""
        if self.driver:
            self.driver.quit()
            print("✅ Ứng dụng đã đóng.")

    def _clear_field_if_not_empty(self, element):
        """Xóa trường bất kể trạng thái hiện tại"""
        try:
            is_password = element.get_attribute("password") == "true"
            current_text = element.get_attribute("text") or element.get_attribute("value") or ""
            
            print(f"ℹ️ Kiểm tra trường, text='{current_text}', is_password={is_password}")
            
            # Xóa trường bất kể nội dung
            element.clear()
            print(f"✅ Đã xóa trường {'mật khẩu' if is_password else 'không phải mật khẩu'}.")
            return True
            
        except Exception as e:
            print(f"⚠️ Không thể xóa trường: {e}")
            return False

    def _ensure_clean_register_screen(self):
        """Đảm bảo màn hình đăng ký ở trạng thái sạch"""
        try:
            # Kiểm tra và đóng bất kỳ dialog lỗi nào
            buttons = [
                (AppiumBy.XPATH, '//android.widget.Button[@text="OK"]'),
            ]
            for button in buttons:
                try:
                    btn = self.driver.find_element(*button)
                    btn.click()
                    print("✅ Đã đóng dialog lỗi còn sót lại.")
                    time.sleep(1)
                except:
                    continue

            # Kiểm tra xem có đang ở màn hình đăng ký không
            try:
                self.wait.until(
                    EC.presence_of_element_located(
                        (AppiumBy.XPATH, '//android.widget.TextView[@text="Sign Up"]')
                    )
                )
                print("ℹ️ Đã ở màn hình đăng ký.")
            except TimeoutException:
                print("ℹ️ Không ở màn hình đăng ký, giả định đang ở màn hình đăng nhập...")
                # Chuyển sang màn hình đăng ký
                sign_up_link = self.wait.until(
                    EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Sign up"))
                )
                sign_up_link.click()
                time.sleep(2)  # Chờ chuyển màn hình
                # Xác nhận đã ở màn hình đăng ký
                self.wait.until(
                    EC.presence_of_element_located(
                        (AppiumBy.XPATH, '//android.widget.TextView[@text="Sign Up"]')
                    )
                )
                print("✅ Đã chuyển sang màn hình đăng ký.")

        except Exception as e:
            print(f"⚠️ Không thể đảm bảo màn hình đăng ký sạch: {e}")
            raise

    def _verify_fields_empty(self, locators):
        """Xác minh tất cả các trường nhập liệu đều trống"""
        for field in locators:
            if field != "sign_up_button":
                try:
                    input_field = self.driver.find_element(*locators[field])
                    current_text = input_field.get_attribute("text") or input_field.get_attribute("value") or ""
                    is_password = input_field.get_attribute("password") == "true"
                    
                    # Define expected placeholder texts
                    default_texts = ["Full Name", "Email", "Phone Number", "Address", "Password", "Confirm Password", ""]
                    
                    print(f"ℹ️ Xác minh trường {field}, text='{current_text}', is_password={is_password}")
                    
                    # For both password and non-password fields
                    if current_text and current_text not in default_texts:
                        print(f"⚠️ Trường {field} không trống: {current_text}")
                        return False
                except:
                    print(f"⚠️ Không thể kiểm tra trường {field}.")
                    return False
        print("✅ Tất cả các trường đều trống.")
        return True

    def _register(self, username, email, phone, address, password, confirm_password):
        """Thực hiện đăng ký với các thông tin được cung cấp"""
        try:
            # Đảm bảo màn hình đăng ký sạch trước khi bắt đầu
            self._ensure_clean_register_screen()

            # Định nghĩa các locator dựa trên index từ XML
            locators = {
                "full_name": (AppiumBy.XPATH, '//android.widget.EditText[@index="1"]'),
                "email": (AppiumBy.XPATH, '//android.widget.EditText[@index="2"]'),
                "phone": (AppiumBy.XPATH, '//android.widget.EditText[@index="3"]'),
                "address": (AppiumBy.XPATH, '//android.widget.EditText[@index="4"]'),
                "password": (AppiumBy.XPATH, '//android.widget.EditText[@index="5"]'),
                "confirm_password": (AppiumBy.XPATH, '//android.widget.EditText[@index="6"]'),
                "sign_up_button": (AppiumBy.ACCESSIBILITY_ID, "Sign Up")
            }

            # Xóa tất cả các trường trước khi nhập dữ liệu mới
            try:
                for field, locator in locators.items():
                    if field != "sign_up_button":
                        try:
                            input_field = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located(locator)
                            )
                            if self._clear_field_if_not_empty(input_field):
                                print(f"✅ Đã xóa dữ liệu trường {field} trước khi nhập.")
                            else:
                                print(f"ℹ️ Trường {field} đã trống, không cần xóa.")
                        except TimeoutException:
                            print(f"⚠️ Không tìm thấy trường {field} để xóa trước khi nhập, tiếp tục...")
            except Exception as clear_e:
                print(f"⚠️ Không thể xóa dữ liệu các trường trước khi nhập: {clear_e}")

            # Xử lý từng trường nhập liệu
            for field, value in [
                ("full_name", username),
                ("email", email),
                ("phone", phone),
                ("address", address),
                ("password", password),
                ("confirm_password", confirm_password)
            ]:
                if value:
                    try:
                        input_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located(locators[field])
                        )
                        input_field.send_keys(str(value))
                        print(f"✅ Đã nhập dữ liệu vào trường {field}: {value}")
                    except TimeoutException:
                        print(f"⚠️ Không tìm thấy trường {field} để nhập dữ liệu: {value}")

            # Nhấn nút đăng ký
            sign_up_button = self.wait.until(
                EC.element_to_be_clickable(locators["sign_up_button"])
            )
            sign_up_button.click()
            time.sleep(2)  # Chờ phản hồi từ ứng dụng

            # Kiểm tra kết quả đăng ký
            try:
                # Trường hợp đăng ký thành công
                success_dialog = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (AppiumBy.XPATH, '//android.widget.TextView[@text="Success"]')
                    )
                )
                if success_dialog.is_displayed():
                    print("✅ Phát hiện thông báo thành công.")
                    # Nhấn nút OK
                    ok_button = self.wait.until(
                        EC.element_to_be_clickable(
                            (AppiumBy.XPATH, '//android.widget.Button[@text="OK"]')
                        )
                    )
                    ok_button.click()
                    time.sleep(1)
                    # Xác nhận đã chuyển về màn hình đăng nhập
                    try:
                        self.wait.until(
                            EC.presence_of_element_located(
                                (AppiumBy.XPATH, '//android.widget.TextView[@text="Sign Up"]')
                            )
                        )
                        print("❌ Vẫn ở màn hình đăng ký sau khi đăng ký thành công.")
                        return False
                    except TimeoutException:
                        print("✅ Đã chuyển về màn hình đăng nhập.")
                        # Chuyển lại màn hình đăng ký
                        sign_up_link = self.wait.until(
                            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Sign up"))
                        )
                        sign_up_link.click()
                        time.sleep(2)
                        self.wait.until(
                            EC.presence_of_element_located(
                                (AppiumBy.XPATH, '//android.widget.TextView[@text="Sign Up"]')
                            )
                        )
                        print("✅ Đã quay lại màn hình đăng ký.")
                        # Xác minh các trường trống
                        if self._verify_fields_empty(locators):
                            return True
                        else:
                            print("❌ Các trường không trống sau khi đăng ký thành công.")
                            return False
            except TimeoutException:
                # Trường hợp đăng ký thất bại
                try:
                    error_dialog = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[@text="Error"]')
                        )
                    )
                    if error_dialog.is_displayed():
                        print("✅ Phát hiện thông báo lỗi.")
                        # Nhấn nút OK
                        ok_button = self.wait.until(
                            EC.element_to_be_clickable(
                                (AppiumBy.XPATH, '//android.widget.Button[@text="OK"]')
                            )
                        )
                        ok_button.click()
                        time.sleep(1)
                        # Xác nhận vẫn ở màn hình đăng ký
                        try:
                            self.wait.until(
                                EC.presence_of_element_located(
                                    (AppiumBy.XPATH, '//android.widget.TextView[@text="Sign Up"]')
                                )
                            )
                            print("✅ Vẫn ở màn hình đăng ký.")
                            # Xóa tất cả các trường
                            try:
                                for field, locator in locators.items():
                                    if field != "sign_up_button":
                                        try:
                                            input_field = WebDriverWait(self.driver, 5).until(
                                                EC.element_to_be_clickable(locator)
                                            )
                                            if self._clear_field_if_not_empty(input_field):
                                                print(f"✅ Đã xóa dữ liệu trường {field}.")
                                            else:
                                                print(f"⚠️ Không thể xóa trường {field}.")
                                        except TimeoutException:
                                            print(f"⚠️ Không tìm thấy trường {field}, giả định đã trống.")
                            except Exception as clear_e:
                                print(f"⚠️ Không thể xóa dữ liệu các trường nhập: {clear_e}")
                                try:
                                    print("🔍 Trạng thái UI khi lỗi xóa trường:", self.driver.page_source)
                                except:
                                    print("⚠️ Không thể lấy trạng thái UI khi xóa trường.")
                                return False
                            # Xác minh các trường trống
                            if self._verify_fields_empty(locators):
                                return False
                            else:
                                print("❌ Không thể xóa hết các trường sau khi đăng ký thất bại.")
                                return False
                        except TimeoutException:
                            print("❌ Đã rời khỏi màn hình đăng ký sau khi đăng ký thất bại.")
                            return False
                except TimeoutException:
                    print("⚠️ Không tìm thấy thông báo 'Success' hoặc 'Error'.")
                    return False

        except Exception as e:
            print(f"❌ Lỗi khi đăng ký: {e}")
            try:
                print("🔍 Trạng thái UI khi lỗi:", self.driver.page_source)
            except:
                print("⚠️ Không thể lấy trạng thái UI.")
            return False

    def test_register_cases(self):
        """Chạy tất cả test case từ dữ liệu Excel"""
        for test_case in self.test_cases:
            test_id = test_case["Test Case ID"]
            description = test_case["Test Case Description"]
            username = str(test_case["Username"]) if test_case["Username"] else ""
            email = str(test_case["Email"]) if test_case["Email"] else ""
            phone = str(test_case["Phone"]) if test_case["Phone"] else ""
            address = str(test_case["Address"]) if test_case["Address"] else ""
            password = str(test_case["Password"]) if test_case["Password"] else ""
            confirm_password = str(test_case["Confirm password"]) if test_case["Confirm password"] else ""
            expected_result = test_case["Expected Result"]

            print(f"\nĐang chạy: {test_id} - {description}")
            print(f"ℹ️ Dữ liệu: Username='{username}', Email='{email}', Phone='{phone}', "
                  f"Address='{address}', Password='{password}', Confirm Password='{confirm_password}', "
                  f"Expected Result='{expected_result}'")

            register_result = self._register(username, email, phone, address, password, confirm_password)

            try:
                if "success" in expected_result.lower():
                    self.assertTrue(register_result, f"{test_id}: Đăng ký thất bại!")
                    print(f"✅ {test_id} Passed: Đăng ký thành công.")
                    test_case["Actual Result"] = "Register successfully"
                    test_case["Result"] = "Passed"
                else:
                    self.assertFalse(register_result, f"{test_id}: Đăng ký không thất bại như mong đợi!")
                    print(f"✅ {test_id} Passed: Đăng ký thất bại như mong đợi.")
                    test_case["Actual Result"] = "Register failed"
                    test_case["Result"] = "Passed"
            except AssertionError as e:
                print(f"❌ {test_id} Failed: {str(e)}")
                test_case["Actual Result"] = f"Kết quả không như mong đợi: {str(e)}"
                test_case["Result"] = "Failed"
            except Exception as e:
                print(f"❌ {test_id} Failed với lỗi không mong muốn: {str(e)}")
                test_case["Actual Result"] = f"Lỗi: {str(e)}"
                test_case["Result"] = "Failed"

    @classmethod
    def tearDownClass(cls):
        """Lưu kết quả test vào file Excel sau khi hoàn thành"""
        cls.data_manager.save_register_test_data(   
            "D:/nam3/KTPM2/Script-test-ecommerece/Result/test_register_result.xlsx"
        )


if __name__ == "__main__":
    unittest.main()