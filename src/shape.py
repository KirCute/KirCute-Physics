import abc
import pygame
from common import *


class Shape(metaclass=abc.ABCMeta):
    def __init__(self, radius: float):
        self.radius = radius
        self.color = (127, 127, 127)

    @abc.abstractmethod
    def render(self, screen: pygame.Surface, position: Vector, rotation: float):
        pass


class Circle(Shape):
    def render(self, screen: pygame.Surface, position: Vector, rotation: float):
        pygame.draw.circle(screen, self.color, position.tuple(), self.radius, 0)


class Polygon(Shape):
    def __init__(self, halfL: float, points: list):
        super().__init__(halfL * math.sqrt(2))
        self.pointsR = []
        for p in points:
            self.pointsR.append(p * halfL)
        self.pointsR.append(self.pointsR[0])
        self.points = []
        self.normals = []
        for i in range(len(self.pointsR) - 1):
            self.points.append(self.pointsR[i])
            s = self.pointsR[i]
            e = self.pointsR[i + 1]
            direction = (e - s).rotate(math.pi / 2.)
            direction *= (direction % s)
            self.normals.append(direction.normalize())

    def render(self, screen: pygame.Surface, position: Vector, rotation: float):
        location = []
        for point in self.points:
            location.append((point.rotate(rotation) + position).tuple())
        pygame.draw.polygon(screen, self.color, location, 0)


'''
class Rectangle(Shape):
    def __init__(self, radius: int, scale: float = 1.):
        super().__init__(radius)
        self.scale = Rotation(scale)  # 长宽比

    def render(self, screen: pygame.Surface, position: Vector, rotation: Rotation):
        halfWidth = self.radius * self.scale.cos
        start = position - rotation.vector() * halfWidth
        end = position + rotation.vector() * halfWidth
        pygame.draw.line(screen, self.color, start.tuple(), end.tuple(), self.radius * self.scale.sin * 2.)

    def getCornerPosition(self, rotation: Rotation) -> (Vector, Vector, Vector, Vector):
        first = Rotation(rotation.angle() + self.scale.angle())
        rotation.cos = -rotation.cos
        second = Rotation(rotation.angle() + self.scale.angle())
        rotation.sin = -rotation.sin
        third = Rotation(rotation.angle() + self.scale.angle())
        rotation.cos = -rotation.cos
        fourth = Rotation(rotation.angle() + self.scale.angle())
        rotation.sin = -rotation.sin
        return first, second, third, fourth
'''
