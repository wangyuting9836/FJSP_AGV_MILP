import numpy as np
import pandas as pd
from docplex.cp.solution import CpoSequenceVarSolution
from matplotlib import pyplot as plt

from gantt import set_gantt_color, gantt


def read_optimal_solution(solution_file: str) -> object:
    with open(solution_file, "r") as fh:
        lines = [line for line in fh.readlines() if line.strip()]
        return [(int(line.split()[0]), int(line.split()[1]), int(line.split()[2])) for line in lines]


def show_solution(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, model, optimal_solution_filename, gantt_image_filename, title):
    job_set = np.arange(1, num_jobs + 1)
    vehicle_set = np.arange(1, num_vehicles + 1)

    job_operation_array = [(i, j) for i in job_set for j in operation_set[i]]

    x = {
        (i, j, k): model.getVarByName(f'x[{i},{j},{k}]').X
        for i, j in job_operation_array
        for k in Delta[i, j]
    }
    w = {
        (i, j, r): model.getVarByName(f'w[{i},{j},{r}]').X
        for i, j in job_operation_array
        for r in vehicle_set
    }
    y = {
        (i, j, i1, j1, k): model.getVarByName(f'y[{i},{j},{i1},{j1},{k}]').X
        for i in job_set
        for i1 in job_set
        for j in operation_set[i]
        for j1 in operation_set[i1]
        if i != i1  # or (i == i1 and j < j1)
        for k in set(Delta[i, j]) & set(Delta[i1, j1])
    }
    u = {
        (i, j, i1, j1, r): model.getVarByName(f'u[{i},{j},{i1},{j1},{r}]').X
        for i, j in job_operation_array
        for i1, j1 in job_operation_array
        if i != i1  # or (i == i1 and j < j1)
        for r in vehicle_set
    }
    a = {
        (i, j): model.getVarByName(f'a[{i},{j}]').X
        for i, j in job_operation_array
    }
    c = {
        (i, j): model.getVarByName(f'c[{i},{j}]').X
        for i, j in job_operation_array
    }

    with open(optimal_solution_filename, 'w') as f:
        f.write("decision variables x\n")
        for key, value in x.items():
            if value > 0.8:
                i, j, k = key
                f.write(f"{i} {j} {k} {value}\n")
        f.write("decision variables w\n")
        for key, value in w.items():
            if value > 0.8:
                i, j, r = key
                f.write(f"{i} {j} {r} {value}\n")
        f.write("decision variables y\n")
        for key, value in y.items():
            if value > 0.8:
                i, j, i1, j1, k = key
                f.write(f"{i} {j} {i1} {j1} {k} {value}\n")
        f.write("decision variables u\n")
        for key, value in u.items():
            if value > 0.8:
                i, j, i1, j1, r = key
                f.write(f"{i} {j} {i1} {j1} {r} {value}\n")

    result_job = []
    result_agv = []
    for k in np.arange(1, num_machines + 1):
        result_job.append(
            {"bar_type": "PlaceholderBar",
             "machine": k,
             "label": "",
             "text": "",
             "color_category": 0,
             "start": 0,
             "finish": 0,
             })

    for i, j in job_operation_array:
        for k in Delta[i, j]:
            if x[i, j, k] >= 0.9:
                result_job.append(
                    {"bar_type": "NormalBar",
                     "machine": k,
                     "label": "Job" + str(i),
                     "text": "$O_{" + str(i) + "," + str(j) + "}$",
                     "color_category": i,
                     "start": c[i, j] - p[i, j, k],
                     "finish": c[i, j],
                     })

    for r in vehicle_set:
        t_order1 = {}
        for i, j in job_operation_array:
            if w[i, j, r] >= 0.9:
                t_order1[i, j] = 0
                for i1 in job_set:
                    for j1 in operation_set[i1]:
                        if (i1 != i and u[i1, j1, i, j, r] >= 0.9) or (i1 == i and j1 < j and w[i1, j1, r] >= 0.9):
                            t_order1[i, j] = t_order1[i, j] + 1
        t_order2 = {order: operation for operation, order in t_order1.items()}

        for i, j in job_operation_array:
            if w[i, j, r] >= 0.9:
                for k2 in Delta[i, j]:
                    if x[i, j, k2] > 0.9:
                        machine2 = k2
                        break
                if j == 1:
                    machine1 = 0
                else:
                    for k1 in Delta[i, j - 1]:
                        if x[i, j - 1, k1] > 0.9:
                            machine1 = k1
                            break
                if t_order1[i, j] == 0:
                    machine = 0
                else:
                    i1, j1 = t_order2[t_order1[i, j] - 1]
                    for k in Delta[i1, j1]:
                        if x[i1, j1, k] > 0.9:
                            machine = k
                            break

                start_time1 = a[i, j] - t_time_matrix[machine1][machine2]
                start_time2 = start_time1 - t_time_matrix[machine][machine1]
                if a[i, j] > start_time1:
                    result_agv.append(
                        {"agv": r,
                         "text": "$O_{" + str(i) + "," + str(j) + "}$",
                         "color_category": i,
                         "start_m": machine1,
                         "end_m": machine2,
                         "start": start_time1,
                         "finish": a[i, j]
                         })
                if start_time1 > start_time2:
                    result_agv.append(
                        {"agv": r,
                         "text": "",
                         "color_category": 0,
                         "start_m": machine,
                         "end_m": machine1,
                         "start": start_time2,
                         "finish": start_time1
                         })

    df_job = pd.DataFrame(result_job)
    df_agv = pd.DataFrame(result_agv)
    df_agv.sort_values(by=['agv', 'start', 'finish'], ascending=True, inplace=True, ignore_index=True)

    for r in vehicle_set:
        df_of_one_agv = df_agv[df_agv.agv == r]
        row_index = df_of_one_agv.index
        for i in range(len(row_index) - 1):
            if df_of_one_agv.start[row_index[i + 1]] > df_of_one_agv.finish[row_index[i]]:
                new_row = pd.DataFrame({
                    "agv": [r],
                    "text": [""],
                    "color_category": [-1],
                    "start_m": [df_of_one_agv.end_m[row_index[i]]],
                    "end_m": [df_of_one_agv.start_m[row_index[i + 1]]],
                    "start": [df_of_one_agv.finish[row_index[i]]],
                    "finish": [df_of_one_agv.start[row_index[i + 1]]],
                })
                df_agv = pd.concat([df_agv, new_row], ignore_index=True)

    max_finish = df_job.finish.max()
    # print(df)

    # set_gantt_color(df_job, palette="Pastel1")
    # set_gantt_color(df_agv, palette="Pastel1")
    set_gantt_color(df_job, palette="Set2")
    set_gantt_color(df_agv, palette="Set2")

    fig, axes = plt.subplots(1, 1, figsize=(7.5, 3))
    gantt(num_jobs, num_vehicles, data_job=df_job, data_agv=df_agv, max_finish=max_finish, show_title=True, show_y_lable=True, show_legend=True, title=title)
    plt.tight_layout()
    # plt.show()
    plt.savefig(gantt_image_filename, format='svg', dpi=600)
    plt.close(fig)


