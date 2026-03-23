import datetime
import os

import gurobipy as gp
import numpy as np
from gurobipy import GRB

from lower_bound import calculate_lower_bound, calculate_upper_bound
from read_data import read_fjsp_data
from record_result import write_csv, write_csv_header
from show_solution import show_solution


def solve_fjspt_all(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, log_file_path='a.log'):
    try:
        # h = 0x0000ffff
        h = calculate_upper_bound(num_jobs, p, operation_set, Delta, t_time_matrix)
        print(f"upper_bound: {h}")
        job_set = np.arange(1, num_jobs + 1)
        # machine_set = np.arange(1, num_machines + 1)
        vehicle_set = np.arange(1, num_vehicles + 1)

        lb = calculate_lower_bound(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix)

        # Create a new model
        model = gp.Model("FJSP_AGV")
        model.setParam(GRB.Param.Presolve, 2)
        model.setParam(GRB.Param.LogFile, log_file_path)
        model.setParam(GRB.Param.TimeLimit, 3600)
        # model.setParam(GRB.Param.Threads, min(16, os.cpu_count()))
        # model.setParam(GRB.Param.MIPFocus, 0)
        # model.setParam(GRB.Param.MIPGap, 0)
        # model.setParam(GRB.Param.IntFeasTol, 1e-9)

        # Create variables
        x = model.addVars(
            [
                (i, j, k)
                for i in job_set
                for j in operation_set[i]
                for k in Delta[i, j]
            ],
            vtype=GRB.BINARY, name="x"
        )
        q = model.addVars(
            [(i, j, k, i1, j1, k1)
             for i in job_set
             for j in operation_set[i]
             for i1 in job_set
             for j1 in operation_set[i1]
             if i < i1 or (i == i1 and j <= j1)
             for k in Delta[i, j]
             for k1 in Delta[i1, j1]],
            vtype=GRB.BINARY, name="q"
        )
        y = model.addVars(
            [
                (i, j, i1, j1, k)
                for i in job_set
                for i1 in job_set
                for j in operation_set[i]
                for j1 in operation_set[i1]
                if i != i1
                for k in set(Delta[i, j]) & set(Delta[i1, j1])
            ],
            vtype=GRB.BINARY, name="y"
        )
        z = model.addVars(
            [
                (i, j)
                for i in job_set
                for j in operation_set[i]
            ],
            vtype=GRB.BINARY, name="z"
        )
        w = model.addVars(
            [
                (i, j, r)
                for i in job_set
                for j in operation_set[i]
                for r in vehicle_set
            ],
            vtype=GRB.BINARY, name="w"
        )
        u = model.addVars(
            [
                (i, j, i1, j1, r)
                for i in job_set
                for i1 in job_set
                for j in operation_set[i]
                for j1 in operation_set[i1]
                if i != i1
                for r in vehicle_set
            ],
            vtype=GRB.BINARY, name="u"
        )
        a = model.addVars(
            [
                (i, j)
                for i in job_set
                for j in operation_set[i]
            ],
            vtype=GRB.CONTINUOUS, name="a", lb=0
        )
        c = model.addVars(
            [
                (i, j)
                for i in job_set
                for j in operation_set[i]
            ],
            vtype=GRB.CONTINUOUS, name="c", lb=0
        )
        c_max = model.addVar(vtype=GRB.CONTINUOUS, name="c_max", lb=lb)
        f = model.addVars(job_set, vehicle_set, vtype=GRB.BINARY, name="f")

        # Set objective
        model.setObjective(c_max, GRB.MINIMIZE)

        # Add constraints
        # (1)
        model.addConstrs(
            gp.quicksum(x[i, j, k] for k in Delta[i, j]) == 1
            for i in job_set
            for j in operation_set[i])
        # (2)
        model.addConstrs(
            gp.quicksum(q[i, j, k, i1, j1, k1] for k1 in Delta[i1, j1]) == x[i, j, k]
            for i in job_set
            for j in operation_set[i]
            for i1 in job_set
            for j1 in operation_set[i1]
            if i < i1 or (i == i1 and j <= j1)
            for k in Delta[i, j])
        # (3)
        model.addConstrs(
            gp.quicksum(q[i, j, k, i1, j1, k1] for k in Delta[i, j]) == x[i1, j1, k1]
            for i in job_set
            for j in operation_set[i]
            for i1 in job_set
            for j1 in operation_set[i1]
            if i < i1 or (i == i1 and j <= j1)
            for k1 in Delta[i1, j1])
        # (4)
        model.addConstrs(
            y[i, j, i1, j1, k] + y[i1, j1, i, j, k] == q[i, j, k, i1, j1, k]
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            for j1 in operation_set[i1]
            if i < i1
            for k in np.intersect1d(Delta[i, j], Delta[i1, j1]))
        # (5)
        model.addConstrs(
            c[i, j1] >= c[i, j] + p[i, j1, k] + (q[i, j, k, i, j1, k] - 1) * h
            for i in job_set
            for j in operation_set[i]
            for j1 in operation_set[i][1:]
            if j < j1
            for k in np.intersect1d(Delta[i, j], Delta[i, j1]))
        # (6)
        model.addConstrs(
            c[i1, j1] >= c[i, j] + p[i1, j1, k] + (y[i, j, i1, j1, k] - 1) * h
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            for j1 in operation_set[i1]
            if i != i1
            for k in np.intersect1d(Delta[i, j], Delta[i1, j1]))
        # (7)
        model.addConstrs(
            z[i, 1] == 1
            for i in job_set)
        # (8)
        model.addConstrs(
            z[i, j] == 1 - gp.quicksum(q[i, j - 1, k, i, j, k] for k in np.intersect1d(Delta[i, j - 1], Delta[i, j]))
            for i in job_set
            for j in operation_set[i][1:])
        # (9)
        model.addConstrs(
            gp.quicksum(w[i, j, r] for r in vehicle_set) == z[i, j]
            for i in job_set
            for j in operation_set[i])
        # (10)
        model.addConstrs(
            f[i, r] <= w[i, 1, r]
            for i in job_set
            for r in vehicle_set)
        # (11)
        model.addConstrs(
            gp.quicksum(f[i, r] for i in job_set) == 1
            for r in vehicle_set)
        # (12)
        model.addConstrs(
            gp.quicksum(i * f[i, r - 1] for i in job_set) <= gp.quicksum(i * f[i, r] for i in job_set)
            for r in vehicle_set[1:])
        # (13)
        model.addConstrs(
            u[i, j, i1, 1, r] <= -(w[i, j, r] + f[i1, r] - 2)
            for i in job_set
            for j in operation_set[i]
            for i1 in job_set
            if i != i1
            for r in vehicle_set)
        # (14)
        model.addConstrs(
            u[i, 1, i1, j1, r] >= 1 + (w[i1, j1, r] + f[i, r] - 2)
            for i in job_set
            for i1 in job_set
            for j1 in operation_set[i1]
            if i != i1
            for r in vehicle_set)
        # (15)
        model.addConstrs(
            u[i, j, i1, j1, r] + u[i1, j1, i, j, r] <= w[i, j, r]
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            for j1 in operation_set[i1]
            if i < i1
            for r in vehicle_set)
        # (16)
        model.addConstrs(
            u[i, j, i1, j1, r] + u[i1, j1, i, j, r] <= w[i1, j1, r]
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            for j1 in operation_set[i1]
            if i < i1
            for r in vehicle_set)
        # (17)
        model.addConstrs(
            u[i, j, i1, j1, r] + u[i1, j1, i, j, r] >= w[i, j, r] + w[i1, j1, r] - 1
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            for j1 in operation_set[i1]
            if i < i1
            for r in vehicle_set)
        # (18)
        model.addConstrs(
            a[i, j1] >= a[i, j]
            + gp.quicksum(t_time_matrix[k][k1] * q[i, j, k, i, j1 - 1, k1] for k in Delta[i, j] for k1 in Delta[i, j1 - 1])
            + gp.quicksum(t_time_matrix[k][k1] * q[i, j1 - 1, k, i, j1, k1] for k in Delta[i, j1 - 1] for k1 in Delta[i, j1])
            + (w[i, j, r] + w[i, j1, r] - 2) * h
            for i in job_set
            for j in operation_set[i]
            for j1 in operation_set[i][1:]
            if j < j1
            for r in vehicle_set)
        # (19)
        model.addConstrs(
            a[i1, j1] >= a[i, j]
            + gp.quicksum(t_time_matrix[k][k1] * q[i, j, k, i1, j1 - 1, k1] for k in Delta[i, j] for k1 in Delta[i1, j1 - 1])
            + gp.quicksum(t_time_matrix[k][k1] * q[i1, j1 - 1, k, i1, j1, k1] for k in Delta[i1, j1 - 1] for k1 in Delta[i1, j1])
            + (u[i, j, i1, j1, r] - 1) * h
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            for j1 in operation_set[i1][1:]
            if i < i1
            for r in vehicle_set)
        # (20)
        model.addConstrs(
            a[i1, j1] >= a[i, j]
            + gp.quicksum(t_time_matrix[k][k1] * q[i1, j1 - 1, k1, i, j, k] for k in Delta[i, j] for k1 in Delta[i1, j1 - 1])
            + gp.quicksum(t_time_matrix[k][k1] * q[i1, j1 - 1, k, i1, j1, k1] for k in Delta[i1, j1 - 1] for k1 in Delta[i1, j1])
            + (u[i, j, i1, j1, r] - 1) * h
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            for j1 in operation_set[i1][1:]
            if i > i1
            for r in vehicle_set)
        # (21)
        model.addConstrs(
            a[i1, 1] >= a[i, j]
            + gp.quicksum(t_time_matrix[k][0] * x[i, j, k] for k in Delta[i, j])
            + gp.quicksum(t_time_matrix[0][k] * x[i1, 1, k] for k in Delta[i1, 1])
            + (u[i, j, i1, 1, r] - 1) * h
            for i in job_set
            for i1 in job_set
            for j in operation_set[i]
            if i != i1
            for r in vehicle_set)
        # (22)
        model.addConstrs(
            a[i, 1] >= gp.quicksum(t_time_matrix[0][k] * x[i, 1, k] for k in Delta[i, 1])
            for i in job_set)
        # (23)
        model.addConstrs(
            c[i, j] >= a[i, j] + gp.quicksum(x[i, j, k] * p[i, j, k] for k in Delta[i, j])
            for i in job_set
            for j in operation_set[i])
        # (24)
        model.addConstrs(
            a[i, j] >= c[i, j - 1]
            + gp.quicksum(t_time_matrix[k][k1] * q[i, j - 1, k, i, j, k1] for k in Delta[i, j - 1] for k1 in Delta[i, j])
            for i in job_set
            for j in operation_set[i][1:])
        # (25)
        model.addConstrs(
            c_max >= c[i, operation_set[i][-1]]
            for i in job_set)
        # (26)
        # model.addConstr(c_max >= lb)

        # Optimize model
        model.optimize()

        # for v in model.getVars():
        #      print('%s %g' % (v.VarName, v.X))
        print('Obj: %g' % model.ObjVal)

        return model
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError as e:
        print('Encountered an attribute error')


