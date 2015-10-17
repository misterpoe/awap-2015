def whereBuild(hub):
  nodes_cap = 100

  total_nodes = 1
  search_radius = 0
  (best, bestDeg) = (hub, nx.degree(hub))
  S = set([hub])
  visited = set()

  # cap on the nodes we look at and the distance from the predicted hub
  while (total_nodes < nodes_cap and search_radius < min(ORDER_VAR/2, SCORE_MEAN/DECAY_FACTOR):
    nextS = set()
    for s in S:
      if degree(s) > bestDeg and best not in self.stations: 
        (best, bestDeg) = (s, nx.degree(s))
      visited.add(s)
      for neighbor in nx.all_neighbours(self.graph, s):
        if neighbor not in visited:
          nextS.add(neighbor)
      total_nodes += 1
    search_radius += 1
    S = nextS
  return best

def shouldBuild():
  expected_profit = (GAME_LENGTH-state.time)*ORDER_CHANCE*(SCORE_MEAN-ORDER_VAR*DECAY_FACTOR)/(len(self.stations)+1)
  return expected_profit > INIT_BUILD_COST*(BUILD_FACTOR**len(self.stations))
