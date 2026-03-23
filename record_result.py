import pandas
import csv


def write_csv_header(csv_file):
    header = ("Problem",
              "Current optimization status",
              "Indicates whether the model is a MIP",
              "Indicates whether the model has multiple objectives",
              "Current relative MIP optimality gap",
              "The objective value for the current solution",
              "Runtime for most recent optimization",
              "Work spent on most recent optimization",
              "Number of variables",
              "Number of integer variables",
              "NumBinVars",
              "Number of linear constraints",
              "Number of SOS constraints",
              "Number of quadratic constraints",
              "Number of general constraints",
              "Number of non-zero coefficients in the constraint matrix",
              "Number of non-zero coefficients in the constraint matrix (in double format)",
              "Number of non-zero quadratic objective terms",
              "Number of non-zero terms in quadratic constraints",
              "Number of stored solutions",
              "Number of simplex iterations performed in most recent optimization",
              "Number of barrier iterations performed in most recent optimization",
              "Number of branch-and-cut nodes explored in most recent optimization",
              "Number of open branch-and-cut nodes at the end of most recent optimization",
              "Maximum linear objective coefficient (in absolute value)",
              "MinObjCoeff Minimum (non-zero) linear objective coefficient (in absolute value)",
              "Maximum constraint right-hand side (in absolute value)",
              "Minimum (non-zero) constraint right-hand side (in absolute value)",
              "Number of objectives",
              "Number of solutions Gurobi found",
              "PoolObjVal")

    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)


def write_csv(model, problem_name, csv_file):
    csv_result = {"Problem": problem_name}
    status = ''
    match model.Status:
        case 1:
            status = "LOADED"
        case 2:
            status = "OPTIMAL"
        case 3:
            status = "INFEASIBLE"
        case 4:
            status = "INF_OR_UNBD"
        case 5:
            status = "UNBOUNDED"
        case 6:
            status = "CUTOFF"
        case 7:
            status = "ITERATION_LIMIT"
        case 8:
            status = "NODE_LIMIT"
        case 9:
            status = "TIME_LIMIT"
        case 10:
            status = "SOLUTION_LIMIT"
        case 11:
            status = "INTERRUPTED"
        case 12:
            status = "NUMERIC"
        case 13:
            status = "SUBOPTIMAL"
        case 14:
            status = "INPROGRESS"
        case 15:
            status = "USER_OBJ_LIMIT"
        case 16:
            status = "WORK_LIMIT"
        case 17:
            status = "MEM_LIMIT"
    csv_result["Current optimization status"] = status + "(" + str(model.Status) + ")"
    csv_result["Indicates whether the model is a MIP"] = model.IsMIP
    csv_result["Indicates whether the model has multiple objectives"] = model.IsMultiObj
    if model.IsMultiObj == 0:
        csv_result["Current relative MIP optimality gap"] = model.MIPGap
    csv_result["The objective value for the current solution"] = model.ObjVal
    csv_result["Runtime for most recent optimization"] = model.Runtime
    csv_result["Work spent on most recent optimization"] = model.Work

    csv_result["Number of variables"] = model.NumVars
    csv_result["Number of integer variables"] = model.NumIntVars
    csv_result["NumBinVars"] = model.NumBinVars

    csv_result["Number of linear constraints"] = model.NumConstrs
    csv_result["Number of SOS constraints"] = model.NumSOS
    csv_result["Number of quadratic constraints"] = model.NumQConstrs
    csv_result["Number of general constraints"] = model.NumGenConstrs

    csv_result["Number of non-zero coefficients in the constraint matrix"] = model.NumNZs
    csv_result["Number of non-zero coefficients in the constraint matrix (in double format)"] = model.DNumNZs
    csv_result["Number of non-zero quadratic objective terms"] = model.NumQNZs
    csv_result["Number of non-zero terms in quadratic constraints"] = model.NumQCNZs

    csv_result["Number of stored solutions"] = model.SolCount
    csv_result["Number of simplex iterations performed in most recent optimization"] = model.IterCount
    csv_result["Number of barrier iterations performed in most recent optimization"] = model.NodeCount
    csv_result["Number of branch-and-cut nodes explored in most recent optimization"] = model.NumQCNZs
    csv_result[
        "Number of open branch-and-cut nodes at the end of most recent optimization"] = model.OpenNodeCount

    csv_result["Maximum linear objective coefficient (in absolute value"] = model.MaxObjCoeff
    csv_result[
        "MinObjCoeff Minimum (non-zero) linear objective coefficient (in absolute value)"] = model.MinObjCoeff
    csv_result["Maximum constraint right-hand side (in absolute value)"] = model.MaxRHS
    csv_result["Minimum (non-zero constraint right-hand side (in absolute value)"] = model.MinRHS

    # get the set of variables
    variables = model.getVars()

    # Ensure status is optimal
    # assert model.Status == GRB.Status.OPTIMAL

    # Query number of multiple objectives, and number of solutions
    nSolutions = model.SolCount
    nObjectives = model.NumObj

    csv_result["Number of objectives"] = nObjectives
    csv_result["Number of solutions Gurobi found"] = nSolutions

    # For each solution, print value of first three variables, and
    # value for each objective function

    PoolObjVal = ''
    for s in range(nSolutions):
        # Set which solution we will query from now on
        model.params.SolutionNumber = s

        # Print objective value of this solution in each objective
        # print('Solution', s, ':', end=' ')
        if model.IsMultiObj == 0:
            PoolObjVal += str(model.PoolObjVal) + ','
        else:
            for o in range(nObjectives):
                # Set which objective we will query
                model.params.ObjNumber = o
                # Query the o-th objective value
                # print(model.ObjNVal, end=' ')
                PoolObjVal += str(model.ObjNVal) + ' '
            PoolObjVal += ','
    csv_result["PoolObjVal"] = PoolObjVal

    df = pandas.DataFrame(csv_result, index=[0])
    df.to_csv(csv_file, mode='a', index=False, header=False)