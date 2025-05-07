import unittest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from test_data_manager import TestDataManager
import time

class TestSearchApp(unittest.TestCase):
    """Kiểm thử chức năng tìm kiếm trên ứng dụng Android."""

    capabilities = {
        "platformName": "Android",
        "automationName": "uiautomator2",
        "deviceName": "ce0917192499191c027e",
        "app": "D:/application-2e2e75d8-a91c-49f4-9c02-84e45244343c.apk",
    }
    appium_server_url = "http://127.0.0.1:4723/wd/hub"

    @classmethod
    def setUpClass(cls):
        """Khởi tạo TestDataManager, đọc dữ liệu kiểm thử và đăng nhập."""
        cls.data_manager = TestDataManager("D:/nam3/KTPM2/Script-test-ecommerece/data/data_test2.xlsx")
        cls.test_cases = cls.data_manager.read_search_test_data()
        cls.driver = webdriver.Remote(
            cls.appium_server_url,
            options=UiAutomator2Options().load_capabilities(cls.capabilities),
        )
        cls.wait = WebDriverWait(cls.driver, 80)
        cls._login_initial()

    @classmethod
    def tearDownClass(cls):
        """Đóng ứng dụng và lưu kết quả test."""
        if cls.driver:
            cls.driver.quit()
            print("✅ Ứng dụng đã đóng.")
        try:
            cls.data_manager.save_search_test_data(
                "D:/nam3/KTPM2/Script-test-ecommerece/Result/test_search_result.xlsx"
            )
        except KeyError as e:
            print(f"⚠️ Lỗi khi lưu kết quả: {e}. Vui lòng kiểm tra cột 'Platform'.")

    @classmethod
    def _login_initial(cls):
        """Đăng nhập để vào màn hình Shop."""
        try:
            # Chờ màn hình đăng nhập
            email_input = cls.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Email")')
                )
            )
            email_input.clear()
            email_input.send_keys("testuser@example.com")

            password_input = cls.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Password")')
                )
            )
            password_input.clear()
            password_input.send_keys("Password123")

            # Nhấn nút đăng nhập
            login_button = cls.wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Login"))
            )
            login_button.click()

            # Chuyển đến màn hình Shop
            shop_button = cls.wait.until(
                EC.element_to_be_clickable(
                    (AppiumBy.XPATH, '//android.widget.TextView[@text="Shop"]')
                )
            )
            shop_button.click()

            # Xác nhận vào màn hình Shop
            cls.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Shop")')
                )
            )
            print("✅ Đã đăng nhập và vào trang Shop.")
        except Exception as e:
            print(f"❌ Lỗi khi đăng nhập: {e}")
            raise

    def _clear_search_input(self):
        """Xóa nội dung trong ô tìm kiếm."""
        try:
            search_input = self.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH, '//android.widget.EditText')
                )
            )
            try:
                search_input.clear()
            except:
                for _ in range(20):
                    search_input.send_keys(Keys.BACKSPACE)
            self.wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                )
            )
            print("✅ Đã xóa nội dung ô tìm kiếm.")
        except Exception as e:
            print(f"❌ Lỗi khi xóa nội dung ô tìm kiếm: {e}")
            raise

    def scroll_horizontal_to_category(self, category_text, max_scrolls=8):
        """Scroll ngang hàng category để tìm và trả về phần tử category mong muốn (Appium 2.x, hỗ trợ nhiều biến thể text)."""
        start_x = 1300  # gần phải (dựa trên bounds [49,530][1391,677])
        end_x = 100     # gần trái
        y = 600         # nằm giữa 530 và 677
        text_variants = [category_text, category_text.lower(), category_text.upper(), category_text.capitalize()]
        for scroll_idx in range(max_scrolls):
            # In ra tất cả text của các category hiện tại để debug
            categories = self.driver.find_elements("xpath", "//android.widget.HorizontalScrollView//android.widget.TextView")
            print(f"[Scroll {scroll_idx}] Category texts: {[c.text for c in categories]}")
            for variant in text_variants:
                try:
                    category = self.driver.find_element("xpath", f'//android.widget.TextView[@text="{variant}"]')
                    if category.is_displayed():
                        print(f"[Scroll {scroll_idx}] Found category with text: {variant}")
                        return category
                except:
                    pass
            # Sử dụng swipeGesture của Appium 2.x
            self.driver.execute_script(
                "mobile: swipeGesture",
                {
                    "left": end_x,
                    "top": y-50,
                    "width": start_x-end_x,
                    "height": 100,
                    "direction": "left",
                    "percent": 0.8
                }
            )
            time.sleep(0.5)  # Thêm delay nhỏ
        raise Exception(f"Không tìm thấy category '{category_text}' sau khi scroll")

    def test_search_cases(self):
        """Chạy tất cả test case từ sheet Search."""
        for test_case in self.test_cases:
            test_id = test_case["Test Case ID"]
            description = test_case["Test Case Description"]
            keywords = test_case["Key Words"]
            expected_result = test_case["Expected Result"]

            print(f"\nĐang chạy: {test_id} - {description}")
            print(f"ℹ️ Keywords='{keywords}', Expected Result='{expected_result}'")

            try:
                if test_id == "[Search-12]":
                    """Tìm kiếm sản phẩm hợp lệ (iPhone 13)."""
                    self._clear_search_input()
                    search_input = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                        )
                    )
                    search_input.send_keys("iPhone 13")
                    product = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "IPhone 13")]')
                        )
                    )
                    if product.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị sản phẩm 'iPhone 13'.")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không tìm thấy sản phẩm 'iPhone 13'")

                elif test_id == "[Search-13]":
                    """Tìm kiếm với từ khóa chỉ chứa số (13)."""
                    self._clear_search_input()
                    search_input = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                        )
                    )
                    search_input.send_keys("13")
                    try:
                        product = self.wait.until(
                            EC.presence_of_element_located(
                                (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "13")]')
                            )
                        )
                        if product.is_displayed():
                            print(f"✅ {test_id} Passed: Hiển thị sản phẩm chứa '13'.")
                            test_case["Actual Result"] = expected_result
                            test_case["Result"] = "Passed"
                        else:
                            raise Exception("Không tìm thấy sản phẩm chứa '13'")
                    except Exception as e:
                        print(f"❌ {test_id} Failed: {str(e)}")
                        test_case["Actual Result"] = f"Lỗi: {str(e)}"
                        test_case["Result"] = "Failed"
                        # Không raise exception để tránh tắt ứng dụng

                elif test_id == "[Search-14]":
                    """Tìm kiếm theo danh mục hợp lệ (iPhone)."""
                    category_button = self.scroll_horizontal_to_category("iphone")
                    category_button.click()
                    product = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "IPhone")]')
                        )
                    )
                    if product.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị sản phẩm trong danh mục 'iPhone'.")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không tìm thấy sản phẩm trong danh mục 'iPhone'")

                elif test_id == "[Search-15]":
                    """Tìm kiếm kết hợp danh mục và từ khóa (Galaxy S24, Samsung)."""
                    category_button = self.scroll_horizontal_to_category("samsung")
                    category_button.click()
                    self._clear_search_input()
                    search_input = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                        )
                    )
                    search_input.send_keys("Galaxy S24")
                    product = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Galaxy S24")]')
                        )
                    )
                    if product.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị sản phẩm 'Galaxy S24' trong danh mục 'Samsung'.")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không tìm thấy sản phẩm 'Galaxy S24' trong danh mục 'Samsung'")

                elif test_id == "[Search-16]":
                    """Tìm kiếm với từ khóa không tồn tại."""
                    self._clear_search_input()
                    search_input = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                        )
                    )
                    search_input.send_keys("nonexistentproduct")
                    message = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[@text="Không tìm thấy sản phẩm nào."]')
                        )
                    )
                    if message.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị 'Không tìm thấy sản phẩm nào.'")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không hiển thị 'Không tìm thấy sản phẩm nào.'")

                elif test_id == "[Search-17]":
                    """Tìm kiếm với từ khóa ngắn (1 ký tự: a)."""
                    self._clear_search_input()
                    search_input = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                        )
                    )
                    search_input.send_keys("a")
                    try:
                        product = self.wait.until(
                            EC.presence_of_element_located(
                                (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "a")]')
                            )
                        )
                        if product.is_displayed():
                            print(f"✅ {test_id} Passed: Hiển thị sản phẩm chứa 'a'.")
                            test_case["Actual Result"] = expected_result
                            test_case["Result"] = "Passed"
                    except:
                        message = self.wait.until(
                            EC.presence_of_element_located(
                                (AppiumBy.XPATH, '//android.widget.TextView[@text="Không tìm thấy sản phẩm nào."]')
                            )
                        )
                        if message.is_displayed():
                            print(f"✅ {test_id} Passed: Hiển thị 'Không tìm thấy sản phẩm nào.'")
                            test_case["Actual Result"] = expected_result
                            test_case["Result"] = "Passed"
                        else:
                            raise Exception("Không tìm thấy sản phẩm hoặc thông báo không tìm thấy")

                elif test_id == "[Search-18]":
                    """Tìm kiếm với từ khóa chứa khoảng trắng (i Phone 13)."""
                    self._clear_search_input()
                    search_input = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                        )
                    )
                    search_input.send_keys("i Phone 13")
                    message = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[@text="Không tìm thấy sản phẩm nào."]')
                        )
                    )
                    if message.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị 'Không tìm thấy sản phẩm nào.'")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không hiển thị 'Không tìm thấy sản phẩm nào.'")

                elif test_id == "[Search-19]":
                    """Tìm kiếm với ký tự đặc biệt (@#$%)."""
                    self._clear_search_input()
                    search_input = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.EditText[@text="Tìm kiếm..."]')
                        )
                    )
                    search_input.send_keys("@#$%")
                    message = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[@text="Không tìm thấy sản phẩm nào."]')
                        )
                    )
                    if message.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị 'Không tìm thấy sản phẩm nào.'")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không hiển thị 'Không tìm thấy sản phẩm nào.'")

                elif test_id == "[Search-20]":
                    """Tìm kiếm danh mục không có sản phẩm."""
                    category_button = self.scroll_horizontal_to_category("vivo")
                    category_button.click()
                    message = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[@text="Không tìm thấy sản phẩm nào."]')
                        )
                    )
                    if message.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị 'Không tìm thấy sản phẩm nào.'")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không hiển thị 'Không tìm thấy sản phẩm nào.'")

                elif test_id == "[Search-21]":
                    """Tìm kiếm với chuyển đổi danh mục nhanh."""
                    category_button = self.scroll_horizontal_to_category("samsung")
                    category_button.click()
                    product = self.wait.until(
                        EC.presence_of_element_located(
                            (AppiumBy.XPATH, '//android.widget.TextView[contains(@text, "Samsung")]')
                        )
                    )
                    if product.is_displayed():
                        print(f"✅ {test_id} Passed: Hiển thị sản phẩm trong danh mục 'Samsung'.")
                        test_case["Actual Result"] = expected_result
                        test_case["Result"] = "Passed"
                    else:
                        raise Exception("Không tìm thấy sản phẩm trong danh mục 'Samsung'")

                else:
                    print(f"⚠️ {test_id} Skipped: Chưa triển khai chi tiết.")
                    test_case["Actual Result"] = "Test case chưa được triển khai"
                    test_case["Result"] = "Skipped"

            except Exception as e:
                print(f"❌ {test_id} Failed: {str(e)}")
                test_case["Actual Result"] = f"Lỗi: {str(e)}"
                test_case["Result"] = "Failed"
            finally:
                # Xóa ô tìm kiếm sau mỗi test case
                try:
                    self._clear_search_input()
                except Exception as e:
                    print(f"⚠️ Lỗi khi xóa ô tìm kiếm sau {test_id}: {e}")

if __name__ == "__main__":
    unittest.main()