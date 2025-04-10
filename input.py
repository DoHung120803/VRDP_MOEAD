import pandas as pd

# Đọc dữ liệu từ file Excel
# file_path = "C://Users//Computer//AppData//Local//Temp//Rar$DIa0.358//h100r202.csv"  # Thay bằng đường dẫn file thực tế
file_path = "C://Users//hungdm129//Documents//Zalo Received Files//Data_VRP_Drone//h100r202.csv"  # Thay bằng đường dẫn file thực tế
df = pd.read_csv(file_path)

# Lưu từng cột vào danh sách riêng biệt
x_coords = df["x"].tolist()  # Danh sách tọa độ x
y_coords = df["y"].tolist()  # Danh sách tọa độ y
demands = df["demand"].tolist()  # Nhu cầu hàng hóa
eet = df["eet"].tolist()  # Earliest End Time
open_time = df["open"].tolist()  # Giờ mở cửa
close_time = df["close"].tolist()  # Giờ đóng cửa
elt = df["elt"].tolist()  # Earliest Latest Time
service_time = df["servicetime"].tolist()  # Thời gian phục vụ
drone_serve = df["drone_serve"].tolist()  # Cờ có thể dùng drone

time_windows = [list(item) for item in zip(eet, open_time, close_time, elt)]
