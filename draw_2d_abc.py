# modified from this:
# https://github.com/iaciac/py-draw-simplicial-complex/blob/master/Draw%202d%20simplicial%20complex.ipynb

import networkx as nx
import itertools

import matplotlib.pyplot as plt
import numpy as np

def draw_2d_simplicial_complex(simplices, colors=None, labels=None, pos=None, return_pos=False, ax=None):
    """
    Draw a simplicial complex up to dimension 2 from a list of simplices, as in [1].

        Args
        ----
        simplices: list of lists of integers
            List of simplices to draw. Sub-simplices are not needed (only maximal).
            For example, the 2-simplex [1,2,3] will automatically generate the three
            1-simplices [1,2],[2,3],[1,3] and the three 0-simplices [1],[2],[3].
            When a higher order simplex is entered only its sub-simplices
            up to D=2 will be drawn.

        pos: dict (default=None)
            If passed, this dictionary of positions d:(x,y) is used for placing the 0-simplices.
            The standard nx spring layour is used otherwise.

        ax: matplotlib.pyplot.axes (default=None)

        return_pos: dict (default=False)
            If True returns the dictionary of positions for the 0-simplices.
    """

    # List of 0-simplices
    nodes = list(set(itertools.chain(*simplices)))

    # List of 1-simplices
    edges = list(set(itertools.chain(
        *[[tuple(sorted((i, j))) for i, j in itertools.combinations(simplex, 2)] for simplex in simplices])))

    # List of 2-simplices
    triangles = list(set(itertools.chain(
        *[[tuple(sorted((i, j, k))) for i, j, k in itertools.combinations(simplex, 3)] for simplex in simplices])))

    if ax is None: ax = plt.gca()
    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    ax.axis('off')

    if pos is None:
        # Creating a networkx Graph from the edgelist
        G = nx.Graph()
        G.add_edges_from(edges)
        # Creating a dictionary for the position of the nodes
        pos = nx.spring_layout(G)

    # Drawing the edges
    for i, j in edges:
        (x0, y0) = pos[i]
        (x1, y1) = pos[j]
        line = plt.Line2D([x0, x1], [y0, y1], color='black', zorder=1, lw=0.7)
        ax.add_line(line)

    # Filling in the triangles
    for i, j, k in triangles:
        (x0, y0) = pos[i]
        (x1, y1) = pos[j]
        (x2, y2) = pos[k]
        tri = plt.Polygon([[x0, y0], [x1, y1], [x2, y2]],
                          edgecolor='black', facecolor=plt.cm.Blues(0.6),
                          zorder=2, alpha=0.4, lw=0.5)
        ax.add_patch(tri)

    # Drawing the nodes
    for i in nodes:
        (x, y) = pos[i]
        color = colors[i] if colors is not None else u'#ff7f0e'
        label = labels[i] if labels is not None else None
        circ = plt.Circle((x, y), radius=0.05, zorder=3, lw=0.5,
                          edgecolor='Black', facecolor=color, hatch=label)
        ax.add_patch(circ)

    if return_pos:
        return pos


if __name__ == "__main__":
    colors = {0: "red", 1: "green", 2: "yellow", 3: "red", 4: "green", 5: "yellow"}
    labels = {0: "//////", 1: "//////", 2: "//////", 3: None, 4: None, 5: None}

    simplices = [[0, 1, 2], [3, 4, 2], [3, 1, 5], [0, 4, 2], [0, 1, 5]]
    plt.figure(figsize=(7, 7))
    ax = plt.subplot(111)
    draw_2d_simplicial_complex(simplices, colors=colors, labels=labels, ax=ax)
    plt.show()
