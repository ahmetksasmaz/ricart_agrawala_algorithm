.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To deploy the algorithm, we utilized an event-driven node sourced from the adhoccomputing library. These nodes seamlessly manage events through an internal queue.

Communication among nodes occurs via channels, serving as direct links representing edges in the system's structure.

The algorithm encompasses four primary event types:

1. Requesting privilege
2. Releasing privilege
3. Receiving request messages
4. Receiving reply messages

For comprehensive details and formal definitions, consult the documentation.

To validate the algorithm, we initially construct an appropriate network topology. For the Ricart-Agrawala algorithm, a connected topology is required.

Creating a connected topology involves specifying the number of nodes and the probability of edge connections between pairs of nodes.

We systematically pair nodes and establish edges based on the provided probability. Subsequently, we verify connectivity among all components.

To ensure complete connectivity, any disjoint components are linked by randomly selecting nodes from each and connecting them with an edge.

Key Considerations:

1. When the probability equals 1.0, the topology becomes fully connected.

2. When the probability equals 0.0, although the topology is non-connected, our method ensures that all components remain connected, effectively resembling a linked list.

Once the topology is established, all nodes are activated.

Selected nodes are then prompted to request privilege at random intervals following a Poisson distribution.

The testing process waits until no nodes are requesting privilege.

Finally, data from all nodes is collected and analyzed to derive benchmark results, including:

1. Total privilege requests
2. Instances of duplicate privilege requests
3. Total critical section usage
4. Total critical section releases
5. Count of received request messages
6. Count of received reply messages
7. Count of sent request messages
8. Count of sent reply messages
9. Total forwarded messages

The relationship between total privilege requests and the sum of request and reply messages indicates message complexity.

Moreover, the correlation between total privilege requests and total critical section releases provides practical evidence of fairness and absence of starvation.

Additionally, it's notable that the number of edges inversely correlates with the total forwarded messages, highlighting an interesting aspect of the system's behavior.

Results
~~~~~~~~

Present your AHCv2 run results, plot figures.


This is probably the most variable part of any research paper, and depends upon the results and aims of the experiment. For quantitative research, it is a presentation of the numerical results and data, whereas for qualitative research it should be a broader discussion of trends, without going into too much detail. For research generating a lot of results, then it is better to include tables or graphs of the analyzed data and leave the raw data in the appendix, so that a researcher can follow up and check your calculations. A commentary is essential to linking the results together, rather than displaying isolated and unconnected charts, figures and findings. It can be quite difficulty to find a good balance between the results and the discussion section, because some findings, especially in a quantitative or descriptive experiment, will fall into a grey area. As long as you not repeat yourself to often, then there should be no major problem. It is best to try to find a middle course, where you give a general overview of the data and then expand upon it in the discussion - you should try to keep your own opinions and interpretations out of the results section, saving that for the discussion [Shuttleworth2016]_.


.. image:: figures/CDFInterferecePowerFromKthNode2.png
  :width: 400
  :alt: Impact of interference power


.. list-table:: Title
   :widths: 25 25 50
   :header-rows: 1

   * - Heading row 1, column 1
     - Heading row 1, column 2
     - Heading row 1, column 3
   * - Row 1, column 1
     -
     - Row 1, column 3
   * - Row 2, column 1
     - Row 2, column 2
     - Row 2, column 3

Discussion
~~~~~~~~~~

Present and discuss main learning points.




.. [Shuttleworth2016] M. Shuttleworth. (2016) Writing methodology. `Online <https://explorable.com/writing-methodology>`_.