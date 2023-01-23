from matplotlib import pyplot as plt
import numpy as np

from simplicial_complex import SimplicialComplex2D, draw_2d_simplicial_complex

if __name__ == "__main__":
    a = 1
    standard_2_simplex = SimplicialComplex2D(
        vertices={0, 1, 2, 3, 4, 5, 6},
        simplexes=[[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 1]],
        colors={0: "red", 1: "yellow", 2: "green", 3: "yellow", 4: "green", 5: "yellow", 6: "green"},
        coordinates={
                        0: (np.array([0, 0])),
                        1: (np.array([a, 0])),
                        2: (np.array([a/2, a*np.sqrt(3)/2])),
                        3: (np.array([-a/2, a*np.sqrt(3)/2])),
                        4: (np.array([-a, 0])),
                        5: (np.array([-a/2, -a*np.sqrt(3)/2])),
                        6: (np.array([a/2, -a*np.sqrt(3)/2])),
                     },
        radii={0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.05, 6: 0.05}
    )

    # Take the second standard chromatic subdivision
    # scs2 = standard_2_simplex.standard_chromatic().standard_chromatic()
    scs2 = standard_2_simplex.delayed_snapshot(1)

    plt.figure(figsize=(7, 7))
    ax = plt.subplot(111)
    draw_2d_simplicial_complex(scs2.simplexes, colors=scs2.colors, pos=scs2.coordinates, radii=scs2.radii, ax=ax)
    plt.show()