import copy
import json
import math
import sys

import pygame
from abc import ABC
from math import inf
from queue import Queue
from typing import List

# import HelperAlgo
from api import MinHeapDijkstra
from api.GraphAlgoInterface import GraphAlgoInterface
from api.Node import Node
from api.GraphInterface import GraphInterface
from api.DiGraph import DiGraph
from api.Edge import Edge


class GraphAlgo(GraphAlgoInterface):
    def __init__(self, graph: DiGraph = None):
        self.graph = graph
        self.g = None
        self.initiated = False

    def get_graph(self) -> GraphInterface:
        return self.graph

    def load_from_json(self, file_name: str) -> bool:
        # send the file name to the DiGraph in order to use the load function
        self.graph = DiGraph(file_name)
        if self.graph is not None:
            return True
        else:
            return False

    """
    We save to json using the json.dump method
    in order to reach the correct format inorder to dump to json we create a dict which holds 2 keys
    those 2 keys hold lists of nodes and edges which hold dict's of nodes and edges. We add to those
    dict's by iterating over the nodes and edges of the graph and add them
    """

    def save_to_json(self, file_name: str) -> bool:
        nodes_array = []
        edges_array = []
        dictionary = {}
        for i in self.graph.nodes.keys():
            # iterate over the nodes in the graph and for every node insert its info to the list
            node_temp = self.graph.nodes.get(i)
            node_temp: Node
            nodes_dict = {}
            str_pos = node_temp.geolocation.__str__()
            # reformat the geolocation tuple to the json style
            str_pos = str_pos.replace(" ", "")
            str_pos = str_pos.replace("(", "")
            str_pos = str_pos.replace(")", "")
            nodes_dict["pos"] = str_pos
            # insert the id of the node as the id in the list
            nodes_dict["id"] = i
            nodes_array.append(nodes_dict)
            # iterate over the out edges of every node and insert their data to the list
            for j in node_temp.outEdges.keys():
                edge_dict = {}
                w = node_temp.outEdges.get(j)
                edge_dict["src"] = i
                edge_dict["w"] = w
                edge_dict["dest"] = j
                edges_array.append(edge_dict)
        dictionary["Edges"] = edges_array
        dictionary["Nodes"] = nodes_array
        try:
            # dumps the dict to json
            with open(file_name, 'w') as f:
                json.dump(dictionary, f)
                f.close()
            return True
        except:
            return False

    """
    This function returns the shortest between two nodes.
    It return the weight of the path and the shortest path itself. 
    """

    def shortest_path(self, id1: int, id2: int) -> (float, list):
        list_of_path = []
        if (not self.initiated):
            g_algo = GraphAlgo(self.graph)
            # init the dijkstra class
            self.g = MinHeapDijkstra.DijkstraUsingMinHeap.Graph(g_algo)
            self.initiated = True
        try:
            # send the node to the dijkstra function
            self.g.dijkstra_Getmin_distances(id1)
            # if there is no path between the two nodes then raise exception
            if self.g.heap_nodes[id2] == sys.maxsize:
                raise Exception()
            index = id2
            # iterate over the parents list till we reach the starting node
            while index != id1:
                # add the parent to the list
                list_of_path.insert(0, index)
                index = self.g.parents[index]
            # insert the starting node to the start of the path 
            list_of_path.insert(0, id1)
            # save the ans as the tuple contains the dist and the path
            ans = (self.g.heap_nodes[id2], list_of_path)
            return ans
        except:
            return inf, []

    def TSP(self, node_lst: List[int]) -> (List[int], float):
        actual_nodes_lst = []
        # we want to work with a list of nodes rather then a list of the id's of nodes
        for i in node_lst:
            actual_nodes_lst.append(self.graph.nodes.get(i))
        # first we search by a helper function if we even have a path between our node_lst if not we
        # obviously return none
        if not self.find_path(actual_nodes_lst, self.graph):
            return None
        try:
            best_path = []
            min_path = sys.maxsize
            # we will iterate over our node_lst and greedily search whats the best path to take from that node for which
            # we are iterating over ot reach all nodes in out nodes_lst.
            for j in range(len(actual_nodes_lst)):
                hold_cities = list(actual_nodes_lst)
                current = 0
                path = []
                src_i = j
                dest_i, current_dest = 0, 0
                src = actual_nodes_lst[src_i].key
                hold_cities.pop(src_i)
                path.append(src)
                ans: float
                while hold_cities:
                    min_dist = sys.maxsize
                    for i in range(len(hold_cities)):
                        a: int
                        a = hold_cities[i].key
                        ans = 0
                        # if the node we are searching for a path to from our src node is not in the path
                        # already we find the shortest path to it
                        if a not in path:
                            b = self.shortest_path(src, a)
                            ans = b[0]
                        dist = ans
                        # if we found a shorter distance we update that distance and
                        # the nodes we traveled to be the minimum
                        if dist != inf:
                            if dist < min_dist:
                                min_dist = dist
                                current_dest = a
                                dest_i = i
                        else:
                            break
                    current += min_dist
                    temp_path = self.shortest_path(src, current_dest)[1]
                    if temp_path is None:
                        return None  # because this means we couldn't find a path connecting all our nodes
                    flag_first = True
                    # iterate over the current founded path and add it to the path
                    for n in temp_path:
                        if flag_first:
                            flag_first = False
                        else:
                            path.append(n)
                    # now the dest became the src
                    hold_cities.pop(dest_i)
                    src = current_dest
                # the path with minimum dist is the best path
                if current < min_path:
                    min_path = current
                    best_path = path
            return best_path, min_path
        except:
            return None

    def centerPoint(self) -> (int, float):
        min_max_value = sys.maxsize
        index = 0
        g_algo = GraphAlgo(self.graph)
        # init the dijkstra algorithm
        g1 = MinHeapDijkstra.DijkstraUsingMinHeap.Graph(g_algo)
        try:
            # iterate over every node for the algorithm
            for i in self.graph.nodes.keys():
                g1.dijkstra_Getmin_distances(i)
                if g1.max == sys.maxsize:
                    raise Exception()
                # asking if the dist from the node with the maximum dist to the current node is the minimum dist
                if g1.max < min_max_value:
                    min_max_value = g1.max
                    index = i
            # the node with the minimum max dist is the center point 
            ans = (index, min_max_value)
            return ans
        except:
            return None, inf

    def get_edge_on_point(self, geo_location: tuple, type_of_edge: int) -> Edge:
        all_nodes = self.get_graph().get_all_v()
        for node in all_nodes.keys():
            edges = self.get_graph().all_out_edges_of_node(node)
            for edge in edges.values():
                loc = edge.get_point_on_edge(geo_location[0])
                if  loc == geo_location[1]:
                    if type_of_edge < 0 and edge.edge_type < 0:
                        return edge
                    elif type_of_edge > 0 and edge.edge_type > 0:
                        return edge

    def plot_graph(self) -> None:
        # call to the
        self.graph_plot()

    def graph_plot(self, ):
        pygame.init()
        scr = pygame.display.set_mode((900, 650))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            scr.fill((255, 255, 255))
            self.graph.set_location()
            scaling = self.graph.caclulate_minmax()
            min_x = scaling[0][0]
            min_y = scaling[0][1]
            lon = scaling[2][0]
            lat = scaling[2][1]
            color = (200, 30, 70)
            font = pygame.font.SysFont('Times ', 12)
            # iterate over the edges first and draw them
            for node in self.graph.nodes:
                for edge in self.graph.all_out_edges_of_node(node):
                    x1 = (self.graph.nodes[node].geolocation[0] - min_x) * (lon) + 60
                    y1 = (self.graph.nodes[node].geolocation[1] - min_y) * (lat) + 60
                    x2 = (self.graph.nodes[edge].geolocation[0] - min_x) * (lon) + 60
                    y2 = (self.graph.nodes[edge].geolocation[1] - min_y) * (lat) + 60
                    pygame.draw.line(scr, color, (x1, y1), (x2, y2), 2)
            # iterate over every edge and draw arrows to it if needed
            for node in self.graph.nodes:
                for edge in self.graph.all_out_edges_of_node(node):
                    x1 = (self.graph.nodes[node].geolocation[0] - min_x) * (lon) + 60
                    y1 = (self.graph.nodes[node].geolocation[1] - min_y) * (lat) + 60
                    x2 = (self.graph.nodes[edge].geolocation[0] - min_x) * (lon) + 60
                    y2 = (self.graph.nodes[edge].geolocation[1] - min_y) * lat + 60
                    self.draw_arrow_lines(scr, x1, y1, x2, y2, 6, 5)
            # iterate over the nodes and draw them
            for node in self.graph.nodes:
                x = (self.graph.nodes[node].geolocation[0] - min_x) * (lon) + 60
                y = (self.graph.nodes[node].geolocation[1] - min_y) * (lat) + 60
                pygame.draw.circle(scr, (0, 0, 0), (x, y), 4)
                txt = font.render(str(node), 1, (0, 150, 255))
                scr.blit(txt, (x - 8, y - 19))

            pygame.display.flip()
        pygame.quit()

    def draw_arrow_lines(self, scr: pygame.Surface, x1, y1, x2, y2, d, h):
        dx = x2 - x1
        dy = y2 - y1
        D = math.sqrt(dx * dx + dy * dy)
        xm = D - 3.5
        xn = xm
        ym = h
        yn = (0 - h)
        sin = dy / D
        cos = dx / D
        x = xm * cos - ym * sin + x1
        ym = xm * sin + ym * cos + y1
        xm = x
        x = xn * cos - yn * sin + x1
        yn = xn * sin + yn * cos + y1
        xn = x
        newX2 = (xm + xn) / 2
        newY2 = (ym + yn) / 2
        dx1 = newX2 - x1
        dy1 = newY2 - y1
        D1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
        xm1 = D1 - d
        xn1 = xm1
        ym1 = h
        yn1 = 0 - h
        sin1 = dy1 / D1
        cos1 = dx1 / D1
        nx = xm1 * cos1 - ym1 * sin1 + x1
        ym1 = xm1 * sin1 + ym1 * cos1 + y1
        xm1 = nx
        nx = xn1 * cos1 - yn1 * sin1 + x1
        yn1 = xn1 * sin1 + yn1 * cos1 + y1
        xn1 = nx
        points = [(newX2, newY2), (xm1, ym1), (xn1, yn1)]
        pygame.draw.polygon(scr, (200, 30, 70), points)
