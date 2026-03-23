import datetime
import os

import gurobipy as gp
import numpy as np
from gurobipy import GRB

from read_data import read_fjsp_data_yao
from record_result import write_csv, write_csv_header


def solve_fjspt_yao(num_jobs, num_operations, num_machines, num_vehicles, NF, NL, PP, PM, TT, log_file_path='a.log'):
    try:
        V = 0x000fffff
        # h = calculate_upper_bound(num_jobs, p, operation_set, Delta, t_time_matrix)
        print(f"upper_bound: {V}")
        N = np.arange(0, num_operations)
        K = np.arange(0, num_machines)
        R = np.arange(0, num_vehicles)

        # Create a new model
        model = gp.Model("FJSP_AGV")
        model.setParam(GRB.Param.Presolve, 2)
        model.setParam(GRB.Param.LogFile, log_file_path)
        model.setParam(GRB.Param.TimeLimit, 36000)
        # model.setParam(GRB.Param.Threads, min(16, os.cpu_count()))
        # model.setParam(GRB.Param.MIPFocus, 0)
        # model.setParam(GRB.Param.MIPGap, 0)
        # model.setParam(GRB.Param.IntFeasTol, 1e-9)

        # Create variables
        c_max = model.addVar(vtype=GRB.CONTINUOUS, name="c_max")
        Pt = model.addVars(N, vtype=GRB.CONTINUOUS, name="Pt")
        Tt = model.addVars(N, vtype=GRB.CONTINUOUS, name="Tt")
        SO = model.addVars(N, vtype=GRB.CONTINUOUS, name="SO")
        ST = model.addVars(N, vtype=GRB.CONTINUOUS, name="ST")
        eta = model.addVars(N, vtype=GRB.BINARY, name="eta")
        phi = model.addVars(N, K, vtype=GRB.BINARY, name="phi")
        mu = model.addVars(N, R, vtype=GRB.BINARY, name="mu")
        y = model.addVars(N, N, K, vtype=GRB.BINARY, name="y")
        z = model.addVars(N, N, R, vtype=GRB.BINARY, name="z")

        # Set objective
        model.setObjective(c_max, GRB.MINIMIZE)

        # Add constraints
        # (3)
        model.addConstrs(eta[j] <= V * (2 - phi[j, k] - phi[j - 1, k])
                         for j in np.setdiff1d(N, NF)
                         for k in K)
        # (4)
        model.addConstrs(eta[j] >= 1 - V * (2 - phi[j, k] - phi[j - 1, k1])
                         for j in np.setdiff1d(N, NF)
                         for k in K
                         for k1 in K
                         if k != k1)
        # (6)
        model.addConstrs(c_max >= SO[j] + Pt[j]
                         for j in NL)
        # (7)
        model.addConstrs(gp.quicksum(phi[j, k] for k in K) == 1
                         for j in N)
        # (8)
        model.addConstrs(phi[j, k] <= PM[j][k]
                         for j in N
                         for k in K)
        # (9)
        model.addConstrs(Pt[j] == gp.quicksum(phi[j, k] * PP[j][k] for k in K)
                         for j in N)
        # (10)
        model.addConstrs(SO[j] >= SO[j1] + Pt[j1] - V * (2 - phi[j, k] - phi[j1, k]) - V * y[j, j1, k]
                         for j in N
                         for j1 in N
                         if j < j1
                         for k in K)
        # (11)
        model.addConstrs(SO[j1] >= SO[j] + Pt[j] - V * (2 - phi[j, k] - phi[j1, k]) - V * (1 - y[j, j1, k])
                         for j in N
                         for j1 in N
                         if j < j1
                         for k in K)
        # (12)
        model.addConstrs(eta[j] == 1
                         for j in NF)
        # (12)
        model.addConstrs(gp.quicksum(mu[j, r] for r in R) == eta[j]
                         for j in N)
        # (14)
        model.addConstrs(ST[j1] >= ST[j] + Tt[j] + TT[k + 1][k2 + 1] - V * (5 - phi[j, k] - phi[j1 - 1, k2] - mu[j, r] - mu[j1, r] - z[j, j1, r])
                         for j in N
                         for j1 in np.setdiff1d(N, NF)
                         if j != j1
                         for k in K
                         for k2 in K
                         for r in R)
        # (15)
        model.addConstrs(ST[j1] >= ST[j] + Tt[j] + TT[k + 1][0] - V * (4 - phi[j, k] - mu[j, r] - mu[j1, r] - z[j, j1, r])
                         for j in N
                         for j1 in NF
                         if j != j1
                         for k in K
                         for r in R)
        # (16)
        model.addConstrs(z[j, j1, r] + z[j1, j, r] == 1
                         for j in N
                         for j1 in N
                         if j != j1
                         for r in R)
        # (17)
        model.addConstrs(Tt[j] <= TT[k + 1][k1 + 1] + V * (2 - phi[j - 1, k] - phi[j, k1])
                         for j in np.setdiff1d(N, NF)
                         for k in K
                         for k1 in K)
        # (18)
        model.addConstrs(Tt[j] >= TT[k + 1][k1 + 1] - V * (2 - phi[j - 1, k] - phi[j, k1])
                         for j in np.setdiff1d(N, NF)
                         for k in K
                         for k1 in K)
        # (19)
        model.addConstrs(Tt[j] <= TT[0][k + 1] + V * (1 - phi[j, k])
                         for j in NF
                         for k in K)
        # (20)
        model.addConstrs(Tt[j] >= TT[0][k + 1] - V * (1 - phi[j, k])
                         for j in NF
                         for k in K)
        # (21)
        model.addConstrs(SO[j] >= ST[j] + Tt[j] - V * (1 - eta[j])
                         for j in N)
        # (22)
        model.addConstrs(SO[j] >= SO[j - 1] + Pt[j - 1] - V * eta[j]
                         for j in np.setdiff1d(N, NF))
        # (23)
        model.addConstrs(ST[j] + V * (1 - eta[j]) >= SO[j - 1] + Pt[j - 1]
                         for j in np.setdiff1d(N, NF))

        # Optimize model
        model.optimize()

        # for v in model.getVars():
        #     print('%s %g' % (v.VarName, v.X))
        print('Obj: %g' % model.ObjVal)

        return model
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ': ' + str(e))

    except AttributeError as e:
        print('Encountered an attribute error')


