import unittest
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from test_data_manager import TestDataManager

class TestLoginApp(unittest.TestCase):
    capabilities = dict(
        platformName='Android',
        automationName='uiautomator2',
        deviceName='ce0917192499191c027e',
        app='F:\Test\eshop.apk',
    )
    appium_server_url = 'http://127.0.0.1:4723/wd/hub'

    @classmethod
    def setUpClass(cls):
        """Khởi tạo TestDataManager và đọc dữ liệu kiểm thử"""
        cls.data_manager = TestDataManager("F:\Test\script-test\data\data_test.xlsx")
        cls.test_cases = cls.data_manager.read_app_test_data()

    def setUp(self) -> None:
        """Khởi động Appium và mở ứng dụng trước mỗi test"""
        self.driver = webdriver.Remote(self.appium_server_url, options=UiAutomator2Options().load_capabilities(self.capabilities))
        time.sleep(5)

    def tearDown(self) -> None:
        """Đóng ứng dụng sau mỗi test"""
        if self.driver:
            self.driver.quit()
            print("✅ Ứng dụng đã đóng.")

    def _login(self, username, password):
        """Hàm hỗ trợ để nhập thông tin đăng nhập và nhấn nút Login"""
        # Tìm trường Email bằng text="Email"
        email_field = self.driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="Email"]')
        email_field.clear()
        if username:
            email_field.send_keys(username)

        # Tìm trường Password bằng text="Mật khẩu"
        password_field = self.driver.find_element(AppiumBy.XPATH, '//android.widget.EditText[@text="Mật khẩu"]')
        password_field.clear()
        if password:
            password_field.send_keys(password)

        # Tìm nút Đăng Nhập bằng content-desc="Đăng Nhập"
        login_button = self.driver.find_element(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc="Đăng Nhập"]')
        login_button.click()
        time.sleep(8)

    def test_login_cases(self):
        """Chạy tất cả test case từ dữ liệu Excel"""
        for test_case in self.test_cases:
            test_id = test_case['Test Case ID']
            description = test_case['Test Case Description']
            username = test_case['Username']
            password = test_case['Password']

            print(f"\nĐang chạy: {test_id} - {description}")
            self._login(username, password)

            try:
                if test_id == '[Login-11]':  # Valid credentials
                    # Giả định màn hình chính có resource-id
                    home_screen = self.driver.find_element(AppiumBy.XPATH,'//android.widget.TextView[@text="Bán chạy"]')
                    self.assertTrue(home_screen.is_displayed(), f"{test_id}: Đăng nhập thành công nhưng không thấy màn hình chính!")
                    print(f"✅ {test_id} Passed: Đăng nhập thành công.")
                else:  # Các trường hợp thất bại
                    # Giả định thông báo lỗi là TextView với text chứa "Sai"
                    error_message = self.driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Sai")]')
                    self.assertTrue(error_message.is_displayed(), f"{test_id}: Không thấy thông báo lỗi!")
                    print(f"✅ {test_id} Passed: Đăng nhập thất bại như mong đợi.")
            except Exception as e:
                print(f"❌ {test_id} Failed: {str(e)}")
                self.fail(f"{test_id} failed with error: {str(e)}")

    @classmethod
    def tearDownClass(cls):
        """Lưu kết quả test vào file Excel sau khi hoàn thành"""
        cls.data_manager.save_app_test_data("F:\Test\script-test\Result\test_login_result.xlsx")

if __name__ == '__main__':
    unittest.main()