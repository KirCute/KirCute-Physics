import random
from shape import *
from rigidbody import *
from frame import GameFrame


def generateRandomColor() -> tuple:
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


class FloatDemo(GameFrame):
    def _update(self, events: list):
        pygame.display.set_caption("KirCute-Physics Demo fps: %s, len: %s" % (self.getFPS(), len(self._world.objs)))
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                l, _, r = pygame.mouse.get_pressed()
                if l:
                    rbody = Rigidbody(1., Circle(10, generateRandomColor()), Vector.parse(pygame.mouse.get_pos()))
                    rbody.linearVelocity = Vector(random.randint(-500, 500), random.randint(-500, 500)) / 1000.
                    self._world.register(rbody)
                elif r:
                    rbody = Rigidbody(2., Polygon.createRectangle(20, 20, generateRandomColor()),
                                      Vector.parse(pygame.mouse.get_pos()))
                    rbody.angularVelocity += .02
                    rbody.linearVelocity = Vector(random.randint(-500, 500), random.randint(-500, 500)) / 1000.
                    self._world.register(rbody)


if __name__ == "__main__":
    FloatDemo().start()