# 辅助函数：解析加工任务名称 OP_{i}_{j}_{k} → (i,j)
def parse_op_name(name):
    parts = name.split("_")
    return int(parts[1]), int(parts[2])


# 辅助函数：解析运输任务名称 T_{i}_{j}_{k1}_{k2}_{r} → (i,j, k1, k2)
def parse_trans_name(name):
    parts = name.split("_")
    return int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])


def show_solution_cp(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, model, sol, optimal_solution_filename, gantt_image_filename,
                     title):
    job_set = np.arange(1, num_jobs + 1)
    vehicle_set = np.arange(1, num_vehicles + 1)

    fig, ax = plt.subplots(figsize=(10, 5))

    with open(optimal_solution_filename, 'w') as f:
        # 1. 决策变量 x：机器加工分配
        f.write("decision variables x\n")
        for k in range(1, num_machines + 1):
            seq_sol = sol.get_var_solution(f"M_seq_{k}")
            if not isinstance(seq_sol, CpoSequenceVarSolution) or not seq_sol.get_value():
                continue
            for proc in seq_sol.get_value():
                i, j = parse_op_name(proc.get_name())
                f.write(f"{i} {j} {k} 1\n")

        # 2. 决策变量 w：AGV运输分配
        f.write("decision variables w\n")
        for r in vehicle_set:
            seq_sol = sol.get_var_solution(f"AGV_seq_{r}")
            if not isinstance(seq_sol, CpoSequenceVarSolution) or not seq_sol.get_value():
                continue
            for task in seq_sol.get_value()[1:]:
                i, j, _, _ = parse_trans_name(task.get_name())
                f.write(f"{i} {j} {r} 1\n")

        # 3. 决策变量 y：机器工序先后顺序
        f.write("decision variables y\n")
        for k in range(1, num_machines + 1):
            seq_sol = sol.get_var_solution(f"M_seq_{k}")
            ordered = seq_sol.get_value() if isinstance(seq_sol, CpoSequenceVarSolution) else []
            if len(ordered) < 2:
                continue
            # 遍历前驱-当前任务对
            for pre, cur in zip(ordered, ordered[1:]):
                i_pre, j_pre = parse_op_name(pre.get_name())
                i_cur, j_cur = parse_op_name(cur.get_name())
                f.write(f"{i_pre} {j_pre} {i_cur} {j_cur} {k} 1\n")

        # 4. 决策变量 u：AGV运输先后顺序
        f.write("decision variables u\n")
        for r in vehicle_set:
            seq_sol = sol.get_var_solution(f"AGV_seq_{r}")
            ordered = seq_sol.get_value() if isinstance(seq_sol, CpoSequenceVarSolution) else []
            if len(ordered) < 3:
                continue
            # 遍历前驱-当前任务对
            for pre, cur in zip(ordered[1:], ordered[2:]):
                i_pre, j_pre, _, _ = parse_trans_name(pre.get_name())
                i_cur, j_cur, _, _ = parse_trans_name(cur.get_name())
                f.write(f"{i_pre} {j_pre} {i_cur} {j_cur} {r} 1\n")

    result_job = []
    result_agv = []
    for k in np.arange(1, num_machines + 1):
        result_job.append(
            {"bar_type": "PlaceholderBar",
             "machine": k,
             "label": "",
             "text": "",
             "color_category": 0,
             "start": 0,
             "finish": 0,
             })
    for k in np.arange(1, num_machines + 1):
        machine_sequence_var_sol = sol.get_var_solution(f"M_seq_{k}")
        if not isinstance(machine_sequence_var_sol, CpoSequenceVarSolution):
            continue
        ordered_procs = machine_sequence_var_sol.get_value()
        if len(ordered_procs) == 0:
            continue
        for proc in ordered_procs:
            i, j = parse_op_name(proc.get_name())
            result_job.append(
                {"bar_type": "NormalBar",
                 "machine": k,
                 "label": "Job" + str(i),
                 "text": "$O_{" + str(i) + "," + str(j) + "}$",
                 "color_category": i,
                 "start": float(proc.start),
                 "finish": float(proc.end),
                 })

    for r in vehicle_set:
        vehicle_sequence_var_sol = sol.get_var_solution(f"AGV_seq_{r}")
        if not isinstance(vehicle_sequence_var_sol, CpoSequenceVarSolution):
            continue
        ordered_tasks = vehicle_sequence_var_sol.get_value()
        if len(ordered_tasks) == 1:
            continue
        pre_task = ordered_tasks[1]

        i_pre, j_pre, m1_pre, m2_pre = parse_trans_name(pre_task.get_name())

        result_agv.append(
            {"agv": r,
             "text": "$O_{" + str(i_pre) + "," + str(j_pre) + "}$",
             "color_category": i_pre,
             "start_m": m1_pre,
             "end_m": m2_pre,
             "start": float(pre_task.start),
             "finish": float(pre_task.end),
             })

        for task in ordered_tasks[2:]:
            i_cur, j_cur, m1_cur, m2_cur = parse_trans_name(task.get_name())
            if m1_cur != m2_pre:
                result_agv.append(
                    {"agv": r,
                     "text": "",
                     "color_category": 0,
                     "start_m": m2_pre,
                     "end_m": m1_cur,
                     "start": float(pre_task.end),
                     "finish": float(pre_task.end + t_time_matrix[m2_pre][m1_cur]),
                     })

            result_agv.append(
                {"agv": r,
                 "text": "$O_{" + str(i_cur) + "," + str(j_cur) + "}$",
                 "color_category": i_cur,
                 "start_m": m1_cur,
                 "end_m": m2_cur,
                 "start": float(task.start),
                 "finish": float(task.end),
                 })
            pre_task, m2_pre = task, m2_cur

    df_job = pd.DataFrame(result_job)
    df_agv = pd.DataFrame(result_agv)
    df_agv.sort_values(by=['agv', 'start', 'finish'], ascending=True, inplace=True, ignore_index=True)

    for r in vehicle_set:
        df_of_one_agv = df_agv[df_agv.agv == r]
        row_index = df_of_one_agv.index
        for i in range(len(row_index) - 1):
            if df_of_one_agv.start[row_index[i + 1]] > df_of_one_agv.finish[row_index[i]]:
                new_row = pd.DataFrame({
                    "agv": [r],
                    "text": [""],
                    "color_category": [-1],
                    "start_m": [df_of_one_agv.end_m[row_index[i]]],
                    "end_m": [df_of_one_agv.start_m[row_index[i + 1]]],
                    "start": [df_of_one_agv.finish[row_index[i]]],
                    "finish": [df_of_one_agv.start[row_index[i + 1]]],
                })
                df_agv = pd.concat([df_agv, new_row], ignore_index=True)

    max_finish = df_job.finish.max()
    # print(df)

    # set_gantt_color(df_job, palette="Pastel1")
    # set_gantt_color(df_agv, palette="Pastel1")
    set_gantt_color(df_job, palette="Paired")
    set_gantt_color(df_agv, palette="Paired")

    fig, axes = plt.subplots(1, 1, figsize=(9, 3))
    gantt(num_jobs, num_vehicles, data_job=df_job, data_agv=df_agv, max_finish=max_finish, show_title=True, show_y_lable=True, show_legend=True, title=title)
    plt.tight_layout()
    # plt.show()
    plt.savefig(gantt_image_filename, format='svg', dpi=600)
    plt.close(fig)
