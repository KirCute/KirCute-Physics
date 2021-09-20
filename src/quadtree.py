import abc
import contact
from common import *
from rigidbody import Rigidbody
from pygame import Surface, draw

MaxLayer = 3
DivideCount = 5
DrawEdge = False


class Parent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def collide(self, rbody: Rigidbody):
        pass

    @abc.abstractmethod
    def insert(self, rbody: Rigidbody):
        pass


class NodeProxy(Parent):
    def __init__(self, parent: Parent, layer: int, start: tuple, end: tuple):
        self._node = Leaf(parent, self, layer, start, end)

    def __len__(self):
        return len(self._node)

    def rebuild(self, node):
        self._node = node

    def insert(self, rbody: Rigidbody):
        self._node.insert(rbody)

    def contains(self, rbody: Rigidbody) -> bool:
        return self._node.contains(rbody)

    def update(self, force: Vector):
        self._node.update(force)

    def render(self, screen: Surface):
        self._node.render(screen)

    def check(self):
        self._node.check()

    def collideCheck(self):
        self._node.collideCheck()

    def collide(self, rbody: Rigidbody):
        self._node.collide(rbody)

    def solveEdge(self, screen: Surface):
        self._node.solveEdge(screen)


class Root(Parent):
    def __init__(self, edgeWidth: int, windowRect: tuple):
        self._root = NodeProxy(self, 0, (-edgeWidth, -edgeWidth),
                               (windowRect[0] + edgeWidth, windowRect[1] + edgeWidth))

    def __len__(self):
        return len(self._root)

    def collide(self, rbody: Rigidbody):
        return  # 单次碰撞检测的终点

    def insert(self, rbody: Rigidbody):
        # 此处的rbody已经离开窗口，进行有关刚体删除的工作（其实等待gc就行）
        rbody.destroyed = True
        return

    def append(self, rbody: Rigidbody):  # World调用用来添加刚体
        self._root.insert(rbody)

    def update(self, screen: Surface, force: Vector):
        self._root.update(force)
        self._root.check()
        self._root.collideCheck()
        self._root.solveEdge(screen)

    def render(self, screen: Surface):
        self._root.render(screen)


class Node(metaclass=abc.ABCMeta):
    def __init__(self, parent: Parent, proxy: NodeProxy, layer: int, start: tuple, end: tuple):
        self._parent = parent
        self._proxy = proxy
        self._layer = layer
        self._start = start
        self._end = end
        self._storage = []

    def __len__(self):
        return len(self._storage)

    def insert(self, rbody: Rigidbody):
        self._storage.append(rbody)

    def contains(self, rbody: Rigidbody) -> bool:
        return rbody.position.x + rbody.shape.radius <= self._end[0] and \
               rbody.position.x - rbody.shape.radius >= self._start[0] and \
               rbody.position.y + rbody.shape.radius <= self._end[1] and \
               rbody.position.y - rbody.shape.radius >= self._start[1]

    def collideCheck(self):
        for i in range(len(self._storage)):
            for j in range(i + 1, len(self._storage)):
                contact.contactCheck(self._storage[i], self._storage[j])
        for obj in self._storage:
            self._parent.collide(obj)

    def collide(self, rbody):
        for obj in self._storage:
            contact.contactCheck(obj, rbody)
        self._parent.collide(rbody)

    def solveEdge(self, screen: Surface):
        for obj in self._storage:
            contact.solveEdge(screen, obj)

    def update(self, force: Vector):
        for rbody in self._storage:
            rbody.force += force * rbody.mass
            rbody.update()

    def render(self, screen: Surface):
        for rbody in self._storage:
            rbody.render(screen)

    def check(self):
        remove = 0
        for i in range(len(self._storage)):
            if self._storage[i - remove].destroyed or not self.contains(self._storage[i - remove]):
                self._parent.insert(self._storage[i - remove])
                self._storage.remove(self._storage[i - remove])
                remove += 1


