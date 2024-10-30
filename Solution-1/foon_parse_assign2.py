import re
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import time


class OptimizedFOONSearch:
    def __init__(self, foon_file, kitchen_file, motion_file):
        self.graph, self.unit_to_objects = self.load_foon(foon_file)
        self.kitchen = self.load_kitchen(kitchen_file)
        self.motion_data = self.load_motion(motion_file)

    def load_foon(self, foon_file):
        """Load and parse FOON data and create a map between units and objects to streamline searching."""
        with open(foon_file, 'r') as file:
            lines = file.readlines()

        units = []
        unit_to_objects = {}
        current_unit = []
        for line in lines:
            line = re.sub(r'[^\w\s]', '', line).strip().lower()
            line = re.sub(r'\s+', ' ', line)

            if line == '\\' or line == '':
                if current_unit:
                    units.append(current_unit)
                current_unit = []
            else:
                current_unit.append(line)

                if line.startswith('o'):
                    object_name = line.split()[1]
                    if object_name not in unit_to_objects:
                        unit_to_objects[object_name] = []
                    unit_to_objects[object_name].append(current_unit)

        return units, unit_to_objects

    def load_kitchen(self, kitchen_file):
        """Load available kitchen ingredients and utensils into a set for quick lookup."""
        kitchen = set()
        with open(kitchen_file, 'r') as file:
            for line in file:
                kitchen.add(line.strip().lower())
        return kitchen

    def load_motion(self, motion_file):
        """Parse motion data and store as a dictionary with motions and success rates."""
        motion_dict = {}
        with open(motion_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) >= 2:
                    motion = parts[0]
                    try:
                        success_rate = float(parts[1])
                    except ValueError:
                        continue
                    motion_dict[motion] = success_rate
        return motion_dict

    def available_in_kitchen(self, unit):
        """Check if the majority of input objects in the functional unit exist in the kitchen."""
        missing_objects = []
        for line in unit:
            if line.startswith('o'):
                object_name = line.split()[1]
                if object_name not in self.kitchen:
                    missing_objects.append(object_name)
        return True if not missing_objects else missing_objects

    def iterative_deepening_search(self, goal_object, goal_state, max_depth=40):
        """Conduct Iterative Deepening Search (IDS) to build a task tree to achieve the specified goal."""
        for depth in range(max_depth):
            print(f"Searching with depth limit: {depth}")
            result = self.depth_limited_search(goal_object, goal_state, depth)
            if result:
                return result
        print(f"Unable to locate goal within depth limit of {max_depth}")
        return None

    def depth_limited_search(self, goal_object, goal_state, depth):
        """Carry out a depth-limited search to find the task tree for the given goal."""
        if depth == 0:
            return None
        if goal_object not in self.unit_to_objects:
            print(f"Goal object {goal_object} not found in FOON data.")
            return None

        for unit in self.unit_to_objects[goal_object]:
            if self.unit_matches_goal(unit, goal_object, goal_state):
                kitchen_status = self.available_in_kitchen(unit)
                if kitchen_status is True:
                    print(f"Matching unit found at depth {depth}: {unit}")
                    return unit
                else:
                    print(f"Missing objects from the kitchen: {kitchen_status}")
            else:
                print(f"Unit does not match goal state: {unit}")

        return None

    def unit_matches_goal(self, unit, goal_object, goal_state):
        """Relax the goal state matching process to accept units close to the target state."""
        object_match = False
        state_match = False
        for line in unit:
            parts = line.split()
            if line.startswith('o'):
                object_name = parts[1]
                if goal_object == object_name:
                    object_match = True
            elif line.startswith('s'):
                state_value = ' '.join(parts[1:])
                if goal_state in state_value or goal_state == state_value:
                    state_match = True

        return object_match and state_match

    def a_star_search(self, goal_object, goal_state):
        """Execute A* Search to find the optimal task tree for the specified goal."""
        open_list = []
        closed_list = set()
        start_node = (0, goal_object, goal_state)
        heapq.heappush(open_list, start_node)

        while open_list:
            current_cost, current_object, current_state = heapq.heappop(open_list)
            if (current_object, current_state) in closed_list:
                continue

            closed_list.add((current_object, current_state))

            if current_object not in self.unit_to_objects:
                continue

            for unit in self.unit_to_objects[current_object]:
                if self.unit_matches_goal(unit, current_object, current_state) and self.available_in_kitchen(unit):
                    success_rate = self.motion_data.get(unit[0].split()[1], 1)
                    new_cost = current_cost + (1 / success_rate)
                    print(f"Matching unit found using A* search: {unit}")
                    return unit

        print("A* Search did not yield a task tree.")
        return None

    def save_task_tree(self, task_tree, filename):
        """Write the task tree to a file."""
        if task_tree:
            with open(filename, 'w') as file:
                file.write("Task Tree:\n")
                for line in task_tree:
                    file.write(line + '\n')
            print(f"Task tree saved to {filename}")
        else:
            print(f"No task tree available to save to {filename}")

    def visualize_task_tree(self, task_tree, filename="task_tree.png"):
        """Generate a visualization of the task tree and save it as an image."""
        if not task_tree:
            print("No task tree to visualize.")
            return
        
        G = nx.DiGraph()
        previous_node = None

        for line in task_tree:
            if line.startswith('o'): 
                object_name = line.split()[1]
                G.add_node(object_name)
                if previous_node:
                    G.add_edge(previous_node, object_name)
                previous_node = object_name
            elif line.startswith('m'): 
                motion_name = line.split()[1]
                G.add_node(motion_name)
                G.add_edge(previous_node, motion_name)
                previous_node = motion_name

        plt.figure(figsize=(8, 6))
        nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10, font_weight='bold')
        plt.title('FOON Task Tree')
        plt.savefig(filename)
        print(f"Task tree visualization saved as {filename}")


if __name__ == "__main__":
    foon_search = OptimizedFOONSearch('FOON.txt', 'kitchen.txt', 'motion.txt')

    goal_object = "omelette"
    goal_state = "cooked"

    # IDS
    start_time = time.time()
    ids_task_tree = foon_search.iterative_deepening_search(goal_object, goal_state, max_depth=40)
    print(f"IDS Search completed in {time.time() - start_time} seconds")
    foon_search.save_task_tree(ids_task_tree, 'ids_task_tree.txt')

    # A*
    start_time = time.time()
    astar_task_tree = foon_search.a_star_search(goal_object, goal_state)
    print(f"A* Search completed in {time.time() - start_time} seconds")
    foon_search.save_task_tree(astar_task_tree, 'astar_task_tree.txt')

    foon_search.visualize_task_tree(ids_task_tree)