if __name__ == '__main__':
    model_config = 'all'
    csv_file = f'result/model_all/result_model_all_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
    write_csv_header(csv_file)

    dir_paths = ["benchmark/FJSPT/", "benchmark/EX/", "benchmark/SFJS/", "benchmark/MFJS/", "benchmark/MK/", "benchmark/case_study/"]
    result_paths = ["result/model_all/FJSPT/", "result/model_all/EX/", "result/model_all/SFJS/",
                    "result/model_all/MFJS/", "result/model_all/MK/", "result/model_all/case_study/"]
    for dir_path, result_path in zip(dir_paths, result_paths):
        instance_files = os.listdir(dir_path)
        for file in instance_files:
            file_name, ext = os.path.splitext(file)
            if ext == '.dat':
                fjs_file_path = dir_path + file_name + ".dat"
                num_jobs, num_operations, num_machines, p, operation_set, Delta, Omega, t_time_matrix = read_fjsp_data(fjs_file_path)
                num_vehicles = 2
                log_file_path = result_path + file_name + ".log"
                optimal_solution_filename = result_path + file_name + "_optimal.txt"
                gantt_image_filename = result_path + file_name + ".svg"
                model = solve_fjspt_all(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, log_file_path=log_file_path)
                title = f"{file_name}({num_jobs}-{num_operations}-{num_machines}-{num_vehicles})"
                show_solution(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, model, optimal_solution_filename,
                              gantt_image_filename, title)
                write_csv(model, file_name, csv_file)
                print(title)
