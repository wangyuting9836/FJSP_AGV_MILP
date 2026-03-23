from pathlib import Path
from typing import Union, Tuple

import numpy as np


def parse_job_line(line: list[int]) -> list[list[Tuple[int, int]]]:
    num_operations = line[0]
    operations = []
    idx = 1

    for _ in range(num_operations):
        num_pairs = int(line[idx]) * 2
        machines = line[idx + 1: idx + 1 + num_pairs: 2]
        durations = line[idx + 2: idx + 2 + num_pairs: 2]
        operations.append([(m, d) for m, d in zip(machines, durations)])

        idx += 1 + num_pairs

    return operations


def file2lines(loc: Union[Path, str]) -> list[list[int]]:
    with open(loc, "r") as fh:
        lines = [line for line in fh.readlines() if line.strip()]

    def parse_num(word: str):
        return int(word) if "." not in word else float(word)

    return [[parse_num(x) for x in line.split()] for line in lines]


def read_fjsp_data(instance_file):
    lines = file2lines(instance_file)
    num_jobs, num_machines = lines[0][0], lines[0][1]
    jobs_info = [parse_job_line(line) for line in lines[1:num_jobs + 1]]
    num_operations_of_job = [len(operations) for operations in jobs_info]
    num_operations = sum(num_operations_of_job)

    p = {}  # Processing time of O_{i,j} on machine k.
    operation_set = {}  # Set of operation operations of job i.
    Delta = {}  # Set of eligible machines for O_{ij}.
    Omega = {}  # Set of operations can be processed by machine k.

    for k in np.arange(1, num_machines + 1):
        Omega[k] = []

    for i in np.arange(1, num_jobs + 1):
        # p[i] = {}
        operation_set[i] = np.arange(1, num_operations_of_job[i - 1] + 1)
        for j in operation_set[i]:
            # p[i][j] = {}
            Delta[i, j] = []
            process_info = jobs_info[i - 1][j - 1]
            for k, process_time in process_info:
                p[i, j, k] = np.float32(process_time)
                Delta[i, j].append(k)
                Omega[k].append((i, j))

    t_time_matrix = np.array(lines[num_jobs + 1:], dtype=np.float32)

    return num_jobs, num_operations, num_machines, p, operation_set, Delta, Omega, t_time_matrix


def read_fjsp_data_yao(instance_file):
    lines = file2lines(instance_file)
    num_jobs, num_machines = lines[0][0], lines[0][1]
    jobs_info = [parse_job_line(line) for line in lines[1:num_jobs + 1]]
    num_operations_of_job = [len(operations) for operations in jobs_info]
    num_operations = sum(num_operations_of_job)

    NF = np.zeros(num_jobs, dtype=int)  # set of the first operation of all jobs
    NL = np.zeros(num_jobs, dtype=int)  # set of the last operation of all jobs
    PP = np.zeros((num_operations, num_machines), dtype=np.float32)  # the process time of operation j on the machine k
    PM = np.zeros((num_operations, num_machines), dtype=int)  # 0-1, whether the operation j can be processed on the machine k

    operation_index = 0
    for i in np.arange(0, num_jobs):
        NF[i] = operation_index
        for j in np.arange(0, num_operations_of_job[i]):
            process_info = jobs_info[i][j]
            for k, process_time in process_info:
                PP[operation_index][k-1] = np.float32(process_time)
                PM[operation_index][k-1] = 1
            operation_index += 1
        NL[i] = operation_index - 1

    TT = np.array(lines[num_jobs + 1:], dtype=np.float32)  # the transport time from machine k to machine k1

    return num_jobs, num_operations, num_machines, NF, NL, PP, PM, TT
