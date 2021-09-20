import quadtree
from shape import *
from rigidbody import *
from frame import GameFrame


class QuadtreeDemo(GameFrame):
    def _init(self):
        quadtree.DrawEdge = True
        self.setGravity(10.)

    def _update(self, events: list):
        pygame.display.set_caption("KirCute-Physics Demo fps: %s, len: %s" % (self.getFPS(), len(self._world.objs)))
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                l, _, r = pygame.mouse.get_pressed()
                if l:
                    self._world.register(Rigidbody(1., Circle(10), Vector.parse(pygame.mouse.get_pos())))
                elif r:
                    self._world.register(
                        Rigidbody(1.5, Polygon.createRectangle(10, 10), Vector.parse(pygame.mouse.get_pos())))


if __name__ == "__main__":
    QuadtreeDemo().start()
