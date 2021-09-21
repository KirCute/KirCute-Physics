import random
from shape import *
from rigidbody import *
from frame import GameFrame


def generateRandomColor() -> tuple:
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


class VortexDemo(GameFrame):
    def _init(self):
        self.background = pygame.image.load('vortex_background.png').convert()
        self._world.forceField.append(lambda rbody: Vector(0., 1.) if rbody.position.x < 400 and rbody.position.y < 300 else Vector(0., 0.))
        self._world.forceField.append(lambda rbody: Vector(1., 0.) if rbody.position.x < 400 and rbody.position.y > 300 else Vector(0., 0.))
        self._world.forceField.append(lambda rbody: Vector(0., -1.) if rbody.position.x > 400 and rbody.position.y > 300 else Vector(0., 0.))
        self._world.forceField.append(lambda rbody: Vector(-1., 0.) if rbody.position.x > 400 and rbody.position.y < 300 else Vector(0., 0.))
        self._world.forceField.append(lambda rbody: rbody.linearVelocity.opposite() * .1 if rbody.linearVelocity.magnitudeSqr() > 100. else Vector(0., 0.))

    def _update(self, events: list):
        pygame.display.set_caption("KirCute-Physics Demo fps: %s, len: %s" % (self.getFPS(), len(self._world.objs)))
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                l, _, r = pygame.mouse.get_pressed()
                if l:
                    self._world.register(Rigidbody(1., Circle(10, generateRandomColor()), Vector.parse(pygame.mouse.get_pos())))
                elif r:
                    self._world.register(Rigidbody(2., Circle(14, generateRandomColor()), Vector.parse(pygame.mouse.get_pos())))
        self._screen.blit(self.background, (0, 0))


if __name__ == "__main__":
    VortexDemo().start()
