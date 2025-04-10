from validation import is_valid_chromosome, ERROR_TYPES

def local_search_repair(chromosome, n_points, n_trucks, demands, Q=1000):
    truck_routes = list(chromosome.truck_routes)
    drone_assignment = list(chromosome.drone_assignment)
    
    valid, error_type = is_valid_chromosome(chromosome, n_points, n_trucks, demands, Q)
    while not valid:
        print(f"Đang sửa lỗi: {ERROR_TYPES[error_type]}")
        
        if error_type == 1:  # NO_START_END_ZERO
            if truck_routes[0] != 0:
                truck_routes.insert(0, 0)
            if truck_routes[-1] != 0:
                truck_routes.append(0)
        
        elif error_type == 2:  # INVALID_CUSTOMERS
            customers = [x for x in truck_routes if x != 0]
            missing = set(range(1, n_points)) - set(customers)
            duplicates = [x for x in customers if customers.count(x) > 1]
            for dup in set(duplicates):
                idx = truck_routes.index(dup)
                if missing:
                    truck_routes[idx] = missing.pop()
                else:
                    truck_routes.pop(idx)
            for m in missing:
                truck_routes.insert(-1, m)
        
        elif error_type == 3:  # WRONG_TRUCK_COUNT
            zero_count = truck_routes.count(0)
            if zero_count < n_trucks + 1:
                # Thêm số 0 vào giữa các khách hàng để tạo đoạn mới
                customers_per_truck = (n_points - 1) // n_trucks
                new_routes = [0]
                customer_idx = 0
                customers = [x for x in truck_routes if x != 0]
                for _ in range(n_trucks - 1):
                    for _ in range(customers_per_truck):
                        if customer_idx < len(customers):
                            new_routes.append(customers[customer_idx])
                            customer_idx += 1
                    new_routes.append(0)
                while customer_idx < len(customers):
                    new_routes.append(customers[customer_idx])
                    customer_idx += 1
                new_routes.append(0)
                truck_routes = new_routes
            elif zero_count > n_trucks + 1:
                # Xóa số 0 thừa, giữ đúng n_trucks + 1 số 0
                zero_positions = [i for i, x in enumerate(truck_routes) if x == 0]
                excess_zeros = zero_count - (n_trucks + 1)
                # Xóa số 0 từ các vị trí không phải đầu hoặc cuối
                for _ in range(excess_zeros):
                    for i in zero_positions[1:-1]:  # Bỏ vị trí đầu và cuối
                        if i in zero_positions:  # Kiểm tra i vẫn còn trong danh sách
                            truck_routes.pop(i)
                            zero_positions = [j for j, x in enumerate(truck_routes) if x == 0]
                            break
        
        elif error_type == 4:  # CONSECUTIVE_ZERO
            for i in range(len(truck_routes) - 1):
                if truck_routes[i] == 0 and truck_routes[i + 1] == 0:
                    truck_routes.pop(i)
                    break
        
        elif error_type == 5:  # EXCEED_CAPACITY
            start = 0
            for i in range(1, len(truck_routes)):
                if truck_routes[i] == 0:
                    segment = truck_routes[start:i]
                    total_demand = sum(demands[j] for j in segment if j != 0)
                    if total_demand > Q:
                        excess = total_demand - Q
                        for j in segment[::-1]:
                            if j != 0 and demands[j] <= excess:
                                truck_routes.remove(j)
                                truck_routes.insert(-1, j)
                                break
                    start = i
        
        elif error_type == 6:  # SINGLE_DRONE_CUSTOMER
            start = 0
            for i in range(1, len(truck_routes)):
                if truck_routes[i] == 0:
                    segment = truck_routes[start:i]
                    if len(segment) == 2 and drone_assignment[segment[1]] == 1:
                        # Tìm khách hàng từ đoạn khác để chuyển sang
                        other_segment_found = False
                        other_start = 0
                        for j in range(1, len(truck_routes)):
                            if truck_routes[j] == 0 and j != i:
                                other_segment = truck_routes[other_start:j]
                                if len(other_segment) > 2:  # Đoạn có hơn 1 khách hàng
                                    customer_to_move = other_segment[-1]  # Lấy khách hàng cuối
                                    truck_routes.pop(other_start + len(other_segment) - 1)
                                    truck_routes.insert(start + 1, customer_to_move)
                                    other_segment_found = True
                                    break
                                other_start = j + 1
                        # Nếu không tìm được, chuyển drone_assignment sang 0
                        if not other_segment_found:
                            drone_assignment[segment[1]] = 0
                    start = i
        
        chromosome.truck_routes = truck_routes
        chromosome.drone_assignment = drone_assignment
        valid, error_type = is_valid_chromosome(chromosome, n_points, n_trucks, demands, Q)
    
    return chromosome