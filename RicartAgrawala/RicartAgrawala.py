"""
Distributed Computing Systems Mutual Exclusion Algorithms

This module implements Ricart-Agrawala Algorithm
"""

from enum import Enum
from time import sleep
import random
import networkx as nx

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import *

class RicartAgrawalaMessageTypes(Enum):
    """
    Ricart-Agrawala Algorithm has only two message types.
    One of them is request: it is sent when a node requests for privilege.
    Another of them is reply: it is sent as reply when request of another node is received.
    """
    REQUEST = "REQUEST"
    REPLY = "REPLY"

class RicartAgrawalaEventTypes(Enum):
    """
    Ricart Agrawala Algorithm has four event types.
    First one of them is want privilege: the event is triggered when a node wants to use critical section.
    Second one of them is release privilege: the event is triggered when a node is done with the critical section.
    Third one of them is get request: the event is triggered when a node receives a request message. (see RicartAgrawalaMessageTypes)
    Fourth one of them is get token: the event is triggered when a node receives a token message. (see RicartAgrawalaMessageTypes)
    """
    WANT_PRIVILEGE = "WANT_PRIVILEGE"
    RELEASE_PRIVILEGE = "RELEASE_PRIVILEGE"
    GET_REQUEST = "GET_REQUEST"
    GET_REPLY = "GET_REPLY"

class RicartAgrawalaMessagePayload(GenericMessagePayload):
    """
    Ricart Agrawala Algorithm has custom payload.
    It includes logical clock of the node.
    """
    def __init__(self, node_id, clock):
        self.node_id = node_id
        self.clock = clock

