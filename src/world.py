from pygame import Surface
from rigidbody import Rigidbody
from quadtree import Root
from common import *


class World:
    def __init__(self, edgeWidth: int, windowRect: tuple):
        # self.objs = []
        self.objs = Root(edgeWidth, windowRect)
        self.gravity = Vector(0., 0.)

    def register(self, rbody: Rigidbody):
        self.objs.append(rbody)

    def update(self, screen: Surface):
        """
        for obj in self.objs:
            obj.update()
        for i in range(len(self.objs)):
            for j in range(i + 1, len(self.objs)):
                contact.contactCheck(self.objs[i], self.objs[j])
            contact.solveEdge(self.objs[i], contact.meetEdge(screen, self.objs[i]))
        """
        self.objs.update((screen.get_width(), screen.get_height()), self.gravity)

    def render(self, screen: Surface):
        """
        for obj in self.objs:
            obj.render(screen)
        """
        self.objs.render(screen)
