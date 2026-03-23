import datetime
import os

from FJSPT_model_all import solve_fjspt_all
from FJSPT_model_no_first_task import solve_fjspt_no_first_task
from FJSPT_model_no_lb import solve_fjspt_no_lb
from FJSPT_model_no_symmetry_breaking import solve_fjspt_no_symmetry_breaking
from FJSPT_model_yao import solve_fjspt_yao
from read_data import read_fjsp_data, read_fjsp_data_yao
from record_result import write_csv, write_csv_header
from show_solution import show_solution

if __name__ == '__main__':
    # benchmark_paths = ["benchmark/FJSPT/", "benchmark/EX/", "benchmark/SFJS/", "benchmark/MFJS/", "benchmark/MK/"]
    benchmark_paths = ["benchmark/case_study/"]

    print("all----------------------------")
    model_config = 'all'
    csv_file = f'result/model_{model_config}/result_model_{model_config}_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
    write_csv_header(csv_file)
    # result_paths = [f"result/model_{model_config}/FJSPT/", f"result/model_{model_config}/EX/", f"result/model_{model_config}/SFJS/",
    #                 f"result/model_{model_config}/MFJS/", f"result/model_{model_config}/MK/"]
    result_paths = [f"result/model_{model_config}/case_study/"]
    for dir_path, result_path in zip(benchmark_paths, result_paths):
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
    '''
    print("no_first_task----------------------------")
    model_config = 'no_first_task'
    csv_file = f'result/model_{model_config}/result_model_{model_config}_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
    write_csv_header(csv_file)
    result_paths = [f"result/model_{model_config}/FJSPT/", f"result/model_{model_config}/EX/", f"result/model_{model_config}/SFJS/",
                    f"result/model_{model_config}/MFJS/", f"result/model_{model_config}/MK/"]
    for dir_path, result_path in zip(benchmark_paths, result_paths):
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
                model = solve_fjspt_no_first_task(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, log_file_path=log_file_path)
                title = f"{file_name}({num_jobs}-{num_operations}-{num_machines}-{num_vehicles})"
                # show_solution(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, model, optimal_solution_filename,
                #               gantt_image_filename, title)
                write_csv(model, file_name, csv_file)
                print(title)

    print("no_lb----------------------------")
    model_config = 'no_lb'
    csv_file = f'result/model_{model_config}/result_model_{model_config}_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
    write_csv_header(csv_file)
    result_paths = [f"result/model_{model_config}/FJSPT/", f"result/model_{model_config}/EX/", f"result/model_{model_config}/SFJS/",
                    f"result/model_{model_config}/MFJS/", f"result/model_{model_config}/MK/"]
    for dir_path, result_path in zip(benchmark_paths, result_paths):
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
                model = solve_fjspt_no_lb(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, log_file_path=log_file_path)
                title = f"{file_name}({num_jobs}-{num_operations}-{num_machines}-{num_vehicles})"
                # show_solution(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, model, optimal_solution_filename,
                #               gantt_image_filename, title)
                write_csv(model, file_name, csv_file)
                print(title)

    print("no_symmetry_breaking----------------------------")
    model_config = 'no_symmetry_breaking'
    csv_file = f'result/model_{model_config}/result_model_{model_config}_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
    write_csv_header(csv_file)
    result_paths = [f"result/model_{model_config}/FJSPT/", f"result/model_{model_config}/EX/", f"result/model_{model_config}/SFJS/",
                    f"result/model_{model_config}/MFJS/", f"result/model_{model_config}/MK/"]
    for dir_path, result_path in zip(benchmark_paths, result_paths):
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
                model = solve_fjspt_no_symmetry_breaking(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix,
                                                         log_file_path=log_file_path)
                title = f"{file_name}({num_jobs}-{num_operations}-{num_machines}-{num_vehicles})"
                # show_solution(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, model, optimal_solution_filename,
                #               gantt_image_filename, title)
                write_csv(model, file_name, csv_file)
                print(title)
    
    print("yao----------------------------")
    model_config = 'yao'
    csv_file = f'result/model_{model_config}/result_model_{model_config}_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
    write_csv_header(csv_file)
    # result_paths = [f"result/model_{model_config}/FJSPT/", f"result/model_{model_config}/EX/", f"result/model_{model_config}/SFJS/",
    #                 f"result/model_{model_config}/MFJS/", f"result/model_{model_config}/MK/"]
    result_paths = [f"result/model_{model_config}/case_study/"]
    for dir_path, result_path in zip(benchmark_paths, result_paths):
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
                # show_solution(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix, model, optimal_solution_filename,
                #               gantt_image_filename, title)
                write_csv(model, file_name, csv_file)
                print(title)
    '''