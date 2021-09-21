from pygame import Surface
from rigidbody import Rigidbody
from quadtree import Entrance


class World:
    def __init__(self, edgeWidth: int, windowRect: tuple):
        # self.objs = []
        self.objs = Entrance(edgeWidth, windowRect)
        self.forceField = []

    def register(self, rbody: Rigidbody):
        self.objs.append(rbody)

    def update(self, screen: tuple):
        """
        for obj in self.objs:
            obj.update()
        for i in range(len(self.objs)):
            for j in range(i + 1, len(self.objs)):
                contact.contactCheck(self.objs[i], self.objs[j])
            contact.solveEdge(self.objs[i], contact.meetEdge(screen, self.objs[i]))
        """
        self.objs.update(screen, self.forceField)

    def render(self, screen: Surface):
        """
        for obj in self.objs:
            obj.render(screen)
        """
        self.objs.render(screen)