class Branch(Node):
    def __init__(self, parent: Parent, proxy: NodeProxy, layer: int, start: tuple, end: tuple, storage: list):
        super().__init__(parent, proxy, layer, start, end)
        self._lu = NodeProxy(proxy, layer + 1, start, ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2))
        self._ru = NodeProxy(proxy, layer + 1, ((start[0] + end[0]) / 2, start[1]), (end[0], (start[1] + end[1]) / 2))
        self._ld = NodeProxy(proxy, layer + 1, (start[0], (start[1] + end[1]) / 2), ((start[0] + end[0]) / 2, end[1]))
        self._rd = NodeProxy(proxy, layer + 1, ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2), end)
        self._storage = storage

    def __len__(self):
        return super().__len__() + len(self._lu) + len(self._ru) + len(self._ld) + len(self._rd)

    def insert(self, rbody: Rigidbody):
        if DrawEdge:
            rbody.shape.color = (127, 127, 127)  # 染色
        super().insert(rbody)

    def update(self, force: Vector):
        super().update(force)
        self._lu.update(force)
        self._ru.update(force)
        self._ld.update(force)
        self._rd.update(force)

    def render(self, screen: Surface):
        super().render(screen)
        self._lu.render(screen)
        self._ru.render(screen)
        self._ld.render(screen)
        self._rd.render(screen)
        if DrawEdge:
            draw.line(screen, (0, 127, 0), ((self._start[0] + self._end[0]) / 2, self._start[1]),
                      ((self._start[0] + self._end[0]) / 2, self._end[1]), MaxLayer - self._layer)  # 画出四叉树边界
            draw.line(screen, (0, 127, 0), (self._start[0], (self._start[1] + self._end[1]) / 2),
                      (self._end[0], (self._start[1] + self._end[1]) / 2), MaxLayer - self._layer)  # 画出四叉树边界

    def collideCheck(self):
        self._lu.collideCheck()
        self._ru.collideCheck()
        self._ld.collideCheck()
        self._rd.collideCheck()
        super().collideCheck()

    def check(self):
        remove = 0
        for i in range(len(self._storage)):
            if self._lu.contains(self._storage[i - remove]):
                if DrawEdge:
                    self._storage[i - remove].shape.color = (255, 127, 127)  # 染色
                self._lu.insert(self._storage[i - remove])
                self._storage.remove(self._storage[i - remove])
                remove += 1
            elif self._ru.contains(self._storage[i - remove]):
                if DrawEdge:
                    self._storage[i - remove].shape.color = (127, 255, 127)  # 染色
                self._ru.insert(self._storage[i - remove])
                self._storage.remove(self._storage[i - remove])
                remove += 1
            elif self._ld.contains(self._storage[i - remove]):
                if DrawEdge:
                    self._storage[i - remove].shape.color = (127, 127, 255)  # 染色
                self._ld.insert(self._storage[i - remove])
                self._storage.remove(self._storage[i - remove])
                remove += 1
            elif self._rd.contains(self._storage[i - remove]):
                if DrawEdge:
                    self._storage[i - remove].shape.color = (255, 255, 127)  # 染色
                self._rd.insert(self._storage[i - remove])
                self._storage.remove(self._storage[i - remove])
                remove += 1
        self._lu.check()
        self._ru.check()
        self._ld.check()
        self._rd.check()
        super().check()

    def solveEdge(self, screen: Surface):
        super().solveEdge(screen)
        self._lu.solveEdge(screen)
        self._ru.solveEdge(screen)
        self._ld.solveEdge(screen)
        self._rd.solveEdge(screen)


class Leaf(Node):
    def check(self):
        if self._layer < MaxLayer and len(self._storage) > DivideCount:
            self._proxy.rebuild(Branch(self._parent, self._proxy, self._layer, self._start, self._end, self._storage))
            self._proxy.check()
        else:
            super().check()
