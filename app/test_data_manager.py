import pandas as pd

class TestDataManager:
    def __init__(self, input_file):
        """
        Khởi tạo TestDataManager với file đầu vào Excel.
        Args:
            input_file (str): Đường dẫn đến file dữ liệu Excel.
        """
        self.input_file = input_file
        self.app_test_cases = []
        self.web_test_cases = []
        # Định nghĩa tên cột thủ công
        self.column_names = ['Test Case ID', 
                             'Test Case Description', 
                             'Username', 'Password', 
                             'Platform',
                             'Expected Result',
                             'Actualy result',
                             'Result'
                            ]

    def read_app_test_data(self):
        """
        Đọc dữ liệu kiểm thử từ file Excel cho nền tảng App, không dùng header.
        Returns:
            list: Danh sách các test case cho App.
        """
        # Đọc file Excel mà không lấy header, gán tên cột thủ công
        df = pd.read_excel(self.input_file, engine='openpyxl', header=None, names=self.column_names, skiprows=1)
        # Lọc dữ liệu cho App
        app_data = df[df['Platform'] == 'APP']
        self.app_test_cases = app_data.to_dict(orient='records')
        return self.app_test_cases

    def read_web_test_data(self):
        """
        Đọc dữ liệu kiểm thử từ file Excel cho nền tảng Web, không dùng header.
        Returns:
            list: Danh sách các test case cho Web.
        """
        # Đọc file Excel mà không lấy header, gán tên cột thủ công
        df = pd.read_excel(self.input_file, engine='openpyxl', header=None, names=self.column_names, skiprows=1)
        # Lọc dữ liệu cho Web
        web_data = df[df['Platform'] == 'WEB']
        self.web_test_cases = web_data.to_dict(orient='records')
        return self.web_test_cases

    def save_app_test_data(self, output_file):
        """
        Lưu và cập nhật dữ liệu kiểm thử cho App vào file Excel.
        Giữ nguyên các test case của Web nếu file đã tồn tại.
        Args:
            output_file (str): Đường dẫn đến file Excel cần lưu.
        """
        try:
            # Đọc dữ liệu hiện có từ file Excel (với header)
            existing_df = pd.read_excel(output_file, engine='openpyxl')
        except FileNotFoundError:
            # Nếu file chưa tồn tại, tạo DataFrame rỗng với tên cột
            existing_df = pd.DataFrame(columns=self.column_names)

        # Lọc các test case không phải App (giữ nguyên Web)
        non_app_data = existing_df[existing_df['Platform'] != 'APP']
        
        # Chuyển test cases của App thành DataFrame
        new_app_df = pd.DataFrame(self.app_test_cases)
        
        # Kết hợp dữ liệu cũ (non-App) và dữ liệu mới (App)
        updated_df = pd.concat([non_app_data, new_app_df], ignore_index=True)
        
        # Lưu lại vào file Excel
        updated_df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Dữ liệu App đã được cập nhật vào {output_file}")

    def save_web_test_data(self, output_file):
        """
        Lưu và cập nhật dữ liệu kiểm thử cho Web vào file Excel.
        Giữ nguyên các test case của App nếu file đã tồn tại.
        Args:
            output_file (str): Đường dẫn đến file Excel cần lưu.
        """
        try:
            # Đọc dữ liệu hiện có từ file Excel (với header)
            existing_df = pd.read_excel(output_file, engine='openpyxl')
        except FileNotFoundError:
            # Nếu file chưa tồn tại, tạo DataFrame rỗng với tên cột
            existing_df = pd.DataFrame(columns=self.column_names)

        # Lọc các test case không phải Web (giữ nguyên App)
        non_web_data = existing_df[existing_df['Platform'] != 'WEB']
        
        # Chuyển test cases của Web thành DataFrame
        new_web_df = pd.DataFrame(self.web_test_cases)
        
        # Kết hợp dữ liệu cũ (non-Web) và dữ liệu mới (Web)
        updated_df = pd.concat([non_web_data, new_web_df], ignore_index=True)
        
        # Lưu lại vào file Excel
        updated_df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Dữ liệu Web đã được cập nhật vào {output_file}")

# # Ví dụ sử dụng
# if __name__ == "__main__":
#     # Khởi tạo đối tượng TestDataManager với file Excel đầu vào
#     test_manager = TestDataManager("test_data.xlsx")
    
#     # Đọc dữ liệu cho App
#     app_test_cases = test_manager.read_app_test_data()
#     print("Test cases cho App:")
#     for test in app_test_cases:
#         print(test)
    
#     # Đọc dữ liệu cho Web
#     web_test_cases = test_manager.read_web_test_data()
#     print("\nTest cases cho Web:")
#     for test in web_test_cases:
#         print(test)
    
#     # Cập nhật file Excel với dữ liệu App
#     output_file = "updated_test_data.xlsx"
#     test_manager.save_app_test_data(output_file)
    
#     # Cập nhật file Excel với dữ liệu Web
#     test_manager.save_web_test_data(output_file)