if __name__ == '__main__':
    csv_file = f'result/model_yao/result_model_yao_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
    write_csv_header(csv_file)

    dir_paths = ["benchmark/FJSPT/", "benchmark/EX/", "benchmark/SFJS/", "benchmark/MFJS/", "benchmark/MK/", "benchmark/case_study/"]
    result_paths = ["result/model_yao/FJSPT/", "result/model_yao/EX/", "result/model_yao/SFJS/",
                    "result/model_yao/MFJS/", "result/model_yao/MK/", "result/model_yao/case_study/"]
    for dir_path, result_path in zip(dir_paths, result_paths):
        instance_files = os.listdir(dir_path)
        for file in instance_files:
            file_name, ext = os.path.splitext(file)
            if ext == '.dat':
                fjs_file_path = dir_path + file_name + ".dat"
                num_jobs, num_operations, num_machines, NF, NL, PP, PM, TT = read_fjsp_data_yao(fjs_file_path)
                num_vehicles = 2
                log_file_path = result_path + file_name + ".log"
                optimal_solution_filename = result_path + file_name + "_optimal.txt"
                gantt_image_filename = result_path + file_name + ".svg"
                model = solve_fjspt_yao(num_jobs, num_operations, num_machines, num_vehicles, NF, NL, PP, PM, TT, log_file_path=log_file_path)
                title = f"{file_name}({num_jobs}-{num_operations}-{num_machines}-{num_vehicles})"
                write_csv(model, file_name, csv_file)
                print(title)
