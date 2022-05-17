from pygame import Surface
from shape import Shape
from common import *
from typing import List, Callable


class Rigidbody:
    def __init__(self, mass: float, s: Shape, pos: Vector, rotation: float = 0., elasticity: float = 1.):
        self.mass: float = mass
        self.shape: Shape = s
        self.position: Vector = pos
        self.rotation: float = rotation
        self.elasticity: float = elasticity
        self.linearVelocity: Vector = Vector(0., 0.)
        self.angularVelocity: float = 0.
        self.force: Vector = Vector(0., 0.)
        self.triggers: List[Callable[[Rigidbody, Rigidbody], None]] = []
        self.destroyed: bool = False

    def render(self, screen: Surface) -> None:
        self.shape.render(screen, self.position, self.rotation)

    def update(self) -> None:
        self.linearVelocity += self.force / self.mass
        self.force.x = 0.
        self.force.y = 0.
        self.position += self.linearVelocity
        self.rotation += self.angularVelocity

    def destroy(self) -> None:
        self.destroyed = True


class StaticRigidbody(Rigidbody):
    def __init__(self, mass: float, s: Shape, pos: Vector, rotation: float = 0., elasticity: float = 1.):
        super().__init__(mass, s, pos, rotation, elasticity)
        self.posStable: Vector = pos
        self.rotStable: float = rotation

    def update(self) -> None:
        self.linearVelocity = Vector(0., 0.)
        self.angularVelocity = 0.
        self.position = self.posStable
        self.rotation = self.rotStable
