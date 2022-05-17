import time
import sys
import abc
import math
import pygame
from world import World
from typing import Tuple, List


class GameFrame(metaclass=abc.ABCMeta):
    def __init__(self, frameSize: Tuple[int, int] = (800, 600), fps: float = 60.0, edgeWidth: int = 50):
        pygame.init()
        self._screen: pygame.Surface = pygame.display.set_mode(frameSize)
        self.__fpsTime: float = 1.0 / fps
        self._background: Tuple[int, int, int] = (255, 255, 255)
        self._world: World = World(edgeWidth, frameSize)
        self.__clock: pygame.time.Clock = pygame.time.Clock()
        self.__lastUpdate: float = time.time()

    def _init(self) -> None:
        pass

    def _exit(self) -> None:
        pass

    def _update(self, events: List[pygame.event.Event]) -> None:
        pass

    def __update(self) -> None:
        if time.time() - self.__lastUpdate < self.__fpsTime:
            return
        self.__lastUpdate = time.time()
        self.__clock.tick()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._exit()
                pygame.quit()
                sys.exit()
        self._screen.fill(self._background)
        self._update(events)
        del events
        self._world.update((self._screen.get_width(), self._screen.get_height()))
        self._world.render(self._screen)
        pygame.display.update()

    def setFPS(self, fps: float) -> None:
        self.__fpsTime = 1.0 / fps

    def getFPS(self) -> int:
        return math.floor(self.__clock.get_fps())

    def start(self) -> None:
        self._init()
        self.__lastUpdate = time.time()
        while True:
            self.__update()
