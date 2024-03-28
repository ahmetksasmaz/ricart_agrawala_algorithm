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
        
        channel list deferred_channels, list of deferred channels
        integer total_channel_number, total number of channels in topology
        integer reply_count, number of replies received so far
        bool using_critical_section, a boolean represents whether node is using critical section or not
        bool has_privilege, a boolean represents whether node has privilege to use critical section
        timestamp request_timestamp, a timestamp for the moment of request for using critical section
        bool currently_interested, a boolean represents whether node is interested in using critical section

        If p wants to use critical section
            currently_interested ← true;
            request_timestamp ← timestamp();
            send request message (request_timestamp) into the all connected channels;

        If p ends using critical section
            using_critical_section ← false;
            currently_interested ← false;
            reply_count ← 0;
            if deferred_channels is not empty then
                has_privilege ← false;
                while deferred_channels is not empty
                    pop from deferred_channels into ⟨i⟩;
                    send reply message (timestamp()) into the channel ⟨i⟩;
                end while
            end if

        If p receives a reply message through a channel i
            reply_count ← reply_count + 1;
            if reply_count = total_channel_number then
                has_token ← true;
                using_critical_section ← true;
            end if
        
        If p receives a request message through a channel i
            message_timestamp ← message.timestamp()
            if using_critical_section = true then
                push ⟨i⟩ into deferred_channels;
            else then
                if currently_interested = false or request_timestamp > message_timestamp then
                    send reply message (timestamp()) into the channel ⟨i⟩;
                else then
                    push ⟨i⟩ into deferred_channels;
                end if
            end if

Explanation of pseudocode lines will be added later.

**Example**
~~~~~~~~

Will be added later.

**Correctness**
~~~~~~~~~~~

1. **Mutual Exclusion:** The proof of the Ricart-Agrawala algorithm's achievement of mutual exclusion is established through contradiction. Assume two sites, Si and Sj, are concurrently executing the critical section (CS), with Si's request having higher priority than Sj's. It's evident that Si received Sj's request after making its own. Thus, for Sj to execute the CS concurrently with Si, Si must reply to Sj's request before exiting the CS. However, this contradicts Sj's lower priority request. Hence, the Ricart-Agrawala algorithm ensures mutual exclusion.

**Complexity**
~~~~~~~~~~

1. **Message Complexity:** The Ricart-Agrawala algorithm needs 2 times (N - 1) messages for each critical section execution, comprising (N - 1) request messages and (N - 1) reply messages.
2. **Synchronization Delay:** Maximum message transmission time.

.. [SuzukiKasamiAlgorithm] Gerard Tel, Introduction to Distributed Algorithms, CAMBRIDGE UNIVERSITY PRESS, 2001
.. [RaymondsAlgorithm] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [RicartAgrawalaAlgorithm] Leslie Lamport, K. Mani Chandy: Distributed Snapshots: Determining Global States of a Distributed System. In: ACM Transactions on Computer Systems 3. Nr. 1, Februar 1985.
.. [MaekawasAlgorithm] Leslie Lamport, K. Mani Chandy: Distributed Snapshots: Determining Global States of a Distributed System. In: ACM Transactions on Computer Systems 3. Nr. 1, Februar 1985.