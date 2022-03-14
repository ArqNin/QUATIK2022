import time
import TSP_utilities
from dwave_tsp_solver import DWaveTSPSolver
import graph_clustering, CommunityPainting, merge_partialTSPs
import collections
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import numpy as np

def solveTSPinstanceClustering(instance,name):
    cluster_size_threshold = 7
    nodes_array = TSP_utilities.readInstance(instance)
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    sapi_token = 'DEV-da3f0bbe6248b777cb2d858a24635889f0835b12'
    dwave_url = 'https://cloud.dwavesys.com/sapi'

    start_time = time.time()
    bf_start_time = start_time

    if sapi_token is None or dwave_url is None:
        print("You cannot run code on DWave without specifying your sapi_token and url")
    elif len(nodes_array) >= 100:
        print("This problem size is to big to run on D-Wave.")
    else:
        print()
        print("First, we calculate the corresponding clusters")
        print()
        start_time = time.time()
        total_partitions = graph_clustering.solvePartitionProblem(cluster_size_threshold,tsp_matrix,nodes_array)
        partitions = total_partitions[2]
        index = []
        route_aux = []
        list_index = []
        list_of_solutions = []
        
        
        clusters = max(partitions)
        
        print()
        print("We calculate now the optimal tour of each cluster")
        print(partitions)
        print()
        
        for i in range(clusters):
            cluster = i+1
            index = [i for i, e in enumerate(partitions) if e == cluster]
            list_index.append(index)
            reduced_node_list = [nodes_array[i] for i in index]
            reduced_tsp_matrix = TSP_utilities.get_tsp_matrix(reduced_node_list)

            cluster_size_threshold_aux = 4
            total_partitions_aux = graph_clustering.solvePartitionProblem(cluster_size_threshold_aux, reduced_tsp_matrix, reduced_node_list)
            partitions_aux = total_partitions_aux[2]

            dwave_solver = DWaveTSPSolver(reduced_tsp_matrix, partitions_aux, sapi_token=sapi_token, url=dwave_url)
            while True:
                dwave_solution, dwave_distribution = dwave_solver.solve_tsp_DWAVE_Advantadge()
                print('iteration')
                if len(dwave_solution) == len(reduced_tsp_matrix) and len(dwave_solution) == len(set(dwave_solution)):
                    print('exit')
                    break
            end_time = time.time()
            calculation_time = end_time - start_time
            costs = [(sol, TSP_utilities.calculate_cost(reduced_tsp_matrix, sol), dwave_distribution[sol]) for sol in dwave_distribution]
            solution_cost = TSP_utilities.calculate_cost(reduced_tsp_matrix, dwave_solution)
            print("DWave:", dwave_solution, solution_cost)
            print("Calculation time:", calculation_time)
#            for cost in costs:
#                print(cost)
            #TSP_utilities.plot_solution('dwave_' + str(cluster) + '_' + str(bf_start_time), reduced_node_list, dwave_solution)
            route_aux = [index[i] for i in dwave_solution]
            list_of_solutions.append(route_aux)
        
        print()
        print("We calculate now the optimal tour of each cluster")
        print()
        
        solution = merge_partialTSPs.recomposeTSPsubcycles(nodes_array,tsp_matrix,list_index,list_of_solutions)
        print(solution)
        route = list(solution[0])
        cost = solution[1]
        permutation_route = []
        permutation_route.append(route[0][0])
        permutation_route.append(route[0][1])
        del route[0]
        while len(route)>1:
            for sublist in route:
                if permutation_route[len(permutation_route)-1] in sublist:
                    sublist_aux = list(sublist)
                    sublist_aux.remove(permutation_route[len(permutation_route)-1])
                    permutation_route.append(sublist_aux[0])
                    route.remove(sublist)
                    break
            
        print(list_of_solutions)
        print(permutation_route)
        print(solution)
        TSP_utilities.plot_solution(name + str(bf_start_time), nodes_array, permutation_route)
        
        
        
def solveTSPinstance(instance,name):
    nodes_array = TSP_utilities.readInstance(instance)
    tsp_matrix = TSP_utilities.get_tsp_matrix(nodes_array)
    sapi_token = 'DEV-da3f0bbe6248b777cb2d858a24635889f0835b12'
    dwave_url = 'https://cloud.dwavesys.com/sapi'

    start_time = time.time()
    bf_start_time = start_time

    if sapi_token is None or dwave_url is None:
        print("You cannot run code on DWave without specifying your sapi_token and url")
    elif len(nodes_array) >= 100:
        print("This problem size is to big to run on D-Wave.")
    else:
        print("DWave solution")

        cluster_size_threshold = 4
        total_partitions = graph_clustering.solvePartitionProblem(cluster_size_threshold, tsp_matrix, nodes_array)
        partitions = total_partitions[2]

        start_time = time.time()
        dwave_solver = DWaveTSPSolver(tsp_matrix, partitions, sapi_token=sapi_token, url=dwave_url)
        while True:
            dwave_solution, dwave_distribution = dwave_solver.solve_tsp_DWAVE_Advantadge()
            print('iteration')
            if len(dwave_solution) == len(tsp_matrix) and len(dwave_solution) == len(set(dwave_solution)):
                print('exit')
                break
        end_time = time.time()
        calculation_time = end_time - start_time
        costs = [(sol, TSP_utilities.calculate_cost(tsp_matrix, sol), dwave_distribution[sol]) for sol in dwave_distribution]
        solution_cost = TSP_utilities.calculate_cost(tsp_matrix, dwave_solution)
        print("DWave:", dwave_solution, solution_cost)
        print("Calculation time:", calculation_time)
        TSP_utilities.plot_solution(name + str(bf_start_time), nodes_array, dwave_solution)

if __name__ == '__main__':

    #for i in range(3):
    #    solveTSPinstance("data/burma5.tsp","OPT_CLUSTERING_")

    for i in range(3):
        solveTSPinstanceClustering("data/burma14.tsp","OPT_CLUSTERING_")

#    for i in 1,2:
#        solveTSPinstanceClustering("data/burma14.tsp","CLUSTERING_")
#        solveTSPinstanceClustering("data/ulysses16.tsp","CLUSTERING_")
#        solveTSPinstanceClustering("data/ulysses22.tsp","CLUSTERING_")
#        solveTSPinstanceClustering("data/wi29.tsp","CLUSTERING_")
#        solveTSPinstanceClustering("data/dj38.tsp","CLUSTERING_")
#        solveTSPinstanceNOClustering("data/burma14.tsp","NO_CLUSTERING_")
#        solveTSPinstanceNOClustering("data/ulysses16.tsp","NO_CLUSTERING_")
#        solveTSPinstanceNOClustering("data/ulysses22.tsp","NO_CLUSTERING_")
#        solveTSPinstanceNOClustering("data/wi29.tsp","NO_CLUSTERING_")
#        solveTSPinstanceNOClustering("data/dj38.tsp","NO_CLUSTERING_")
    
    #Burma 3323
    #Ulysses16 6859
    #Ulysses22 7013
    #Wi29 27603 - http://www.math.uwaterloo.ca/tsp/world/witour.html
    #dj38 6656 - http://www.math.uwaterloo.ca/tsp/world/djtour.html