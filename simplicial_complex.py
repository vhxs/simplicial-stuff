# modified from this:
# https://github.com/iaciac/py-draw-simplicial-complex/blob/master/Draw%202d%20simplicial%20complex.ipynb
from copy import copy

import networkx as nx
import itertools

import matplotlib.pyplot as plt
import numpy as np

np.random.seed(12)
eps = 1/3


class SimplicialComplex2D:
    def __init__(self, vertices, simplexes, colors, coordinates, radii):
        self.vertices = vertices
        self.simplexes = simplexes
        self.colors = colors
        self.coordinates = coordinates
        self.radii = radii

    def set_dimensions(self, dimensions):
        self.dimensions = dimensions

    def delayed_snapshot(self, resilience):
        # set vertex dimensions (carrier dimension) so that we can delete vertices later
        dimensions = {vertex: 0 for vertex in self.vertices}
        self.set_dimensions(dimensions)

        # we want a subcomplex of the second standard chromatic subdivision
        sc = self.standard_chromatic(resilience=resilience).standard_chromatic(resilience=resilience)
        sc.prune(resilience)
        return sc

    def standard_chromatic(self, resilience=None):
        new_vertices = copy(self.vertices)
        new_simplexes = []
        new_colors = copy(self.colors)
        new_coordinates = copy(self.coordinates)
        new_radii = copy(self.radii)

        # create fresh ids for new vertices
        self.vertex_id_counter = max(self.vertices) + 1

        # iterate through maximal simplexes
        for simplex in self.simplexes:
            self.create_new_vertices(simplex, new_vertices, new_simplexes, new_colors, new_coordinates, new_radii, resilience=resilience)

        # return a new object
        sc = SimplicialComplex2D(new_vertices, new_simplexes, new_colors, new_coordinates, new_radii)
        if resilience is not None:
            sc.set_dimensions(self.dimensions)
        return sc

    def get_and_increment(self):
        value = self.vertex_id_counter
        self.vertex_id_counter += 1
        return value

    # weighted towards y
    def two_centroid(self, x, y):
        return x * (1 - eps) / 2 + y * (1 + eps) / 2

    # symmetric in y and z
    def three_centroid(self, x, y, z):
        return x * (1 - eps) / 3 + y * (1 + eps / 2) / 3 + z * (1 + eps / 2) / 3

    def create_new_vertices(self, simplex, new_vertices, new_simplexes, new_colors, new_coordinates, new_radii, resilience=False):
        vertex1, vertex2, vertex3 = simplex
        coords1 = self.coordinates[vertex1]
        coords2 = self.coordinates[vertex2]
        coords3 = self.coordinates[vertex3]

        # create new ids
        vertex12a, vertex12b = self.get_and_increment(), self.get_and_increment()
        vertex23a, vertex23b = self.get_and_increment(), self.get_and_increment()
        vertex31a, vertex31b = self.get_and_increment(), self.get_and_increment()
        vertex123a = self.get_and_increment()
        vertex123b = self.get_and_increment()
        vertex123c = self.get_and_increment()
        if resilience is not None:
            self.dimensions[vertex123a] = self.dimensions[vertex123b] = self.dimensions[vertex123c] = 2
            self.dimensions[vertex12a] = self.dimensions[vertex12b] = max([1, self.dimensions[vertex1], self.dimensions[vertex2]])
            self.dimensions[vertex23a] = self.dimensions[vertex23b] = max([1, self.dimensions[vertex2], self.dimensions[vertex3]])
            self.dimensions[vertex31a] = self.dimensions[vertex31b] = max([1, self.dimensions[vertex3], self.dimensions[vertex1]])

        # compute coordinates for new vertices
        coords12a = self.two_centroid(coords1, coords2)
        coords12b = self.two_centroid(coords2, coords1)
        coords23a = self.two_centroid(coords2, coords3)
        coords23b = self.two_centroid(coords3, coords2)
        coords31a = self.two_centroid(coords3, coords1)
        coords31b = self.two_centroid(coords1, coords3)
        coords123a = self.three_centroid(coords1, coords2, coords3)
        coords123b = self.three_centroid(coords2, coords3, coords1)
        coords123c = self.three_centroid(coords3, coords1, coords2)

        # add them
        vertices_to_add = [vertex12a, vertex12b, vertex23a, vertex23b, vertex31a, vertex31b,
                           vertex123a, vertex123b, vertex123c]
        new_vertices.update(vertices_to_add)
        new_coordinates[vertex12a] = coords12a
        new_coordinates[vertex12b] = coords12b
        new_coordinates[vertex23a] = coords23a
        new_coordinates[vertex23b] = coords23b
        new_coordinates[vertex31a] = coords31a
        new_coordinates[vertex31b] = coords31b
        new_coordinates[vertex123a] = coords123a
        new_coordinates[vertex123b] = coords123b
        new_coordinates[vertex123c] = coords123c

        # give them a radius
        radius = min(self.radii[vertex1], self.radii[vertex2], self.radii[vertex3]) / 2
        for vertex in vertices_to_add:
            new_radii[vertex] = radius

        # color them
        new_colors[vertex12a] = new_colors[vertex1]
        new_colors[vertex12b] = new_colors[vertex2]
        new_colors[vertex23a] = new_colors[vertex2]
        new_colors[vertex23b] = new_colors[vertex3]
        new_colors[vertex31a] = new_colors[vertex3]
        new_colors[vertex31b] = new_colors[vertex1]
        new_colors[vertex123a] = new_colors[vertex1]
        new_colors[vertex123b] = new_colors[vertex2]
        new_colors[vertex123c] = new_colors[vertex3]

        # group them into simplexes
        # add them by shelling order [https://en.wikipedia.org/wiki/Shelling_(topology)
        new_simplexes.append([vertex1, vertex12b, vertex123c])
        new_simplexes.append([vertex1, vertex123c, vertex123b])
        new_simplexes.append([vertex1, vertex123b, vertex31a])
        new_simplexes.append([vertex12b, vertex123c, vertex12a])
        new_simplexes.append([vertex123c, vertex123b, vertex123a])
        new_simplexes.append([vertex123b, vertex31a, vertex31b])
        new_simplexes.append([vertex3, vertex31b, vertex123b])
        new_simplexes.append([vertex3, vertex123b, vertex123a])
        new_simplexes.append([vertex3, vertex123a, vertex23a])
        new_simplexes.append([vertex23a, vertex123a, vertex23b])
        new_simplexes.append([vertex2, vertex23b, vertex123a])
        new_simplexes.append([vertex2, vertex123a, vertex123c])
        new_simplexes.append([vertex2, vertex123c, vertex12a])

    def prune(self, resilience):
        # get vertices to delete
        vertices_to_delete = set()
        for vertex, dimension in self.dimensions.items():
            if dimension < (2 - resilience):
                vertices_to_delete.add(vertex)

        # update simplexes
        simplexes_to_keep = []
        for simplex in self.simplexes:
            keep = True
            for vertex in simplex:
                if vertex in vertices_to_delete:
                    keep = False
                    break
            if keep:
                simplexes_to_keep.append(simplex)
        self.simplexes = simplexes_to_keep

        # delete vertices
        self.vertices.difference_update(vertices_to_delete)

        # don't need this metadata anymore
        del self.dimensions

def draw_2d_simplicial_complex(simplices, colors=None, labels=None, radii=None, pos=None, return_pos=False, ax=None):
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
        radius = radii[i] if radii is not None else 0.05
        circ = plt.Circle((x, y), radius=radius, zorder=3, lw=0.5,
                          edgecolor='Black', facecolor=color, hatch=label)
        ax.add_patch(circ)

    if return_pos:
        return pos


