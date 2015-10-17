import networkx as nx
import random
from base_player import BasePlayer
from settings import *

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    def __init__(self, state):
        self.timefactor = 0.01
        self.l= GAME_LENGTH
        self.h = HUBS
        self.p = ORDER_CHANCE
        self.turnsToWait = min(1.0*self.h/self.p , self.timefactor*self.l*1.0)
        self.pendings = []
        self.guessedHubs = []
        self.stations = []

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
        #recomputing
        pending_orders = state.get_pending_orders()
        self.update_probs(pending_orders)

        self.guessedHubs = self.guessHubs()

        #after colecting some data
        if state.time > self.turnsToWait:
            graph = state.get_graph()
            station = graph.nodes()[0]

        commands = []
        for guess in self.guessedHubs:
            if guess not in self.stations:
                commands.append(self.build_command(guess))
                self.stations.append(guess)

        #print len(self.stations)
        if len(pending_orders) != 0:
            order = random.choice(pending_orders)
            bestPath = None
            bestLength = 9999
            for station in self.stations:
                apath = nx.shortest_path(graph, station, order.get_node())
                print(len(apath))
                if bestPath == None or len(apath) < len(bestPath):
                    bestPath = apath
                    bestLength = len(apath)
            if self.path_is_valid(state, bestPath):
                commands.append(self.send_command(order, bestPath))

            return commands
        return []
