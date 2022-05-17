from pygame import Surface
from common import Vector
from rigidbody import Rigidbody
from quadtree import Entrance
from typing import Tuple, List, Callable


class World:
    def __init__(self, edgeWidth: int, windowRect: Tuple[float, float]):
        self.objs: Entrance = Entrance(edgeWidth, windowRect)
        self.forceField: List[Callable[[Rigidbody], Vector]] = []

    def register(self, rbody: Rigidbody) -> None:
        self.objs.append(rbody)

    def update(self, screen: Tuple[float, float]) -> None:
        self.objs.update(screen, self.forceField)

    def render(self, screen: Surface) -> None:
        self.objs.render(screen)
