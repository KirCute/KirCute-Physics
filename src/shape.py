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
