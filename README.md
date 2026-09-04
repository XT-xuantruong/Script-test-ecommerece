# E-commerce Web & App Automation Testing

Dự án thực hành **Software Testing** cho hệ thống thương mại điện tử trên **Web và Android App**, tập trung vào Functional Automation Testing, quản lý Test Case và Performance Testing.

## Testing Scope

Các chức năng chính được kiểm thử:

* Login
* Register
* Product Search
* Shopping Cart

### Web Testing

* Automation Testing với **Selenium WebDriver**
* Thực thi Test Case theo dữ liệu từ Excel
* So sánh Expected Result và Actual Result
* Ghi nhận kết quả Pass/Fail tự động

### Android App Testing

* Automation Testing với **Appium + UiAutomator2**
* Kiểm thử các luồng Login, Register, Search và Cart
* Quản lý và tái sử dụng Test Data giữa các test script

### Performance Testing

* Load Testing bằng **Apache JMeter**
* Các kịch bản:

  * 500 users
  * 1,000 users
  * 5,000 users
* Kiểm thử các API chính như Authentication, Product Search và Shopping Cart

## Kết quả chính

* Xây dựng automation test cho **4 nhóm chức năng chính** trên Web và Android App.
* Tự động hóa quá trình đọc Test Case, thực thi kiểm thử và ghi kết quả bằng **Python + Excel/Pandas**.
* Kết quả kiểm thử được lưu riêng cho:

  * Login
  * Register
  * Search
  * Shopping Cart
  * Performance Testing
* Xây dựng Load Test tăng dần đến **5,000 users** bằng JMeter.
* Thực hành quy trình từ **Test Case → Test Execution → Expected/Actual Result → Pass/Fail → Test Result**.

## Tech Stack

`Python` · `Selenium` · `Appium` · `UiAutomator2` · `JMeter` · `Pandas` · `Excel`

## Project Structure

```text
.
├── app/            # Android automation tests
├── web/            # Web automation tests
├── performance/    # JMeter load test scenarios
├── data/           # Test data
├── Result/         # Test execution results
└── Fake_data/      # Synthetic test data generators
```

## Run

Cài Python dependencies:

```bash
pip install -r app/requirements.txt
```

Chạy Web test:

```bash
python web/test-login.py
```

Chạy Android test sau khi khởi động Appium:

```bash
python app/test-login.py
```

Performance Test có thể chạy bằng JMeter với các file `.jmx` trong thư mục `performance/`.

## Purpose

Đây là **academic project** được thực hiện trong quá trình học và thực hành Software Testing, nhằm áp dụng kiến thức về Test Case, Automation Testing và Performance Testing vào hệ thống Web/App.
