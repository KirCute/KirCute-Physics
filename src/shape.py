import abc
import pygame
from common import *


class Shape(metaclass=abc.ABCMeta):
    def __init__(self, radius: float, color: tuple = (127, 127, 127)):
        self.radius = radius
        self.color = color

    @abc.abstractmethod
    def render(self, screen: pygame.Surface, position: Vector, rotation: float):
        pass


class Circle(Shape):
    def render(self, screen: pygame.Surface, position: Vector, rotation: float):
        pygame.draw.circle(screen, self.color, position.tuple(), self.radius, 0)


class Polygon(Shape):
    @staticmethod
    def createRectangle(widthHalf: float, heightHalf: float, color: tuple = (127, 127, 127)):
        radiusSqr = widthHalf ** 2 + heightHalf ** 2
        points = [Vector(widthHalf, heightHalf), Vector(widthHalf, -heightHalf),
                  Vector(-widthHalf, -heightHalf), Vector(-widthHalf, heightHalf)]
        return Polygon(math.sqrt(radiusSqr), points, color)

    def __init__(self, radius: float, points: list, color: tuple = (127, 127, 127)):
        super().__init__(radius, color)
        self.pointsR = []
        for p in points:
            self.pointsR.append(p.overturn())
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
