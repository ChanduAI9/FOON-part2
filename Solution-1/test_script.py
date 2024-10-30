import json
import time
import foon_parse_assign2
import graph_vis  

def run_goal_search(output_filename):
    foon_system = foon_parse_assign2.OptimizedFOONSearch('FOON.txt', 'kitchen.txt', 'motion.txt')
    
    target_object = "onion"
    desired_state = "ring shaped"
    
    start_time = time.time()
    matching_units = foon_system.iterative_deepening_search(target_object, desired_state)
    end_time = time.time()
    
    print(f"\nElapsed time for goal search: {end_time - start_time:.2f} seconds")
    
    search_results = {
        "target_object": target_object,
        "desired_state": desired_state,
        "matching_units": matching_units if matching_units else "No matching units identified"
    }
    with open(output_filename, 'w') as output_file:
        json.dump(search_results, output_file, indent=4)
    
    print(f"\nGoal search results for ({target_object}, {desired_state}) stored in {output_filename}")


def run_available_units_check(output_filename):
    foon_system = foon_parse_assign2.OptimizedFOONSearch('FOON.txt', 'kitchen.txt', 'motion.txt')
    
    usable_units = []
    for functional_unit in foon_system.graph:
        if foon_system.available_in_kitchen(functional_unit) == True:
            usable_units.append(functional_unit)
    
    print("\nFunctional units that can be executed with current kitchen resources:")
    available_units_info = {
        "usable_units": usable_units
    }
    with open(output_filename, 'w') as output_file:
        json.dump(available_units_info, output_file, indent=4)
    
    print(f"Usable functional units saved in {output_filename}")


def run_graph_conversion_and_visualization():
    foon_system = foon_parse_assign2.OptimizedFOONSearch('FOON.txt', 'kitchen.txt', 'motion.txt')
    
    graph_representation = graph_vis.foon_to_graph(foon_system.graph)
    print("\nGenerated Graph Data:")
    print(graph_representation)
    graph_vis.visualize_graph(graph_representation)


if __name__ == "__main__":
    run_goal_search('goal_search_results.json')
    run_available_units_check('available_units_results.json')
    run_graph_conversion_and_visualization()