class RicartAgrawalaComponentModel(GenericModel):
    """
    This is a class for component represents a node running in a distributed environment that uses Ricart Agrawala algorithm to privilege critical section.
    """
    def __init__(self, component_name, component_instance_number, context=None, configuration_parameters=None, num_worker_threads=1, topology=None):
        """
        This is a constructor of the class. It defines the events (see RicartAgrawalaEventTypes), sets algorithm based member variables, initializes metrics for experiments.
        """
        super().__init__(component_name, component_instance_number, context, configuration_parameters, num_worker_threads, topology)

        self.eventhandlers[RicartAgrawalaEventTypes.WANT_PRIVILEGE] = self.on_want_privilege
        self.eventhandlers[RicartAgrawalaEventTypes.RELEASE_PRIVILEGE] = self.on_release_privilege
        self.eventhandlers[RicartAgrawalaEventTypes.GET_REQUEST] = self.on_get_request
        self.eventhandlers[RicartAgrawalaEventTypes.GET_REPLY] = self.on_get_reply

        self.clock = 0
        self.request_clock = None
        self.deferred_requests = []
        self.other_nodes = set()
        self.nodes_replied = set()
        self.using_critical_section = False
        self.has_privilege = False
        self.want_privilege = False

        # Metrics for experiments
        self.experiment_sleep_scaler = 1.0
        self.total_want_privilege = 0
        self.total_used_critical_section = 0
        self.total_released_critical_section = 0
        self.total_request_message_received = 0
        self.total_reply_message_received = 0
        self.total_request_message_sent = 0
        self.total_reply_message_sent = 0
        self.total_forwarded_message = 0

    def on_init(self, eventobj: Event):
        """
        This function is called when init event is triggered.
        Other nodes are set except the self.
        """
        self.other_nodes = set(self.topology.nodes)
        self.other_nodes.remove(self.componentinstancenumber)

    def on_message_from_bottom(self, eventobj: Event):
        """
        This function is called when message is received from bottom.
        Then proper Ricart Agrawala Event is triggered according to message type.
        In case of not fully connected topology, we forward others' messages. 
        """
        header = eventobj.eventcontent.header
        if header.messageto == self.componentinstancenumber:
            if header.messagetype == RicartAgrawalaMessageTypes.REQUEST:
                eventobj.event = RicartAgrawalaEventTypes.GET_REQUEST
            elif header.messagetype == RicartAgrawalaMessageTypes.REPLY:
                eventobj.event = RicartAgrawalaEventTypes.GET_REPLY
            self.send_self(eventobj)
        else:
            # Check are we in the shortest route?
            if self.componentinstancenumber == header.nexthop:
                next_hop = self.topology.get_next_hop(self.componentinstancenumber, header.messageto)
                interface_id = f"{self.componentinstancenumber}-{next_hop}"
                self.total_forwarded_message += 1
                header.nexthop = next_hop
                header.interfaceid = interface_id
                eventobj.eventcontent.header = header
                self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_want_privilege(self, eventobj: Event):
        """
        This function is called when self node wants privilege to use critical section.
        If the self node has already requested for privilege, nothing happens.
        If the self node is currently using critical section, nothing happens.
        Otherwise it is time to request for privilege.
        If we have the privilege (but not using), then we can use it.
        If we don't have the privilege, we should ask it.
        """
        if self.want_privilege == False: # Prevent duplicate request
            if self.using_critical_section == False: # Prevent on use request
                self.total_want_privilege += 1
                if self.has_privilege == True: # We already have the token, then use it
                    self.using_critical_section = True
                    self.use_critical_section()
                else: # We don't have the token
                    self.want_privilege = True
                    self.request_clock = self.clock
                    self.clock += 1
                    for node_id in self.other_nodes:
                        self.send_down(Event(self, EventTypes.MFRT, self.create_message(RicartAgrawalaMessageTypes.REQUEST, node_id, self.request_clock)))
                        self.total_request_message_sent += 1

    def on_release_privilege(self, eventobj: Event):
        """
        This function is called when self node is done with the critical section.
        We release the privilege, if there are some nodes that requests privilege in our queue,
        we forward the token to the first one. If still there are others waiting for the privilege, we request the token
        from our new parent.
        """
        self.total_released_critical_section += 1
        self.using_critical_section = False # End using critical section
        self.want_privilege = False
        self.nodes_replied.clear()
        if len(self.deferred_requests) > 0: # If there are others waiting for token
            self.has_privilege = False
            while len(self.deferred_requests) > 0:
                element = self.deferred_requests.pop()
                if self.clock <= element.clock:
                    self.clock = element.clock + 1
                self.send_down(Event(self, EventTypes.MFRT, self.create_message(RicartAgrawalaMessageTypes.REPLY, element.node_id)))
                self.total_reply_message_sent += 1

    def on_get_request(self, eventobj: Event):
        """
        This function is called when self node receives a request. If we have the privilege and currently using critical section
        we simply push the new one into deferred requests. If we have token but not using it, then we send reply.
        If we don't have token, we consider our urge to have privilege. If we want and requested before, other one's request is deferred. Otherwise the requester have priority.
        """
        self.total_request_message_received += 1
        node_id = eventobj.eventcontent.payload.node_id
        request_clock = eventobj.eventcontent.payload.clock
        if self.using_critical_section == False: # If we are not using the token
            if self.has_privilege == True: # If we have the token then give it
                self.has_privilege = False
                if self.clock <= request_clock:
                    self.clock = request_clock + 1
                self.send_down(Event(self, EventTypes.MFRT, self.create_message(RicartAgrawalaMessageTypes.REPLY, node_id)))
                self.total_reply_message_sent += 1
            else: # We don't have the token
                if self.want_privilege == True: # If also we want the privilege
                    if self.request_clock >= request_clock: # We wanted later, so we will give
                        if self.clock <= request_clock:
                            self.clock = request_clock + 1
                        self.send_down(Event(self, EventTypes.MFRT, self.create_message(RicartAgrawalaMessageTypes.REPLY, node_id)))
                        self.total_reply_message_sent += 1
                    else: # We wanted before, so the requester must wait
                        self.deferred_requests.append(eventobj.eventcontent.payload)
                else: # We don't want privilege, so the requester may have it
                    if self.clock <= request_clock:
                        self.clock = request_clock + 1
                    self.send_down(Event(self, EventTypes.MFRT, self.create_message(RicartAgrawalaMessageTypes.REPLY, node_id)))
                    self.total_reply_message_sent += 1
        else: # If we have the token and using critical section
            self.deferred_requests.append(eventobj.eventcontent.payload)
    
    def on_get_reply(self, eventobj:Event):
        """
        This function is called when self node receives reply message.
        We simply add the reply to replied nodes. If all other nodes has sent reply at the end, we start using critical section.
        """
        self.total_reply_message_received += 1
        node_id = eventobj.eventcontent.payload.node_id
        self.nodes_replied.add(node_id)
        if self.nodes_replied == self.other_nodes:
            self.has_privilege = True
            self.using_critical_section = True
            self.use_critical_section()

    # External trigger functions
    def trigger_privilege(self):
        """
        This function is used for external triggering when testing
        """
        self.send_self(Event(self, RicartAgrawalaEventTypes.WANT_PRIVILEGE, None)) # Trigger want privilege

    # Helper functions
    def create_message(self, message_type, node_id, request_clock = None):
        """
        This function is a helper function for creating messages.
        """
        header = None
        payload = RicartAgrawalaMessagePayload(self.componentinstancenumber, request_clock)
        next_hop = self.topology.get_next_hop(self.componentinstancenumber, node_id)
        interface_id = f"{self.componentinstancenumber}-{next_hop}"
        header = GenericMessageHeader(message_type, self.componentinstancenumber, node_id, next_hop, interface_id)
        return GenericMessage(header, payload)
    
    def use_critical_section(self):
        """
        This function is a dummy function for simulate using critical section.
        At the end of the sleep, it triggers release privilege event.
        """
        sleep(random.randint(1,3) * self.experiment_sleep_scaler) # Sleep for 1-3 seconds (multiplied by scaler to make faster experiments)
        self.total_used_critical_section += 1
        self.send_self(Event(self, RicartAgrawalaEventTypes.RELEASE_PRIVILEGE, None)) # Trigger releasing privilege
    
    def set_sleep_scaler(self, scale):
        """
        This function is a setter for sleep scaler for easier experiments.
        """
        self.experiment_sleep_scaler = scale