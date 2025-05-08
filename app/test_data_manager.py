import pandas as pd
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

class TestDataManager:
    """Quản lý dữ liệu kiểm thử từ file Excel cho kịch bản đăng nhập, đăng ký, giỏ hàng và tìm kiếm."""

    LOGIN_COLUMNS = [
        "Test Case ID", "Test Case Description", "Username", "Password",
        "Platform", "Expected Result", "Actual Result", "Result"
    ]
    REGISTER_COLUMNS = [
        "Test Case ID", "Test Case Description", "Username", "Email", "Phone",
        "Address", "Password", "Confirm password", "Platform", "Expected Result",
        "Result", "Actual Result"
    ]
    CART_COLUMNS = [
        "Test Case ID", "Test Case Description", "Platform",
        "Expected Result", "Actual Result", "Result"
    ]
    SEARCH_COLUMNS = [
        "Test Case ID", "Test Case Description", "Key Words", "Platform",
        "Expected Result", "Result", "Actual Result"
    ]
    LOGIN_SHEET = "Login"
    REGISTER_SHEET = "Register"
    CART_SHEET = "Cart"
    SEARCH_SHEET = "Search"

    # Define icon characters (dựa trên script gốc, có thể cần điều chỉnh)
    ICON_PLUS = ""  # Ví dụ: tăng số lượng
    ICON_MINUS = ""  # Ví dụ: giảm số lượng
    ICON_DELETE = ""  # Ví dụ: xóa sản phẩm
    ICON_BACK_ARROW = ""  # Từ script gốc

    def __init__(self, input_file: str):
        """Khởi tạo với đường dẫn file Excel đầu vào.

        Args:
            input_file: Đường dẫn đến file Excel chứa dữ liệu kiểm thử.
        """
        self.input_file = Path(input_file)
        self.app_test_cases: List[Dict[str, Any]] = []
        self.web_test_cases: List[Dict[str, Any]] = []
        self.register_test_cases: List[Dict[str, Any]] = []
        self.cart_test_cases: List[Dict[str, Any]] = []
        self.search_test_cases: List[Dict[str, Any]] = []

    def _read_excel_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Đọc dữ liệu từ sheet Excel và chuẩn hóa.

        Args:
            sheet_name: Tên sheet cần đọc.

        Returns:
            DataFrame đã chuẩn hóa.

        Raises:
            FileNotFoundError: Nếu file Excel không tồn tại.
            ValueError: Nếu sheet không tồn tại hoặc định dạng sai.
        """
        try:
            df = pd.read_excel(self.input_file, sheet_name=sheet_name, engine="openpyxl")
            df.columns = [str(col).strip() for col in df.columns]  # Đảm bảo tên cột là chuỗi
            return df.replace({np.nan: ""})
        except FileNotFoundError:
            raise FileNotFoundError(f"Không tìm thấy file: {self.input_file}")
        except ValueError as e:
            raise ValueError(f"Lỗi khi đọc sheet '{sheet_name}': {e}")

    def _ensure_columns(self, df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
        """Đảm bảo DataFrame có tất cả cột cần thiết, thêm cột trống nếu thiếu.

        Args:
            df: DataFrame cần xử lý.
            required_columns: Danh sách cột mong đợi.

        Returns:
            DataFrame với các cột được chuẩn hóa.
        """
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        return df[required_columns]  # Trả về chỉ các cột cần thiết theo thứ tự

    def _convert_float_to_int(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Chuyển đổi giá trị float thành integer trong các cột chỉ định nếu chúng là số nguyên.

        Args:
            df: DataFrame cần xử lý.
            columns: Danh sách cột cần chuyển đổi (ví dụ: ['Test Case ID']).

        Returns:
            DataFrame với các giá trị float đã được chuyển thành integer.
        """
        for col in columns:
            if col in df.columns:
                try:
                    df[col] = df[col].apply(
                        lambda x: int(x) if pd.notna(x) and isinstance(x, (float, int)) and float(x).is_integer() else x
                    )
                except (ValueError, TypeError):
                    pass  # Bỏ qua nếu cột không thể chuyển đổi
        return df

    def _save_test_data(self, output_file: str, test_cases: List[Dict[str, Any]], columns: List[str], platform_filter: str = None) -> None:
        """Lưu dữ liệu kiểm thử vào file Excel.

        Args:
            output_file: Đường dẫn file Excel đầu ra.
            test_cases: Danh sách test case cần lưu.
            columns: Danh sách cột cho DataFrame.
            platform_filter: Bộ lọc theo nền tảng (APP/WEB) nếu có.

        Raises:
            PermissionError: Nếu không có quyền ghi file.
        """
        output_path = Path(output_file)
        current_run_df = pd.DataFrame(test_cases)
        current_run_df = self._ensure_columns(current_run_df, columns)

        if output_path.exists():
            try:
                existing_df = pd.read_excel(output_path, engine="openpyxl")
                existing_df = self._ensure_columns(existing_df, columns)
            except Exception as e:
                print(f"⚠️ Lỗi khi đọc file Excel '{output_path}': {e}. Sẽ tạo file mới hoặc ghi đè.")
                existing_df = pd.DataFrame(columns=columns)
        else:
            existing_df = pd.DataFrame(columns=columns)

        if platform_filter:
            if "Platform" in existing_df.columns:
                existing_df_filtered = existing_df[existing_df["Platform"].astype(str).str.upper() != str(platform_filter).upper()]
            else:
                existing_df_filtered = existing_df.copy()
            updated_df = pd.concat([existing_df_filtered, current_run_df], ignore_index=True)
        else:
            updated_df = current_run_df

        updated_df = updated_df.reindex(columns=columns, fill_value="")

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            updated_df.to_excel(output_path, index=False, engine="openpyxl")
            platform_info = f"({platform_filter})" if platform_filter else "(all)"
            print(f"✅ Dữ liệu {platform_info} đã được lưu vào {output_file}")
        except PermissionError:
            print(f"❌ Lỗi Quyền Truy Cập: Không thể ghi vào file: {output_file}. File có thể đang mở hoặc bạn không có quyền ghi.")
        except Exception as e:
            print(f"❌ Lỗi không xác định khi lưu dữ liệu: {e}")

    def read_app_test_data(self) -> List[Dict[str, Any]]:
        """Đọc dữ liệu kiểm thử đăng nhập cho ứng dụng từ sheet 'Login'."""
        df = self._read_excel_sheet(self.LOGIN_SHEET)
        df = self._ensure_columns(df, self.LOGIN_COLUMNS)
        df = self._convert_float_to_int(df, ["Test Case ID"])
        self.app_test_cases = df[df["Platform"].astype(str).str.upper() == "APP"].to_dict(orient="records")
        print(f"🔍 Đọc {len(self.app_test_cases)} test case cho App (login).")
        return self.app_test_cases

    def read_web_test_data(self) -> List[Dict[str, Any]]:
        """Đọc dữ liệu kiểm thử đăng nhập cho web từ sheet 'Login'."""
        df = self._read_excel_sheet(self.LOGIN_SHEET)
        df = self._ensure_columns(df, self.LOGIN_COLUMNS)
        df = self._convert_float_to_int(df, ["Test Case ID"])
        self.web_test_cases = df[df["Platform"].astype(str).str.upper() == "WEB"].to_dict(orient="records")
        print(f"🔍 Đọc {len(self.web_test_cases)} test case cho Web (login).")
        return self.web_test_cases

    def read_register_test_data(self) -> List[Dict[str, Any]]:
        """Đọc dữ liệu kiểm thử đăng ký từ sheet 'Register'."""
        df = self._read_excel_sheet(self.REGISTER_SHEET)
        df = self._ensure_columns(df, self.REGISTER_COLUMNS)
        df = self._convert_float_to_int(df, ["Phone", "Test Case ID"])
        register_data = df[
            df["Test Case ID"].astype(str).str.startswith("[Register-") & (df["Test Case ID"] != "")
        ]
        self.register_test_cases = register_data.to_dict(orient="records")
        print(f"🔍 Đọc {len(self.register_test_cases)} test case cho Register.")
        return self.register_test_cases

    def read_cart_test_data(self) -> List[Dict[str, Any]]:
        """Đọc dữ liệu kiểm thử giỏ hàng từ sheet 'Cart'."""
        df = self._read_excel_sheet(self.CART_SHEET)
        df = self._ensure_columns(df, self.CART_COLUMNS)
        df = self._convert_float_to_int(df, ["Test Case ID"])
        self.cart_test_cases = df[df["Platform"].astype(str).str.upper() == "APP"].to_dict(orient="records")
        print(f"🔍 Đọc {len(self.cart_test_cases)} test case cho App (cart).")
        return self.cart_test_cases

    def read_search_test_data(self) -> List[Dict[str, Any]]:
        """Đọc dữ liệu kiểm thử tìm kiếm từ sheet 'Search'."""
        df = self._read_excel_sheet(self.SEARCH_SHEET)
        df = self._ensure_columns(df, self.SEARCH_COLUMNS)
        df = self._convert_float_to_int(df, ["Test Case ID"])
        self.search_test_cases = df[df["Platform"].astype(str).str.upper() == "APP"].to_dict(orient="records")
        print(f"🔍 Đọc {len(self.search_test_cases)} test case cho Search.")
        return self.search_test_cases

    def save_app_test_data(self, output_file: str) -> None:
        """Lưu dữ liệu kiểm thử đăng nhập ứng dụng."""
        self._save_test_data(output_file, self.app_test_cases, self.LOGIN_COLUMNS, platform_filter="APP")

    def save_web_test_data(self, output_file: str) -> None:
        """Lưu dữ liệu kiểm thử đăng nhập web."""
        self._save_test_data(output_file, self.web_test_cases, self.LOGIN_COLUMNS, platform_filter="WEB")

    def save_register_test_data(self, output_file: str) -> None:
        """Lưu dữ liệu kiểm thử đăng ký."""
        self._save_test_data(output_file, self.register_test_cases, self.REGISTER_COLUMNS, platform_filter=None)

    def save_cart_test_data(self, output_file: str) -> None:
        """Lưu dữ liệu kiểm thử giỏ hàng."""
        self._save_test_data(output_file, self.cart_test_cases, self.CART_COLUMNS, platform_filter="APP")

    def save_search_test_data(self, output_file: str) -> None:
        """Lưu dữ liệu kiểm thử tìm kiếm."""
        self._save_test_data(output_file, self.search_test_cases, self.SEARCH_COLUMNS, platform_filter="APP")

