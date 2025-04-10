def calculate_distance(x_coords, y_coords, i, j):
    return ((x_coords[i] - x_coords[j]) ** 2 + (y_coords[i] - y_coords[j]) ** 2) ** 0.5

def truck_travel_time(x_coords, y_coords, i, j, v_truck):
    return calculate_distance(x_coords, y_coords, i, j) / v_truck * 60

def drone_travel_time(x_coords, y_coords, i, j, v_drone):
    return calculate_distance(x_coords, y_coords, i, j) / v_drone * 60

def satisfaction_level(t, eet, tws, twe, elt):
    """Tính mức độ hài lòng S_i(t) dựa trên thời gian đến t."""
    if t < eet:
        return 0
    elif eet <= t < tws:
        return 1 - ((t - eet) / (tws - eet)) ** 5
    elif tws <= t < twe:
        return 1
    elif twe <= t < elt:
        return 1 - ((elt - t) / (elt - twe)) ** 5
    elif t >= elt:
        return 0
    return 0  # Trường hợp mặc định

WAER = 1.2603 
PGFER = 3.773 * (10**-4)
AER = 3.3333

def evaluate_objectives(chromosome, x_coords, y_coords, v_truck, v_drone, service_time, n_trucks, time_windows):
    truck_routes = chromosome.truck_routes
    drone_assignment = chromosome.drone_assignment
    
    # Tách các tuyến xe tải
    routes = []
    start = 0
    for i in range(1, len(truck_routes)):
        if truck_routes[i] == 0:
            routes.append(truck_routes[start:i + 1])
            start = i
    if not routes:
        routes.append(truck_routes)
    
    # Biến lưu kết quả
    truck_times = []
    total_truck_distance = 0
    total_drone_distance = 0
    arrival_times_all = {}  # Lưu thời gian đến từng khách hàng
    
    for route in routes:
        arrival_times = {route[0]: 0}
        current_time = 0
        i_idx = 0
        
        while i_idx < len(route) - 2:  # Đủ i, j, k
            i = route[i_idx]
            j = route[i_idx + 1]
            k = route[i_idx + 2]
            
            if drone_assignment[j] == 1:  # Dùng drone cho j
                truck_distance_ik = calculate_distance(x_coords, y_coords, i, k)
                total_truck_distance += truck_distance_ik
                truck_time_ik = truck_travel_time(x_coords, y_coords, i, k, v_truck) + (service_time[k] if k != 0 else 0)
                truck_arrival_k = arrival_times[i] + truck_time_ik
                
                t_ij = drone_travel_time(x_coords, y_coords, i, j, v_drone)
                t_jk = drone_travel_time(x_coords, y_coords, j, k, v_drone)
                drone_time = t_ij + service_time[j] + t_jk
                drone_arrival_k = arrival_times[i] + drone_time
                
                total_drone_distance += calculate_distance(x_coords, y_coords, i, j) + calculate_distance(x_coords, y_coords, j, k)
                
                current_time = max(truck_arrival_k, drone_arrival_k)
                arrival_times[j] = arrival_times[i] + t_ij  # Thời gian drone đến j
                arrival_times[k] = current_time
                arrival_times_all[j] = arrival_times[j]
                arrival_times_all[k] = arrival_times[k]
                i_idx += 2
            else:
                truck_distance_ij = calculate_distance(x_coords, y_coords, i, j)
                total_truck_distance += truck_distance_ij
                time = truck_travel_time(x_coords, y_coords, i, j, v_truck) + service_time[j]
                current_time += time
                arrival_times[j] = current_time
                arrival_times_all[j] = current_time
                i_idx += 1
        
        # Xử lý đoạn cuối
        if i_idx == len(route) - 2:  # Còn i, j
            i = route[i_idx]
            j = route[i_idx + 1]
            truck_distance_ij = calculate_distance(x_coords, y_coords, i, j)
            total_truck_distance += truck_distance_ij
            time = truck_travel_time(x_coords, y_coords, i, j, v_truck) + (service_time[j] if j != 0 else 0)
            current_time += time
            arrival_times[j] = current_time
            arrival_times_all[j] = current_time
            i_idx += 1
        
        if i_idx == len(route) - 1:
            pass
        
        truck_times.append(current_time)
    
    # Makespan
    makespan = max(truck_times)
    arrival_times_all.pop(0, None)  # Xóa depot
    
    # Tính mức độ hài lòng trung bình
    satisfaction_scores = []
    for customer in range(1, len(time_windows)):  # Bỏ depot (0)
        if customer in arrival_times_all:
            t = arrival_times_all[customer]
            eet, tws, twe, elt = time_windows[customer]
            s = satisfaction_level(t, eet, tws, twe, elt)
            satisfaction_scores.append(s)
    
    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
    carbon_emission = WAER * total_truck_distance + PGFER * AER * total_drone_distance 
    return makespan, carbon_emission, avg_satisfaction

# # Chạy thử
# class Chromosome:
#     def __init__(self, truck_routes, drone_assignment):
#         self.truck_routes = truck_routes
#         self.drone_assignment = drone_assignment

# # Dữ liệu ví dụ
# chromosome = Chromosome([0, 3, 4, 6, 0, 1, 7, 5, 0, 8, 2, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1])
# x_coords = [0, 1, 2, 3, 4, 5, 6, 7, 8]
# y_coords = [0, 0, 0, 0, 0, 0, 0, 0, 0]
# v_truck = 40
# v_drone = 80
# service_time = [0, 5, 5, 5, 5, 5, 5, 5, 5]
# n_trucks = 3
# # Time windows: [EET, TWS, TWE, ELT] cho mỗi khách hàng (0-8)
# time_windows = [
#     [0, 0, 0, 0],    # Depot
#     [0, 5, 10, 15],  # 1
#     [5, 10, 15, 20], # 2
#     [0, 5, 10, 15],  # 3
#     [5, 10, 15, 20], # 4
#     [10, 15, 20, 25],# 5
#     [5, 10, 15, 20], # 6
#     [10, 15, 20, 25],# 7
#     [5, 10, 15, 20]  # 8
# ]

# makespan, truck_distance, drone_distance, avg_satisfaction = evaluate_objectives(
#     chromosome, x_coords, y_coords, v_truck, v_drone, service_time, n_trucks, time_windows
# )
# print(f"Makespan: {makespan} phút")
# print(f"Tổng khoảng cách di chuyển của xe tải: {truck_distance} km")
# print(f"Tổng khoảng cách di chuyển của drone: {drone_distance} km")
# print(f"Mức độ hài lòng trung bình: {avg_satisfaction:.2f}")