import math
from typing import Tuple


class Vector:
    def __init__(self, x: float = 0., y: float = 0.):
        self.x: float = x
        self.y: float = y

    @staticmethod
    def parse(pos: Tuple[float, float]) -> 'Vector':
        return Vector(pos[0], pos[1])

    def __eq__(self, other: 'Vector') -> bool:
        return type(other) is Vector and self.x == other.x and self.y == other.y

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> 'Vector':
        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> 'Vector':
        return Vector(self.x / other, self.y / other)

    def __mod__(self, other: 'Vector') -> float:  # 其实是点乘
        return self.x * other.x + self.y * other.y

    def __pow__(self, other: 'Vector') -> float:  # 其实是叉乘
        return self.x * other.y - self.y * other.x

    def __str__(self) -> str:
        return "(%s, %s)" % (self.x, self.y)

    def tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    def magnitudeSqr(self) -> float:
        return self.x ** 2 + self.y ** 2

    def magnitude(self) -> float:
        return math.sqrt(self.magnitudeSqr())

    def normalize(self) -> 'Vector':
        return self / self.magnitude()

    def opposite(self) -> 'Vector':
        return Vector(-self.x, -self.y)

    def included(self, direction: 'Vector') -> float:  # 与另一向量间的夹角
        sm = self.magnitude()
        dm = direction.magnitude()
        if sm < 0.000001 or dm < 0.000001:
            return 0.
        return self % direction / (sm * dm)

    def decompose(self, other: 'Vector') -> 'Vector':
        return self - other

    def decomposeVertical(self, direction: 'Vector') -> Tuple['Vector', 'Vector']:
        cos = self.included(direction)
        direction = direction.normalize() * self.magnitude() * cos
        return direction, self.decompose(direction)

    def rotate(self, angle: float) -> 'Vector':
        cos = math.cos(angle)
        sin = math.sin(angle)
        return Vector(self.x * cos - self.y * sin, self.x * sin + self.y * cos)

    def overturn(self) -> 'Vector':
        return Vector(self.y, self.x)
