import numpy as np


def calculate_lower_bound(num_jobs, num_machines, num_vehicles, p, operation_set, Delta, t_time_matrix):
    job_set = np.arange(1, num_jobs + 1)
    # machine_set = np.arange(1, num_machines + 1)

    min_t_first_op = np.array([
        np.min([
            t_time_matrix[0][k] for k in Delta[i, 1]
        ])
        for i in job_set
    ])
    min_t_first_op_whit_back = np.sum([
        np.min([
            t_time_matrix[0][k] + t_time_matrix[k][0] for k in Delta[i, 1]
        ])
        for i in job_set
    ])
    max_back_time_from_first_op = np.max([
        np.max([
            t_time_matrix[k][0] for k in Delta[i, 1]
        ])
        for i in job_set
    ])
    min_total_p_time = np.array([
        np.sum([
            np.min([
                p[i, j, k] for k in Delta[i, j]
            ]) for j in operation_set[i]
        ])
        for i in job_set
    ])
    min_t_p_time_successor_op = np.array([
        np.sum([
            np.min([
                t_time_matrix[k][k1] + p[i, j, k1] for k in Delta[i, j - 1] for k1 in Delta[i, j]
            ]) for j in operation_set[i][1:]
        ])
        for i in job_set
    ])
    min_t_p_time_first_op = np.array([
        np.min([
            t_time_matrix[0][k] + p[i, 1, k] for k in Delta[i, 1]
        ])
        for i in job_set
    ])
    min_p_time_first_op = np.array([
        np.min([
            p[i, 1, k] for k in Delta[i, 1]
        ])
        for i in job_set
    ])

    lower_bound1 = np.max(np.sum([min_t_p_time_first_op, min_t_p_time_successor_op], axis=0))
    lower_bound2 = min_t_first_op_whit_back / num_vehicles - max_back_time_from_first_op + np.min(
        np.sum([min_p_time_first_op, min_t_p_time_successor_op], axis=0))
    lower_bound3 = np.sum([min_total_p_time]) / num_machines + np.min(min_t_first_op)

    # operation_lower_bound = {}
    #
    # for i in np.arange(1, num_jobs + 1):
    #     operation_lower_bound[i, 1] = np.min([t_time_matrix[0][k] + p[i, 1, k] for k in Delta[i, 1]])
    #     for j in operation_set[i][1:]:
    #         operation_lower_bound[i, j] = operation_lower_bound[i, j - 1] + np.min(
    #             [t_time_matrix[k][k1] + p[i, j, k1] for k in Delta[i, j - 1] for k1 in Delta[i, j]])
    print([lower_bound1, lower_bound2, lower_bound3])
    return np.max([lower_bound1, lower_bound2, lower_bound3]).astype(np.float32)  # , operation_lower_bound


def calculate_upper_bound(num_jobs, p, operation_set, Delta, t_time_matrix):
    job_set = np.arange(1, num_jobs + 1)
    # machine_set = np.arange(1, num_machines + 1)

    max_total_p_time = np.array([
        np.sum([
            np.max([
                p[i, j, k] for k in Delta[i, j]
            ]) for j in operation_set[i]
        ])
        for i in job_set
    ])
    max_t_time_first_op = np.array([
        np.max([
            t_time_matrix[0][k] for k in Delta[i, 1]
        ])
        for i in job_set
    ])
    max_t_time_successor_op = np.array([
        np.sum([
            np.max([
                t_time_matrix[k][k1] for k in Delta[i, j - 1] for k1 in Delta[i, j]
            ]) for j in operation_set[i][1:]
        ])
        for i in job_set
    ])

    upper_bound = np.sum([max_total_p_time, max_t_time_first_op, max_t_time_successor_op]).astype(np.float32)
    return upper_bound
