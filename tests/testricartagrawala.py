# AHC Library
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, ConnectorTypes
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

# Graph
import networkx as nx
import random

# Time
import math
import time

# System Library
import sys
import argparse
sys.path.append('../') # Necessary for importing parent directory

# Distributed Algorithm
from RicartAgrawala.RicartAgrawala import RicartAgrawalaComponentModel

# Poisson event generator
def next_poisson_event(rate_parameter):
    return -math.log(1.0 - random.random()) / rate_parameter

def create_connected_topology(n, edge):
    G = nx.empty_graph(n)    
    # Create edge with probability
    i = 0
    while i < n-1:
        j = i+1
        while j < n:
            if random.random() <= edge:
                G.add_edge(i, j)
            j += 1
        i += 1
    
    # Ensuring at least one edge with single blobness
    connected_components = [G.subgraph(c) for c in nx.connected_components(G)]
    if len(connected_components) > 1:
        for x in range(len(connected_components) - 1):
            random_component_first = list(connected_components[x].nodes.keys())[random.randint(0, len(connected_components[x].nodes.keys())-1)]
            random_component_second = list(connected_components[x+1].nodes.keys())[random.randint(0, len(connected_components[x+1].nodes.keys())-1)]
            G.add_edge(random_component_first, random_component_second)

    return G

topology = Topology()

def main():
    parser = argparse.ArgumentParser(description='Raymond\'s Algorithm Tester')
    parser.add_argument('-n','--node', help='Total number of nodes in the test', required=True, type=int)
    parser.add_argument('-e','--edge', help='Probability of existing of edge between nodes (0.0, 1.0] - (fully seperated, fully connected] (ensuring at least one edge for a node)', required=True, type=float)
    parser.add_argument('-p','--privilege', help='Number of privilege request for random node in a test', required=True, type=int)
    parser.add_argument('-r','--rate', help='Poisson rate to generate privilege trigger for random node', required=True, type=int)
    parser.add_argument('-s','--scale', help='Using critical section time scale', required=True, type=float)
    args = vars(parser.parse_args())

    if args["edge"] > 1.0 or args["edge"] <= 0.0:
        print("Probability of existing of edge must be in (0.0, 1.0]")
        return 

    G = create_connected_topology(args["node"], args["edge"])

    topology.construct_from_graph(G, RicartAgrawalaComponentModel, GenericChannel)

    for x in range(args["node"]):
        topology.nodes[x].set_sleep_scaler(args["scale"])

    topology.start()

    for x in range(args["privilege"]):
        time.sleep(next_poisson_event(args["rate"]))
        random_node = random.randint(0, args["node"]-1)
        print("Node[",random_node,"] triggered for privilege.")
        topology.nodes[random_node].trigger_privilege()

    still_working = True
    while still_working:
        time.sleep(1)
        still_working = False
        print("####################")
        for x in range(args["node"]):
            if topology.nodes[x].want_privilege == True:
                still_working = True
                print("# Node[",x,"] : ",
                topology.nodes[x].clock, " - ",
                topology.nodes[x].request_clock, " - ",
                # topology.nodes[x].deferred_requests, " - ",
                set(list(range(args["node"]))).difference(topology.nodes[x].nodes_replied), " - ",
                topology.nodes[x].using_critical_section, " - ",
                topology.nodes[x].has_privilege, " - ",
                topology.nodes[x].want_privilege)
                # break
    
    topology.exit()

    # Collect and print data
    total_want_privilege = 0
    total_used_critical_section = 0
    total_released_critical_section = 0
    total_request_message_received = 0
    total_reply_message_received = 0
    total_request_message_sent = 0
    total_reply_message_sent = 0
    total_forwarded_message = 0
    for x in range(args["node"]):
        total_want_privilege += topology.nodes[x].total_want_privilege
        total_used_critical_section += topology.nodes[x].total_used_critical_section
        total_released_critical_section += topology.nodes[x].total_released_critical_section
        total_request_message_received += topology.nodes[x].total_request_message_received
        total_reply_message_received += topology.nodes[x].total_reply_message_received
        total_request_message_sent += topology.nodes[x].total_request_message_sent
        total_reply_message_sent += topology.nodes[x].total_reply_message_sent
        total_forwarded_message += topology.nodes[x].total_forwarded_message

    print("total_want_privilege : ", total_want_privilege)
    print("total_used_critical_section : ", total_used_critical_section)
    print("total_released_critical_section : ", total_released_critical_section)
    print("total_request_message_received : ", total_request_message_received)
    print("total_reply_message_received : ", total_reply_message_received)
    print("total_request_message_sent : ", total_request_message_sent)
    print("total_reply_message_sent : ", total_reply_message_sent)
    print("total_forwarded_message : ", total_forwarded_message)

if __name__ == "__main__":
    main()