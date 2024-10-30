import networkx as nx
import matplotlib.pyplot as plt

def foon_to_graph(foon_data):
    """Convert FOON data to graph nodes and links."""
    G = nx.DiGraph()  

    for unit in foon_data:
        previous_object = None
        for line in unit:
            if line.startswith('o'):  # Object
                object_name = line.split()[1]
                G.add_node(object_name)
                if previous_object is not None:
                    G.add_edge(previous_object, object_name) 
                previous_object = object_name

            elif line.startswith('m'):  
                manipulation_name = line.split()[1]
                G.add_node(manipulation_name)
                if previous_object is not None:
                    G.add_edge(previous_object, manipulation_name)
                previous_object = manipulation_name

            elif line.startswith('s'):
                continue

    return G


def visualize_graph(G):
    """Visualize the FOON graph using NetworkX and Matplotlib."""
    plt.figure(figsize=(10, 8))

    pos = nx.spring_layout(G) 
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, edge_color='gray', font_weight='bold')

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title('FOON Graph Visualization')
    plt.show()
