import abc
import pygame
from common import *
from typing import Tuple, List


class Shape(metaclass=abc.ABCMeta):
    def __init__(self, radius: float, color: Tuple[int, int, int] = (127, 127, 127)):
        self.radius: float = radius
        self.color: Tuple[int, int, int] = color

    @abc.abstractmethod
    def render(self, screen: pygame.Surface, position: Vector, rotation: float) -> None:
        pass


class Circle(Shape):
    def render(self, screen: pygame.Surface, position: Vector, rotation: float) -> None:
        pygame.draw.circle(screen, self.color, position.tuple(), self.radius, 0)


class Polygon(Shape):
    @staticmethod
    def createRectangle(widthHalf: float, heightHalf: float,
                        color: Tuple[int, int, int] = (127, 127, 127)) -> 'Polygon':
        radiusSqr = widthHalf ** 2 + heightHalf ** 2
        points = [Vector(widthHalf, heightHalf), Vector(widthHalf, -heightHalf),
                  Vector(-widthHalf, -heightHalf), Vector(-widthHalf, heightHalf)]
        return Polygon(math.sqrt(radiusSqr), points, color)

    def __init__(self, radius: float, points: List[Vector], color: Tuple[int, int, int] = (127, 127, 127)):
        super().__init__(radius, color)
        self.pointsR: List[Vector] = []
        self.points: List[Vector] = []
        self.normals: List[Vector] = []
        for p in points:
            self.pointsR.append(p.overturn())
        self.pointsR.append(self.pointsR[0])
        for i in range(len(self.pointsR) - 1):
            self.points.append(self.pointsR[i])
            s = self.pointsR[i]
            e = self.pointsR[i + 1]
            direction = (e - s).rotate(math.pi / 2.)
            direction *= (direction % s)
            self.normals.append(direction.normalize())

    def render(self, screen: pygame.Surface, position: Vector, rotation: float) -> None:
        location = []
        for point in self.points:
            location.append((point.rotate(rotation) + position).tuple())
        pygame.draw.polygon(screen, self.color, location, 0)
