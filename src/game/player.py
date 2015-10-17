import networkx as nx
import random
from base_player import BasePlayer
from settings import *
from norm import norm

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
        self.prev_orders = []

        self.reset_probs()
        self.order_processed_for_probs = {}
        self.total_orders_done_since_build = 0
        self.fulfilled_orders = []
        self.missed_orders = []

        graph = state.get_graph()
        self.paths = []

        for src in range(GRAPH_SIZE):
            paths_from_src = nx.single_source_shortest_path(graph, src)
            self.paths.append(paths_from_src)

        return

    def reset_probs(self):
        self.probs = [0] * GRAPH_SIZE

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    def get_prob_from_dist(self, dist):
        if dist == 0:
            return norm(0, 0.5, ORDER_VAR) * 2
        return norm(dist - 0.5, dist + 0.5, ORDER_VAR)

    def update_probs(self, orders):
        for order in orders:
            if order.id not in self.order_processed_for_probs:
            #    print('Update order #%s' % order.id)
                # This is a new order!
                self.order_processed_for_probs[order.id] = True
                # Update probs of all v
                for v in range(GRAPH_SIZE):
                    dist = len(self.paths[v][order.node])
                    self.probs[v] += self.get_prob_from_dist(dist)

    def guessHubs(self):
        hubs = [i for i in range(GRAPH_SIZE)]
        hubs.sort(key=lambda v: self.probs[v], reverse=True)
        # for hub in hubs:
        #     print('%s ' % self.probs[hub]),
        return hubs

    def update_orders(self, state):
        pending_orders = state.get_pending_orders()
        for order in pending_orders:
            if order not in self.prev_orders:
                self.total_orders_done_since_build += 1
                if order not in self.fulfilled_orders:
                    self.missed_orders.append(order)

    def should_build_station(self, state):
        cost = INIT_BUILD_COST * (BUILD_FACTOR ** len(self.stations))
        if cost > state.get_money():
            return False
        if self.total_orders_done_since_build == 0:
            return False
        if float(len(self.missed_orders)) / self.total_orders_done_since_build > 0.5:
            return True
        return False

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
        self.update_orders(state)

        if len(self.stations) == 0:
            self.update_probs(pending_orders)
        else:
            self.update_probs(self.missed_orders)

        self.guessedHubs = self.guessHubs()
        #print(self.guessedHubs)

        #after colecting some data
        if state.time > self.turnsToWait:
            graph = state.get_graph()
            station = graph.nodes()[0]

            commands = []

            for guess in self.guessedHubs:
                if guess not in self.stations:
                    if self.should_build_station(state):
                        commands.append(self.build_command(guess))
                        self.stations.append(guess)
                        self.guessedHubs = []
                        self.missed_orders = []
                        self.total_orders_done_since_build = 0
                        self.reset_probs()

            new_graph = graph.copy()
            for u, v in graph.edges():
                if graph.edge[u][v]['in_use']:
                    new_graph.remove_edge(u, v)

            #print len(self.stations)
            self.prev_orders = pending_orders

            random.shuffle(pending_orders)

            print(self.stations)

            for order in pending_orders:
                bestPath = None
                bestLength = 9999
                for station in self.stations:
                    if not nx.has_path(new_graph, station, order.get_node()):
                        continue
                    apath = nx.shortest_path(new_graph, station, order.get_node())

                    #print(len(apath))
                    if bestPath == None or len(apath) < len(bestPath):
                        bestPath = apath
                        bestLength = len(apath)

                if bestPath and bestLength * DECAY_FACTOR < order.money:
                    commands.append(self.send_command(order, bestPath))
                    self.fulfilled_orders.append(order)
                    for i in range(len(bestPath) - 1):
                        new_graph.remove_edge(bestPath[i], bestPath[i + 1])

                return commands

        return []
