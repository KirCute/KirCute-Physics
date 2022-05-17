import contact
from shape import *
from rigidbody import *
from frame import GameFrame


class PolygonDemo(GameFrame):
    def _init(self) -> None:
        contact.DebugCircleWithPolygon = True
        polygon = Rigidbody(2., Polygon(50, [Vector(0., 50.), Vector(50., 0.), Vector(0., -50.), Vector(-50., 0.)]), Vector(400, 300))
        polygon.angularVelocity = .01
        self._world.register(polygon)

    def _update(self, events: List[pygame.event.Event]) -> None:
        pygame.display.set_caption("KirCute-Physics Demo fps: %s, len: %s" % (self.getFPS(), len(self._world.objs)))
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                l, _, _ = pygame.mouse.get_pressed()
                if l:
                    self._world.register(Rigidbody(1., Circle(10), Vector.parse(pygame.mouse.get_pos())))


if __name__ == "__main__":
    PolygonDemo().start()
