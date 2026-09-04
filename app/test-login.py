import unittest
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_data_manager import TestDataManager


class TestLoginApp(unittest.TestCase):
    # Khởi tạo các thuộc tính chung cho class
    capabilities = {
        "platformName": "Android",
        "automationName": "uiautomator2",
        "deviceName": "",
        "app": "D:/nam3/KTPM2/application-8bd28935-27e6-428e-9b9e-109d07ab30c4.apk",
    }
    appium_server_url = "http://127.0.0.1:4723/wd/hub"

    @classmethod
    def setUpClass(cls):
        """Khởi tạo TestDataManager và đọc dữ liệu kiểm thử"""
        cls.data_manager = TestDataManager("D:/nam3/KTPM2/Script-test-ecommerece/data/data_test2.xlsx")
        cls.test_cases = cls.data_manager.read_app_test_data()

    def setUp(self):
        """Khởi động Appium và mở ứng dụng trước mỗi test"""
        self.driver = webdriver.Remote(
            self.appium_server_url,
            options=UiAutomator2Options().load_capabilities(self.capabilities),
        )
        self.wait = WebDriverWait(self.driver, 15)

    def tearDown(self):
        """Đóng ứng dụng sau mỗi test"""
        if self.driver:
            self.driver.quit()
            print("✅ Ứng dụng đã đóng.")

    def _clear_field_if_not_empty(self, element):
        """Xóa trường nếu không trống"""
        current_text = element.get_attribute("text") or element.get_attribute("value")
        if current_text and current_text not in ["Email", "Password"]:
            element.clear()
            return True
        return False

    def _ensure_clean_login_screen(self):
        """Đảm bảo màn hình đăng nhập ở trạng thái sạch"""
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

            # Kiểm tra xem đã ở màn hình đăng nhập
            self.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Email")')
                )
            )
            print("✅ Màn hình đăng nhập đã sẵn sàng.")
        except Exception as e:
            print(f"⚠️ Không thể đảm bảo màn hình đăng nhập sạch: {e}")

    def _login(self, username, password):
        """Thực hiện đăng nhập với username và password"""
        try:
            # Đảm bảo màn hình đăng nhập sạch trước khi bắt đầu
            self._ensure_clean_login_screen()

            # Tìm và xử lý trường email
            email_input = self.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Email")')
                )
            )
            if username:
                self._clear_field_if_not_empty(email_input)
                email_input.send_keys(username)

            # Tìm và xử lý trường password
            password_input = self.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Password")')
                )
            )
            if password:
                self._clear_field_if_not_empty(password_input)
                password_input.send_keys(password)

            # Nhấn nút đăng nhập
            login_button = self.wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Login"))
            )
            login_button.click()

            # Kiểm tra kết quả đăng nhập
            try:
                # Trường hợp đăng nhập thành công
                self.wait.until(
                    EC.presence_of_element_located(
                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Bán chạy")')
                    )
                )
                print("✅ Đăng nhập thành công và vào được trang chính.")
                return True
            except:
                # Trường hợp đăng nhập thất bại
                try:
                    error_dialogs = [
                        (AppiumBy.XPATH, '//android.widget.TextView[@text="Error"]'),
                    ]
                    
                    for locator in error_dialogs:
                        try:
                            error_dialog = WebDriverWait(self.driver, 3).until(
                                EC.presence_of_element_located(locator)
                            )
                            buttons = [
                                (AppiumBy.XPATH, '//android.widget.Button[@text="OK"]'),
                            ]
                            
                            for button in buttons:
                                try:
                                    btn = self.driver.find_element(*button)
                                    btn.click()
                                    print("✅ Đã đóng thông báo lỗi.")
                                    time.sleep(2)
                                    break
                                except:
                                    continue
                            
                            # Xóa dữ liệu các trường
                            try:
                                self.wait.until(
                                    EC.presence_of_element_located(
                                        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Đăng Nhập")')
                                    )
                                )
                                email_input = self.wait.until(
                                    EC.element_to_be_clickable(
                                        (AppiumBy.XPATH, '//android.view.ViewGroup[@index="1"]/android.widget.EditText[@index="1"]')
                                    )
                                )
                                if self._clear_field_if_not_empty(email_input):
                                    print("✅ Đã xóa dữ liệu trường email.")
                                else:
                                    print("ℹ️ Trường email đã trống, không cần xóa.")
                                
                                password_input = self.wait.until(
                                    EC.element_to_be_clickable(
                                        (AppiumBy.XPATH, '//android.view.ViewGroup[@index="1"]/android.widget.EditText[@index="2"]')
                                    )
                                )
                                if self._clear_field_if_not_empty(password_input):
                                    print("✅ Đã xóa dữ liệu trường password.")
                                else:
                                    print("ℹ️ Trường password đã trống, không cần xóa.")
                            except Exception as clear_e:
                                print(f"⚠️ Không thể xóa dữ liệu các trường nhập: {clear_e}")
                                try:
                                    print("🔍 Trạng thái UI khi lỗi xóa trường:", self.driver.page_source)
                                except:
                                    print("⚠️ Không thể lấy trạng thái UI khi xóa trường.")
                            
                            return False
                        except:
                            continue
                    
                    try:
                        login_button = self.wait.until(
                            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Login"))
                        )
                        if login_button.is_displayed():
                            print("✅ Vẫn ở màn hình đăng nhập - đăng nhập thất bại.")
                            return False
                    except:
                        pass
                    
                    print("⚠️ Không tìm thấy thông báo lỗi hoặc nút OK.")
                    return False
                
                except Exception as inner_e:
                    print(f"⚠️ Không thể xác định trạng thái sau khi đăng nhập: {inner_e}")
                    return False

        except Exception as e:
            print(f"❌ Lỗi khi đăng nhập: {e}")
            try:
                print("🔍 Trạng thái UI khi lỗi:", self.driver.page_source)
            except:
                print("⚠️ Không thể lấy trạng thái UI.")
            return False

    def _reset_to_login_screen(self):
        """Quay lại màn hình đăng nhập bằng cách khởi động lại driver"""
        try:
            print("🔄 Đang khởi động lại driver để quay về màn hình đăng nhập...")
            if self.driver:
                self.driver.quit()
                print("✅ Driver đã đóng.")
            self.driver = webdriver.Remote(
                self.appium_server_url,
                options=UiAutomator2Options().load_capabilities(self.capabilities),
            )
            self.wait = WebDriverWait(self.driver, 15)
            time.sleep(3)
            email_input = self.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Email")')
                )
            )
            if email_input.is_displayed():
                print("✅ Đã quay lại màn hình đăng nhập bằng cách khởi động lại driver.")
            else:
                print("⚠️ Không thể xác nhận màn hình đăng nhập sau khi khởi động lại driver.")
        except Exception as e:
            print(f"⚠️ Lỗi khi khởi động lại driver: {e}")

    def test_login_cases(self):
        """Chạy tất cả test case từ dữ liệu Excel"""
        for test_case in self.test_cases:
            test_id = test_case["Test Case ID"]
            description = test_case["Test Case Description"]
            username = str(test_case["Username"]) if test_case["Username"] else ""
            password = str(test_case["Password"]) if test_case["Password"] else ""
            expected_result = test_case["Expected Result"]

            print(f"\nĐang chạy: {test_id} - {description}")
            print(f"ℹ️ Dữ liệu: Username='{username}', Password='{password}', Expected Result='{expected_result}'")
            
            login_result = self._login(username, password)
            
            try:
                if "success" in expected_result.lower():
                    self.assertTrue(login_result, f"{test_id}: Đăng nhập thất bại!")
                    print(f"✅ {test_id} Passed: Đăng nhập thành công.")
                    test_case["Actual Result"] = "Login Succesfully"
                    test_case["Result"] = "Passed"
                    self._reset_to_login_screen()
                else:
                    self.assertFalse(login_result, f"{test_id}: Đăng nhập không thất bại như mong đợi!")
                    print(f"✅ {test_id} Passed: Đăng nhập thất bại như mong đợi.")
                    test_case["Actual Result"] = "Login failed"
                    test_case["Result"] = "Passed"
            except AssertionError as e:
                print(f"❌ {test_id} Failed: {str(e)}")
                test_case["Actual Result"] = f"Kết quả không như mong đợi: {str(e)}"
                test_case["Result"] = "Failed"
                self._reset_to_login_screen()
            except Exception as e:
                print(f"❌ {test_id} Failed với lỗi không mong muốn: {str(e)}")
                test_case["Actual Result"] = f"Lỗi: {str(e)}"
                test_case["Result"] = "Failed"
                self._reset_to_login_screen()

    @classmethod
    def tearDownClass(cls):
        """Lưu kết quả test vào file Excel sau khi hoàn thành"""
        cls.data_manager.save_app_test_data("D:/nam3/KTPM2/Script-test-ecommerece/Result/test_login_result.xlsx")


if __name__ == "__main__":
    unittest.main()
