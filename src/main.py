import time
import sys
from world import World

from rigidbody import Rigidbody
from shape import *


class GameFrame:
    def __init__(self):
        pygame.init()
        self.__screen = pygame.display.set_mode((800, 600))
        self.__fpsTime = 1.0 / 60.0
        self.__background = (255, 255, 255)
        self.__world = World(50, (800, 600))
        self.__world.gravity.y = 10. * self.__fpsTime
        self.__clock = pygame.time.Clock()
        self.__lastUpdate = time.time()

    def __del__(self):
        pygame.quit()

    def update(self):
        if time.time() - self.__lastUpdate < self.__fpsTime:
            return
        self.__lastUpdate = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                l, _, r = pygame.mouse.get_pressed()
                if l:
                    self.__world.register(Rigidbody(1., Circle(10), Vector.parse(pygame.mouse.get_pos())))
                elif r:
                    rbody = Rigidbody(1.5, Polygon(15., [Vector(-1, 0), Vector(0, 1), Vector(1, 0), Vector(0, -1)]), Vector.parse(pygame.mouse.get_pos()))
                    rbody.angularVelocity = math.pi / 60
                    self.__world.register(rbody)
        self.__screen.fill(self.__background)
        self.__world.update(self.__screen)
        self.__world.render(self.__screen)
        pygame.display.update()
        self.__clock.tick()
        pygame.display.set_caption(
            "KirCute-Physics Demo fps: %s, len: %s" % (math.floor(self.__clock.get_fps()), len(self.__world.objs)))


if __name__ == "__main__":
    frame = GameFrame()
    while True:
        frame.update()
