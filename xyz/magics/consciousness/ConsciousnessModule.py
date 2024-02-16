""" 
============
ConsciousnessModule
============
@file_name: ConsciousnessModule.py
@author: Hongyi.Gu, Tianlei.Shi, BlackSheep-Team, Netmind.AI
@date: 2024-2-6

"""


from xyz.magics.momentum.MomentumModule import MomentumModule
from xyz.magics.momentum.momentumMemory.MomentumMemory import MomentumMemory
import matplotlib.pyplot as plt
import networkx as nx



class ConsciousnessModule:
    
    def __init__(self, shortterm_memory: MomentumMemory = MomentumMemory(
            sql_db = 'momentum_sql_db',
            milvus_host = '18.171.129.243',
            milvus_port = 80,
            milvus_user = 'root',
            milvus_psw = 'NetMindMilvusDB',
            sql_host = '18.171.129.243',
            sql_port = 3306,
            sql_user = 'netmind',
            sql_psw = 'NetMindMySQL',
        )):
        """Initiating Consciousness module with empty momentums
        """
        self.shortterm_memory = shortterm_memory
    
    def sort_momentum(self, inverse=True) -> list:
        """Sort priority of Momentums in self.momentums base on their energy and goals

        Parameters
        ----------
        inverse : bool, optional
            if the returned momentum list order from top priority to low priority or inversely, by default True

        Returns
        -------
        list
            list of momentum ids from top priority to low priority
        """
        sorted_keys = sorted(self.momentums.keys(), key=lambda x: self.momentums[x][2] - self.momentums[x][0])
        
        return sorted_keys
    
    def construct_graph(self, root_id) -> None:
        """Function to construct directed graph from short term memory to do energy distribution
        
        Parameters
        ----------
        G: NetworkX directed graph
        """
        # initiate graph
        G = nx.DiGraph()
        edge_set = []
        
        # iterate through the short term memory tree and get edge set
        queue = [root_id]
        while queue:
            current_node = queue.pop(0)
            child_set = self.shortterm_memory.get_child_id(root_id, table='short_term')
            if child_set:
                # currently set weight to be equal
                edge_set += [(root_id, child_id, 1, 'se') for child_id in child_set]
                queue += child_set
                
        for source, target, weight, label in edge_set:
            G.add_edge(source, target, weight=weight, label=label)
        self.graph = G
        return None
    
    def distribute_energy(self, source, initial_energy):
        """Distribute energy from the source node to its successors evenly.
        
        Parameters
        ----------
        G: NetworkX directed graph
        source: source node with initial energy
        initial_energy: energy of the source node
        """
        # Initialize all nodes with zero energy
        if not self.graph:
            raise Exception("Please construct graph out of memory first")
        
        G = self.graph
        nx.set_node_attributes(G, 0, 'energy')
        
        # Set initial energy for the source node
        G.nodes[source]['energy'] = initial_energy
        
        # Create a queue to process nodes level by level
        queue = [source]
        
        while queue:
            current_node = queue.pop(0)
            successors = [(ele, G[current_node][ele]["weight"]) for ele in G.successors(current_node)]
            if successors:
                # Calculate energy distribution by weight
                weight_sum = sum(ele[1] for ele in successors)
                for successor, successor_weight in successors:
                    # Update successor energy
                    G.nodes[successor]['energy'] += G.nodes[current_node]['energy'] * successor_weight / weight_sum
                    cc_energy = G.nodes[successor]['energy']
                    print(f'the current successor is {successor}, the energy passed is {cc_energy}')
                    
                    # Add successor to queue for further processing
                    queue.append(successor)
                    #G.nodes[current_node]['energy'] = 0
        return None
    
    def show_graph(self):
        """Show the graph
        """
        # Position nodes using the spring layout
        G = self.graph
        pos = nx.spring_layout(G, k=0.5)
        node_labels = {node: data['energy'] for node, data in G.nodes(data=True)}
        label_pos = {key: [value[0] + 0.1, value[1]] for key, value in pos.items()}

        # Draw the nodes
        nx.draw(G, pos, with_labels=False, node_color='skyblue', node_size=700)
        nx.draw_networkx_labels(G, pos, labels=node_labels)

        # Draw the edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

        # Show the graph
        plt.show()

        # Position nodes using the spring layout
        #pos = nx.spring_layout(G, k=0.5)

        # Draw the nodes
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=700)

        # Draw the edge labels
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

        # Show the graph
        plt.show()

    def choose_momentum(self) -> list:
        """Choose the top energy momentum that not resolved from graph and return

        Parameters
        ----------
        k : int, optional
            _description_, by default 3

        Returns
        -------
        list
            _description_
        """
        #first implementation base on threshold for decision, pure rule base
        
        raise NotImplementedError
    
    def update_momentum_attributes(self, momentum_id, new_attributes) -> None:
        """Function for updating attribute in the momentum, incluing it attribute such as energy or feedback

        Parameters
        ----------
        momentum_id : str
            momentum_id for momentum in self.momentums to update to
        new_attributes: dict
            new attributes value to update in momentum modules attribute dict
        """
        raise NotImplementedError
    
    def update_momentum_by_feedback(self, momentum_id, feedback) -> None:
        """Update the momentum from its feedback from the core LLM that process it. If it is finished: delete from momentem list and save in long term memory

        Parameters
        ----------
        momentum_id : str
            momentum_id for momentum in self.momentums to updata to
        feedback : str
            feedback from the core LLM processing the corresponding momentum
        """
        raise NotImplementedError