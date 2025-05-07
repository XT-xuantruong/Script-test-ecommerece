import random

# Danh sách các thành phần để tạo từ khóa
brands = ["Samsung", "iPhone"]
samsung_models = ["Galaxy S23", "Galaxy S24", "Galaxy Z Fold 5", "Galaxy Z Flip 5", "Galaxy A54", "Galaxy A34", "Galaxy Note 20", "Galaxy S22", "Galaxy S21", "Galaxy M34"]
iphone_models = ["15", "15 Pro", "14", "14 Pro", "13", "12", "SE", "11", "XR", "16"]
# Hàm tạo từ khóa ngẫu nhiên
def generate_keywords(num_keywords):
    result = []
    for _ in range(num_keywords):
        brand = random.choice(brands)
        if brand == "Samsung":
            model = random.choice(samsung_models)
        else:
            model = random.choice(iphone_models)
        
        keyword = f"{brand} {model}"
        
        result.append(keyword)
    # Loại bỏ trùng lặp (nếu có)
    result = list(set(result))
    
    return result

# Tạo 100 từ khóa
keywords = generate_keywords(100)

# In ra từ khóa
for i, keyword in enumerate(keywords, 1):
    print(f"{i}. {keyword}")

# Lưu vào file (tùy chọn)
with open("phone_keywords.csv", "w", encoding="utf-8") as f:
    for keyword in keywords:
        f.write(keyword + "\n")

print("\nĐã lưu 100 từ khóa vào file 'phone_keywords.csv'")