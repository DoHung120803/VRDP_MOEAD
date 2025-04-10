import random
import numpy as np
from chromosome_utils import Chromosome, initialize_chromosome
from validation import is_valid_chromosome
from local_search_repair import local_search_repair
from evaluate import evaluate_objectives
from input import x_coords, y_coords, demands, service_time, time_windows, drone_serve

# Tham số toàn cục
v_truck = 40  # Vận tốc xe tải (km/h)
v_drone = 80  # Vận tốc drone (km/h)
n_trucks = 20  # Số xe tải (có thể thay đổi tùy dữ liệu)
Q = 1000      # Tải trọng tối đa của xe tải
n_points = len(x_coords)  # Số điểm (depot + khách hàng)

# Order Crossover (OX) - Chỉ thay đổi truck_routes
def order_crossover(parent1, parent2):
    customers1 = [x for x in parent1.truck_routes if x != 0]
    customers2 = [x for x in parent2.truck_routes if x != 0]
    size = len(customers1)
    start, end = sorted([random.randint(0, size - 1) for _ in range(2)])
    
    child_customers = [-1] * size
    for i in range(start, end + 1):
        child_customers[i] = customers1[i]
    
    remaining = [x for x in customers2 if x not in child_customers]
    j = 0
    for i in range(size):
        if child_customers[i] == -1:
            child_customers[i] = remaining[j]
            j += 1
    
    truck_routes = [0]
    customers_per_truck = size // n_trucks
    for i in range(n_trucks - 1):
        truck_routes.extend(child_customers[i * customers_per_truck:(i + 1) * customers_per_truck])
        truck_routes.append(0)
    truck_routes.extend(child_customers[(n_trucks - 1) * customers_per_truck:])
    truck_routes.append(0)
    
    # Giữ nguyên drone_assignment từ parent1
    return Chromosome(truck_routes, parent1.drone_assignment)

# Swap Mutation - Chỉ thay đổi truck_routes
def swap_mutation(chromosome):
    customers = [x for x in chromosome.truck_routes if x != 0]
    if len(customers) < 2:
        return chromosome
    i, j = random.sample(range(len(customers)), 2)
    customers[i], customers[j] = customers[j], customers[i]
    
    truck_routes = [0]
    customers_per_truck = len(customers) // n_trucks
    for k in range(n_trucks - 1):
        truck_routes.extend(customers[k * customers_per_truck:(k + 1) * customers_per_truck])
        truck_routes.append(0)
    truck_routes.extend(customers[(n_trucks - 1) * customers_per_truck:])
    truck_routes.append(0)
    
    # Giữ nguyên drone_assignment
    return Chromosome(truck_routes, chromosome.drone_assignment)

# Tchebycheff Aggregation
def tchebycheff(chromosome, weight, z):
    makespan, carbon_emission, _ = evaluate_objectives(chromosome, x_coords, y_coords, v_truck, v_drone, service_time, n_trucks, time_windows)
    objectives = [makespan, carbon_emission]  # Chỉ tối ưu 2 mục tiêu
    return max(weight[i] * abs(objectives[i] - z[i]) for i in range(2))

# Lọc các giải pháp không bị chi phối
def get_non_dominated_solutions(pareto_front):
    non_dominated = []
    for i, (ind_i, objectives_i) in enumerate(pareto_front):
        dominated = False
        for j, (ind_j, objectives_j) in enumerate(pareto_front):
            if i != j:
                # Kiểm tra xem objectives_i có bị objectives_j chi phối không
                if (objectives_j[0] <= objectives_i[0] and objectives_j[1] <= objectives_i[1] and
                    (objectives_j[0] < objectives_i[0] or objectives_j[1] < objectives_i[1])):
                    dominated = True
                    break
        if not dominated:
            non_dominated.append((ind_i, objectives_i))
    return non_dominated

# MOEA/D
def moead(pop_size=100, generations=50):
    n_objectives = 2  # makespan và carbon_emission
    
    # Khởi tạo quần thể
    population = [initialize_chromosome(n_points, n_trucks, drone_serve) for _ in range(pop_size)]
    for i in range(pop_size):
        valid, _ = is_valid_chromosome(population[i], n_points, n_trucks, demands, Q)
        if not valid:
            population[i] = local_search_repair(population[i], n_points, n_trucks, demands, Q)
    
    # Khởi tạo trọng số
    weights = []
    for i in range(pop_size):
        w = np.random.dirichlet(np.ones(n_objectives), size=1)[0]
        weights.append(w)
    
    # Tìm láng giềng cho mỗi bài toán con
    B = []
    for i in range(pop_size):
        distances = [np.linalg.norm(weights[i] - weights[j]) for j in range(pop_size)]
        B.append(np.argsort(distances)[:10].tolist())  # 10 láng giềng gần nhất
    
    # Giá trị lý tưởng (z)
    z = [float('inf')] * n_objectives
    for ind in population:
        makespan, carbon_emission, _ = evaluate_objectives(ind, x_coords, y_coords, v_truck, v_drone, service_time, n_trucks, time_windows)
        z[0] = min(z[0], makespan)
        z[1] = min(z[1], carbon_emission)
    
    # Vòng lặp chính
    for gen in range(generations):
        for i in range(pop_size):
            # Chọn ngẫu nhiên 2 láng giềng
            neighbors = random.sample(B[i], 2)
            parent1, parent2 = population[neighbors[0]], population[neighbors[1]]
            
            # Tạo cá thể mới
            child = order_crossover(parent1, parent2)
            child = swap_mutation(child)
            
            # Sửa nếu không hợp lệ
            valid, _ = is_valid_chromosome(child, n_points, n_trucks, demands, Q)
            if not valid:
                child = local_search_repair(child, n_points, n_trucks, demands, Q)
            
            # Đánh giá và cập nhật z
            makespan, carbon_emission, _ = evaluate_objectives(child, x_coords, y_coords, v_truck, v_drone, service_time, n_trucks, time_windows)
            z[0] = min(z[0], makespan)
            z[1] = min(z[1], carbon_emission)
            
            # Cập nhật láng giềng
            for j in B[i]:
                if tchebycheff(child, weights[j], z) < tchebycheff(population[j], weights[j], z):
                    population[j] = child
        
        print(f"Thế hệ {gen + 1}/{generations} hoàn tất.")
    
    # Trả về tập Pareto
    pareto_front = []
    for ind in population:
        makespan, carbon_emission, avg_satisfaction = evaluate_objectives(ind, x_coords, y_coords, v_truck, v_drone, service_time, n_trucks, time_windows)
        pareto_front.append((ind, (makespan, carbon_emission, avg_satisfaction)))
    
    # Lọc các giải pháp không bị chi phối
    pareto_front = get_non_dominated_solutions(pareto_front)
    
    return pareto_front  

# Chạy MOEA/D
if __name__ == "__main__":
    pareto_front = moead(pop_size=50, generations=20)
    
    # In kết quả
    print("\nTập Pareto (Size: {})".format(len(pareto_front)))
    for ind, (makespan, carbon_emission, avg_satisfaction) in pareto_front:
        print(f"Tuyến: {ind.truck_routes}")
        # print(f"Drone Assignment: {ind.drone_assignment}")
        print(f"Makespan: {makespan:.2f}, Carbon Emission: {carbon_emission:.2f}, Avg Satisfaction: {avg_satisfaction:.4f}")
        print("-" * 50)