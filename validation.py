ERROR_TYPES = {
    0: "VALID",
    1: "NO_START_END_ZERO",
    2: "INVALID_CUSTOMERS",
    3: "WRONG_TRUCK_COUNT",
    4: "CONSECUTIVE_ZERO",
    5: "EXCEED_CAPACITY",
    6: "SINGLE_DRONE_CUSTOMER"
}

def is_valid_chromosome(chromosome, n_points, n_trucks, demands, Q=1000):
    truck_routes = chromosome.truck_routes
    drone_assignment = chromosome.drone_assignment
    
    # Kiểm tra luôn có 0 ở đầu và cuối
    if truck_routes[0] != 0 or truck_routes[-1] != 0:
        print("Lỗi: truck_routes không bắt đầu hoặc kết thúc bằng 0")
        return False, 1
    
    # Ràng buộc (4): Mỗi khách hàng được phục vụ đúng một lần
    customers = [x for x in truck_routes if x != 0]
    expected_customers = set(range(1, n_points))
    if set(customers) != expected_customers:
        missing = expected_customers - set(customers)
        duplicates = [x for x in customers if customers.count(x) > 1]
        print(f"Lỗi (4): Khách hàng không hợp lệ. Thiếu: {missing}, Trùng: {duplicates}")
        return False, 2
    
    # Ràng buộc (5) và (6): Số đoạn bằng n_trucks
    zero_count = truck_routes.count(0)
    if zero_count != n_trucks + 1:  # n_trucks đoạn + 1 vì có 0 đầu và cuối
        print(f"Lỗi (5)/(6): Có xe tải không được sử dụng hoặc sử dụng nhiều lần (Số 0 ({zero_count}) không khớp với n_trucks + 1 ({n_trucks + 1}))")
        return False, 3
    
    # Ràng buộc (7): Không có hai 0 liên tiếp (đoạn rỗng)
    for i in range(len(truck_routes) - 1):
        if truck_routes[i] == 0 and truck_routes[i + 1] == 0:
            print("Lỗi (7): Có xe tải xuất phát từ kho và đi về kho mà không phục vụ hành khách nào (Có hai số 0 liên tiếp trong NST)")
            return False, 4
    
    # Ràng buộc (11): Tổng nhu cầu mỗi xe tải không vượt quá Q
    start = 0
    for i in range(1, len(truck_routes)):
        if truck_routes[i] == 0:
            segment = truck_routes[start:i]
            total_demand = sum(demands[j] for j in segment if j != 0)
            if total_demand > Q:
                print(f"Lỗi (11): Demand vượt quá yêu cầu (Tổng nhu cầu ({total_demand}) vượt quá Q ({Q}) ở đoạn {segment})")
                return False, 5
            start = i

    # Kiểm tra mới: Đoạn chỉ có 1 khách hàng và khách hàng đó được drone phục vụ
    start = 0
    for i in range(1, len(truck_routes)):
        if truck_routes[i] == 0:
            segment = truck_routes[start:i]
            if len(segment) == 2:  # Đoạn dạng [0, x, 0]
                customer = segment[1]
                if drone_assignment[customer] == 1:
                    print(f"Lỗi: Đoạn {segment} chỉ có 1 khách hàng {customer} và được drone phục vụ, không thể tạo i và k hợp lệ")
                    return False, 6
            start = i
    
    return True, 0