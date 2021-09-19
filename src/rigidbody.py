from pygame import Surface
from shape import Shape
from common import *


class Rigidbody:
    def __init__(self, mass: float, s: Shape, pos: Vector, rotation: float = 0., elasticity: float = 1.):
        self.mass = mass
        self.shape = s
        self.position = pos
        self.rotation = rotation
        self.elasticity = elasticity
        self.linearVelocity = Vector(0., 0.)
        self.angularVelocity = 0.
        self.force = Vector(0., 0.)

    def render(self, screen: Surface):
        self.shape.render(screen, self.position, self.rotation)

    def update(self):
        self.linearVelocity += self.force / self.mass
        self.force.x = 0.
        self.force.y = 0.
        self.position += self.linearVelocity
        self.rotation += self.angularVelocity
