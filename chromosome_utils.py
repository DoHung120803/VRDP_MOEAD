import random

class Chromosome:
    def __init__(self, truck_routes, drone_assignment):
        self.truck_routes = truck_routes
        self.drone_assignment = drone_assignment

def initialize_chromosome(n_points, n_trucks, drone_serve):
    customers = list(range(1, n_points))  # Danh sách khách hàng (loại bỏ depot)
    random.shuffle(customers)
    
    # Tạo tuyến xe tải với chỉ 1 số 0 phân cách
    truck_routes = [0]  # Bắt đầu bằng depot
    segment_size = len(customers) // n_trucks
    remaining_customers = customers[:]  
    
    for i in range(n_trucks):
        if i < n_trucks - 1:
            segment = remaining_customers[:segment_size]
            remaining_customers = remaining_customers[segment_size:]
        else:
            segment = remaining_customers  # Đoạn cuối lấy hết khách hàng còn lại
        truck_routes.extend(segment)
        truck_routes.append(0)
    
    # Phân công drone khớp với drone_serve
    drone_assignment = drone_serve[:]  # Sao chép trực tiếp từ drone_serve
    
    return Chromosome(truck_routes, drone_assignment)