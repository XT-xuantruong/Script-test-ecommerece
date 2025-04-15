import pandas as pd
import numpy as np


class TestDataManager:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.app_test_cases = []
        self.web_test_cases = []
        self.register_test_cases = []
        self.login_column_names = [
            "Test Case ID",
            "Test Case Description",
            "Username",
            "Password",
            "Platform",
            "Expected Result",
            "Actual Result",
            "Result",
        ]
        self.register_column_names = [
            "Test Case ID",
            "Test Case Description",
            "Username",
            "Email",
            "Phone",
            "Address",
            "Password",
            "Confirm password",
            "Platform",
            "Expected Result",
            "Result",
            "Actual Result",
        ]

    def read_app_test_data(self) -> list:
        df = pd.read_excel(
            self.input_file,
            sheet_name="Login",
            engine="openpyxl",
        )
        df.columns = [col.strip() for col in df.columns]
        missing_cols = [col for col in self.login_column_names if col not in df.columns]
        for col in missing_cols:
            df[col] = ""
        df = df[self.login_column_names]
        df = df.replace({np.nan: ""})
        app_data = df[df["Platform"] == "APP"]
        self.app_test_cases = app_data.to_dict(orient="records")
        print(f"🔍 Đọc {len(self.app_test_cases)} test case cho App (login).")
        return self.app_test_cases

    def read_web_test_data(self) -> list:
        df = pd.read_excel(
            self.input_file,
            sheet_name="Login",
            engine="openpyxl",
        )
        df.columns = [col.strip() for col in df.columns]
        missing_cols = [col for col in self.login_column_names if col not in df.columns]
        for col in missing_cols:
            df[col] = ""
        df = df[self.login_column_names]
        df = df.replace({np.nan: ""})
        web_data = df[df["Platform"] == "WEB"]
        self.web_test_cases = web_data.to_dict(orient="records")
        print(f"🔍 Đọc {len(self.web_test_cases)} test case cho Web (login).")
        return self.web_test_cases

    def read_register_test_data(self) -> list:
        df = pd.read_excel(
            self.input_file,
            sheet_name="Register",
            engine="openpyxl",
        )
        print(f"🔍 Header của file Excel: {df.columns.tolist()}")

        df.columns = [col.strip() for col in df.columns]

        if "Password" in df.columns and "Password.1" in df.columns:
            column_mapping = {}
            first_password_found = False
            for col in df.columns:
                if col == "Password" and not first_password_found:
                    column_mapping[col] = "Email"
                    first_password_found = True
                elif col == "Password.1":
                    column_mapping[col] = "Password"
                else:
                    column_mapping[col] = col
            df.rename(columns=column_mapping, inplace=True)

        missing_cols = [col for col in self.register_column_names if col not in df.columns]
        for col in missing_cols:
            df[col] = ""

        df = df[self.register_column_names]
        df = df.replace({np.nan: ""})

        register_data = df[
            df["Test Case ID"].astype(str).str.startswith("[Register-") &
            (df["Test Case ID"] != "")
        ]

        print(f"🔍 Tổng số dòng dữ liệu đọc được: {len(df)}")
        print(f"🔍 Số test case đăng ký sau khi lọc: {len(register_data)}")
        print(f"🔍 Test case ID: {register_data['Test Case ID'].tolist()}")
        print(f"🔍 Dữ liệu mẫu: {register_data.iloc[0].to_dict() if not register_data.empty else 'Không có dữ liệu'}")

        self.register_test_cases = register_data.to_dict(orient="records")
        return self.register_test_cases

    def save_app_test_data(self, output_file: str):
        try:
            existing_df = pd.read_excel(output_file, engine="openpyxl")
            existing_df = existing_df[[col for col in existing_df.columns if col in self.login_column_names]]
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=self.login_column_names)

        non_app_data = existing_df[existing_df["Platform"] != "APP"]
        new_app_df = pd.DataFrame(self.app_test_cases)
        updated_df = pd.concat([non_app_data, new_app_df], ignore_index=True)
        updated_df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"✅ Dữ liệu App (login) đã được lưu vào {output_file}")

    def save_web_test_data(self, output_file: str):
        try:
            existing_df = pd.read_excel(output_file, engine="openpyxl")
            existing_df = existing_df[[col for col in existing_df.columns if col in self.login_column_names]]
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=self.login_column_names)

        non_web_data = existing_df[existing_df["Platform"] != "WEB"]
        new_web_df = pd.DataFrame(self.web_test_cases)
        updated_df = pd.concat([non_web_data, new_web_df], ignore_index=True)
        updated_df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"✅ Dữ liệu Web (login) đã được lưu vào {output_file}")

    def save_register_test_data(self, output_file: str):
        new_register_df = pd.DataFrame(self.register_test_cases)
        print(f"🔍 Số test case được lưu: {len(new_register_df)}")
        print(f"🔍 Test case ID được lưu: {new_register_df['Test Case ID'].tolist()}")
        new_register_df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"✅ Dữ liệu đăng ký đã được lưu vào {output_file}")