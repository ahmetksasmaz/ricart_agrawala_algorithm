.. include:: substitutions.rst

|DistAlgName|
=========================================

Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In distributed systems, mutual exclusion is crucial for preventing race conditions, ensuring that only one process can access a critical section at any given time. Unlike single computer systems where shared variables can facilitate mutual exclusion, distributed systems lack shared memory and a common clock, necessitating different solutions.

Requirements for a mutual exclusion algorithm in distributed systems include:

    1. **No Deadlock:** Ensure processes don't indefinitely wait for messages.
    2. **No Starvation:** Every process should have a chance to execute its critical section in finite time.
    3. **Fairness:** Requests to execute critical sections should be executed in the order they arrive.
    4. **Fault Tolerance:** The system should recognize failures and continue functioning without disruption.

Solutions include:

    1. **Token Based Algorithm:** Uses a unique token shared among sites, allowing possession of the token to enter the critical section. Examples include the Suzuki-Kasami Algorithm [SuzukiKasamiAlgorithm]_ and Raymond's Algorithm [RaymondsAlgorithm]_.
    2. **Non-token based approach:** Sites communicate to determine which should execute the critical section next, using timestamps to order requests. Examples include the Ricart-Agrawala Algorithm [RicartAgrawalaAlgorithm]_ explained in this document.
    3. **Quorum based approach:** Sites request permission from a subset called a quorum, ensuring mutual exclusion through common subsets. Examples include Maekawa’s Algorithm [MaekawasAlgorithm]_.

These approaches address the challenges of distributed systems, ensuring safe and efficient access to critical sections while meeting system requirements.


Distributed Algorithm: |DistAlgName|
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Ricart-Agrawala Algorithm:**

    .. code-block:: RST
        :linenos:
        :caption: Ricart-Agrawala Algorithm [RicartAgrawalaAlgorithm]_.
        
        integer self_id, self node id
        request list deferred_requests, list of deferred requests
        node set other_nodes, set of other nodes in the topology
        node set nodes_replied, set of replied nodes for request
        bool using_critical_section, a boolean represents whether node is using critical section or not
        bool has_privilege, a boolean represents whether node has privilege to use critical section
        bool want_privilege, a boolean represents whether self node currently wants privilege or not
        integer request_clock, a logical clock stamp for the moment of request for using critical section
        integer clock, a logical clock for node 

        If p initializes
            other_nodes ← topology_nodes / self_id

        If p wants to use critical section
            if want_privilege = false then
                if using_critical_section = false then
                    if has_privilege = true then
                        using_critical_section ← true;
                    else then
                        want_privilege ← true;
                        request_clock ← clock;
                        clock ← clock + 1;
                        for node_id in other_nodes
                            send request message including request_clock to node with node_id
                        end for
                    end if

        If p ends using critical section
            using_critical_section ← false;
            want_privilege ← false;
            clear nodes_replied
            if deferred_requests is not empty then
                has_privilege ← false;
                while deferred_requests is not empty
                    pop from deferred_requests into deferred_request;
                    if clock <= deferred_request.clock then
                        clock ← deferred_request.clock + 1
                    end if
                    send reply message to node with deferred_request.node_id;
                end while
            end if

        If p receives a reply message from node i
            push ⟨i⟩ into nodes_replied
            if nodes_replied = other_nodes then
                has_privilege ← true;
                using_critical_section ← true;
            end if
        
        If p receives a request message from node i
            if using_critical_section = false then
                if has_privilege = true then
                    has_privilege ← false;
                    if clock <= message.clock then
                        clock ← message.clock + 1;
                    end if
                    send reply message to node with message.node_id;
                else then
                    if want_privilege = true then
                        if request_clock > message.clock then
                            if clock <= request_clock then
                                clock ← request_clock + 1;
                            end if
                            send reply message to node with message.node_id;
                        else then
                            push ⟨message⟩ into deferred_requests;
                        end if
                    else then
                        if clock <= message.clock then
                            clock ← message.clock + 1;
                        end if
                        send reply message to node with message.node_id;
                    end if
                endif
            else then
                push ⟨message⟩ into deferred_requests;
            end if

Lines[47-48] This function is called when init event is triggered. Other nodes are set except the self.

Lines[50-62]  This function is called when self node wants privilege to use critical section. If the self node has already requested for privilege, nothing happens. If the self node is currently using critical section, nothing happens. Otherwise it is time to request for privilege. If we have the privilege (but not using), then we can use it.If we don't have the privilege, we should ask it.

Lines[64-77] This function is called when self node is done with the critical section. We release the privilege, if there are some nodes that requests privilege in our queue, we forward the token to the first one. If still there are others waiting for the privilege, we request the token from our new parent.

Lines[79-84] This function is called when self node receives reply message. We simply add the reply to replied nodes. If all other nodes has sent reply at the end, we start using critical section.

Lines[86-113] This function is called when self node receives a request. If we have the privilege and currently using critical section we simply push the new one into deferred requests. If we have token but not using it, then we send reply. If we don't have token, we consider our urge to have privilege. If we want and requested before, other one's request is deferred. Otherwise the requester have priority.

**Example**
~~~~~~~~


**Correctness**
~~~~~~~~~~~

1. **Mutual Exclusion:** The proof of the Ricart-Agrawala algorithm's achievement of mutual exclusion is established through contradiction. Assume two sites, Si and Sj, are concurrently executing the critical section (CS), with Si's request having higher priority than Sj's. It's evident that Si received Sj's request after making its own. Thus, for Sj to execute the CS concurrently with Si, Si must reply to Sj's request before exiting the CS. However, this contradicts Sj's lower priority request. Hence, the Ricart-Agrawala algorithm ensures mutual exclusion.

**Complexity**
~~~~~~~~~~

1. **Message Complexity:** The Ricart-Agrawala algorithm needs 2 times (N - 1) messages for each critical section execution, comprising (N - 1) request messages and (N - 1) reply messages.
2. **Synchronization Delay:** Maximum message transmission time.

.. [SuzukiKasamiAlgorithm] Suzuki, I., & Kasami, T. (1985). A distributed mutual exclusion algorithm. ACM Transactions on Computer Systems (TOCS), 3(4), 344-349.
.. [RaymondsAlgorithm] Raymond, K. (1989). A tree-based algorithm for distributed mutual exclusion. ACM Transactions on Computer Systems (TOCS), 7(1), 61-77.
.. [RicartAgrawalaAlgorithm] Ricart, G., & Agrawala, A. K. (1981). An optimal algorithm for mutual exclusion in computer networks. Communications of the ACM, 24(1), 9-17.
.. [MaekawasAlgorithm] Maekawa, M. (1985). A sqrt(N) algorithm for mutual exclusion in decentralized systems. ACM Transactions on Computer Systems (TOCS), 3(2), 145-159.