import time
from typing import Sequence

import pygamebg
from matplotlib import pyplot as plt
import numpy as np
from pydantic import BaseModel, ConfigDict
from pygame import Vector2
import pygame
import random

from simplicial_complex import SimplicialComplex2D, draw_2d_simplicial_complex

# number of millisecond between updates
TIME_DELTA = 10
# number of milliseconds to move each one
TOTAL = 1000

width, height = 500, 500
screen = pygame.display.set_mode((width, height))


class Triangle(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id_: int
    current: Sequence[Vector2]
    end: Sequence[Vector2]
    color: tuple[int, int, int] = (255, 0, 0)
    active: bool = False
    step: int = 0

    def compute_velocity(self):
        delta = self.end[0] - self.current[0]
        return delta / TIME_DELTA

    def draw(self):
        if not self.active:
            pygame.draw.polygon(screen,
                                self.color,
                                self.current)

        else:
            velocity = self.compute_velocity()
            for idx in range(3):
                self.current[idx] += velocity
            pygame.draw.polygon(screen,
                                self.color,
                                self.current)

            self.step += 1

            if self.step >= TOTAL / TIME_DELTA:
                self.active = False

        return self.active


def new_frame():
    global triangles
    global active_idx

    screen.fill(pygame.Color("darkgray"))

    for idx, triangle in enumerate(triangles):
        still_active = triangle.draw()

        if active_idx == idx and not still_active:
            active_idx += 1
            if active_idx < len(triangles):
                triangles[active_idx].active = True


if __name__ == "__main__":
    a = 1
    standard_2_simplex = SimplicialComplex2D(
        vertices={0, 1, 2, 3, 4, 5, 6},
        simplexes=[[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 1]],
        colors={0: "red", 1: "yellow", 2: "green", 3: "yellow", 4: "green", 5: "yellow", 6: "green"},
        coordinates={
            0: (np.array([0, 0])),
            1: (np.array([a, 0])),
            2: (np.array([a / 2, a * np.sqrt(3) / 2])),
            3: (np.array([-a / 2, a * np.sqrt(3) / 2])),
            4: (np.array([-a, 0])),
            5: (np.array([-a / 2, -a * np.sqrt(3) / 2])),
            6: (np.array([a / 2, -a * np.sqrt(3) / 2])),
        },
        radii={0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.05, 6: 0.05}
    )

    # Take the second standard chromatic subdivision
    # scs2 = standard_2_simplex.standard_chromatic().standard_chromatic()
    scs2 = standard_2_simplex.delayed_snapshot(1)

    # plt.figure(figsize=(7, 7))
    # ax = plt.subplot(111)
    # draw_2d_simplicial_complex(scs2.simplexes, colors=scs2.colors, pos=scs2.coordinates, radii=scs2.radii, ax=ax)

    triangles = []
    for i, simplex in enumerate(scs2.simplexes):
        end = [200 * Vector2(*list(scs2.coordinates[id_])) + Vector2(200, 200) for id_ in simplex]
        random_offset = Vector2(200 * (random.random() + 500), 200 * (random.random() + 500))
        current = [point + random_offset for point in end]

        triangles.append(Triangle(
            id_=i,
            current=current,
            end=end,
        ))

    # plt.show()

    triangles[0].active = True
    active_idx = 0

    screen.fill(pygame.Color("darkgray"))
    pygame.display.update()
    pygame.time.delay(7000)
    pygamebg.frame_loop(10000, new_frame)
