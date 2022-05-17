import quadtree
import random
from shape import *
from rigidbody import *
from frame import GameFrame


class QuadtreeDemo(GameFrame):
    def _init(self) -> None:
        quadtree.DrawEdge = True
        self._world.forceField.append(lambda rbody: Vector(0., 10. * rbody.mass / self.getFPS()))

    def _update(self, events: List[pygame.event.Event]) -> None:
        pygame.display.set_caption("KirCute-Physics Demo fps: %s, len: %s" % (self.getFPS(), len(self._world.objs)))
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                l, _, r = pygame.mouse.get_pressed()
                if l:
                    size = random.randint(5, 15)
                    self._world.register(Rigidbody(size / 10., Circle(size), Vector.parse(pygame.mouse.get_pos())))
                elif r:
                    self._world.register(
                        Rigidbody(1.5, Polygon.createRectangle(10, 10), Vector.parse(pygame.mouse.get_pos())))


if __name__ == "__main__":
    QuadtreeDemo().start()
