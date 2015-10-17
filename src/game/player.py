import networkx as nx
import random
from base_player import BasePlayer
from settings import *

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    # You can set up static state here
    has_built_station = False

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : State
            The initial state of the game. See state.py for more information.
        """

        self.probs = [0] * GRAPH_SIZE
        self.order_processed = {}
        graph = state.get_graph()
        self.paths = []

        for src in GRAPH_SIZE:
            paths_from_src = nx.single_source_shortest_path(graph, src)
            self.paths.append(paths_from_src)

        return

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    def get_prob_from_dist(self, dist):
        return dist;

    def update_probs(self, pending_orders):
        for order in pending_orders:
            if order.id not in self.order_processed:
                # This is a new order!
                self.order_processed[order.id] = True
                # Update probs of all v
                for v in GRAPH_SIZE:
                    dist = len(self.paths[v][order.node])
                    self.probs[v] += get_prob_from_dist(dist)

    def guessHubs(self):
        hubs = [i for i in range(GRAPH_SIZE)]
        hubs.sort(key=lambda v: self.probs[v], reverse=True)
        return hubs

    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. This function must take less than Settings.STEP_TIMEOUT
        seconds.
        --- Parameters ---
        state : State
            The state of the game. See state.py for more information.
        --- Returns ---
        commands : dict list
            Each command should be generated via self.send_command or
            self.build_command. The commands are evaluated in order.
        """

        # We have implemented a naive bot for you that builds a single station
        # and tries to find the shortest path from it to first pending order.
        # We recommend making it a bit smarter ;-)

        graph = state.get_graph()
        pending_orders = state.get_pending_orders()
        
        self.update_probs(pending_orders)

        return commands