if __name__ == '__main__':
    # Ví dụ sử dụng (tùy chọn, để kiểm tra TestDataManager độc lập)
    input_excel_path = "D:/nam3/KTPM2/Script-test-ecommerece/data/data_test2.xlsx"
    output_excel_path_login = "D:/nam3/KTPM2/Script-test-ecommerece/Result/test_login_result_dm.xlsx"
    output_excel_path_register = "D:/nam3/KTPM2/Script-test-ecommerece/Result/test_register_result_dm.xlsx"
    output_excel_path_cart = "D:/nam3/KTPM2/Script-test-ecommerece/Result/test_cart_result_dm.xlsx"
    output_excel_path_search = "D:/nam3/KTPM2/Script-test-ecommerece/Result/test_search_result_dm.xlsx"

    try:
        # Tạo file Excel giả lập nếu không tồn tại
        Path(input_excel_path).parent.mkdir(parents=True, exist_ok=True)
        if not Path(input_excel_path).exists():
            print(f"Tạo file đầu vào giả lập: {input_excel_path}")
            dummy_login_data = {
                "Test Case ID": ["[Login-App-01]", "[Login-Web-01]"],
                "Test Case Description": ["Valid App Login", "Valid Web Login"],
                "Username": ["appuser", "webuser"],
                "Password": ["pass", "pass"],
                "Platform": ["APP", "WEB"],
                "Expected Result": ["Login success", "Login success"],
                "Actual Result": ["", ""],
                "Result": ["", ""]
            }
            dummy_register_data = {
                "Test Case ID": ["[Register-01]"],
                "Test Case Description": ["Valid Registration"],
                "Username": ["newuser"], "Email": ["new@example.com"], "Phone": ["1234567890"],
                "Address": ["123 Main St"], "Password": ["newpass"], "Confirm password": ["newpass"],
                "Platform": ["APP"], "Expected Result": ["Register success"],
                "Result": [""], "Actual Result": [""]
            }
            dummy_cart_data = {
                "Test Case ID": ["[Cart-11]"],
                "Test Case Description": ["Check empty cart"],
                "Platform": ["APP"],
                "Expected Result": ["Empty cart message"],
                "Actual Result": [""],
                "Result": [""]
            }
            dummy_search_data = {
                "Test Case ID": ["[Search-12]"],
                "Test Case Description": ["Search for a valid product"],
                "Key Words": ["iPhone 13"],
                "Platform": ["APP"],
                "Expected Result": ["Displays a list of products related to 'iPhone 13'"],
                "Result": [""],
                "Actual Result": [""]
            }
            with pd.ExcelWriter(input_excel_path, engine='openpyxl') as writer:
                pd.DataFrame(dummy_login_data).to_excel(writer, sheet_name=TestDataManager.LOGIN_SHEET, index=False)
                pd.DataFrame(dummy_register_data).to_excel(writer, sheet_name=TestDataManager.REGISTER_SHEET, index=False)
                pd.DataFrame(dummy_cart_data).to_excel(writer, sheet_name=TestDataManager.CART_SHEET, index=False)
                pd.DataFrame(dummy_search_data).to_excel(writer, sheet_name=TestDataManager.SEARCH_SHEET, index=False)

        data_manager = TestDataManager(input_excel_path)

        # Test Login data
        app_login_cases = data_manager.read_app_test_data()
        if app_login_cases:
            app_login_cases[0]["Actual Result"] = "Login success"
            app_login_cases[0]["Result"] = "Passed"
        data_manager.save_app_test_data(output_excel_path_login)

        web_login_cases = data_manager.read_web_test_data()
        if web_login_cases:
            web_login_cases[0]["Actual Result"] = "Login success"
            web_login_cases[0]["Result"] = "Passed"
        data_manager.save_web_test_data(output_excel_path_login)

        # Test Register data
        register_cases = data_manager.read_register_test_data()
        if register_cases:
            register_cases[0]["Actual Result"] = "Registration successful"
            register_cases[0]["Result"] = "Passed"
        data_manager.save_register_test_data(output_excel_path_register)

        # Test Cart data
        cart_cases = data_manager.read_cart_test_data()
        if cart_cases:
            cart_cases[0]["Actual Result"] = "Empty cart message shown"
            cart_cases[0]["Result"] = "Passed"
        data_manager.save_cart_test_data(output_excel_path_cart)

        # Test Search data
        search_cases = data_manager.read_search_test_data()
        if search_cases:
            search_cases[0]["Actual Result"] = "Displayed products related to iPhone 13"
            search_cases[0]["Result"] = "Passed"
        data_manager.save_search_test_data(output_excel_path_search)

        print("\nTestDataManager example usage complete.")
        print(f"Login results saved to: {output_excel_path_login}")
        print(f"Register results saved to: {output_excel_path_register}")
        print(f"Cart results saved to: {output_excel_path_cart}")
        print(f"Search results saved to: {output_excel_path_search}")

    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the input Excel file exists or paths are correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")  