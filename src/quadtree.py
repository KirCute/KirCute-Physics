import abc
import contact
from rigidbody import Rigidbody
from pygame import Surface, draw
from typing import Tuple, List, Callable
from common import Vector

MaxLayer = 3
DivideCount = 5
DrawEdge = False


class Parent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def collide(self, rbody: Rigidbody) -> None:
        pass

    @abc.abstractmethod
    def insert(self, rbody: Rigidbody) -> None:
        pass


class NodeProxy(Parent):
    def __init__(self, parent: Parent, layer: int, start: Tuple[float, float], end: Tuple[float, float]):
        self._node: 'Node' = Leaf(parent, self, layer, start, end)

    def __len__(self) -> int:
        return len(self._node)

    def rebuild(self, node: 'Node') -> None:
        self._node = node

    def insert(self, rbody: Rigidbody) -> None:
        self._node.insert(rbody)

    def contains(self, rbody: Rigidbody) -> bool:
        return self._node.contains(rbody)

    def update(self, force: List[Callable[[Rigidbody], Vector]]) -> None:
        self._node.update(force)

    def render(self, screen: Surface) -> None:
        self._node.render(screen)

    def check(self) -> None:
        self._node.check()

    def collideCheck(self) -> None:
        self._node.collideCheck()

    def collide(self, rbody: Rigidbody) -> None:
        self._node.collide(rbody)

    def solveEdge(self, screen: Tuple[float, float]) -> None:
        self._node.solveEdge(screen)


class Entrance(Parent):
    def __init__(self, edgeWidth: int, windowRect: Tuple[float, float]):
        self._root: NodeProxy = NodeProxy(self, 0, (-edgeWidth, -edgeWidth),
                                          (windowRect[0] + edgeWidth, windowRect[1] + edgeWidth))

    def __len__(self) -> int:
        return len(self._root)

    def collide(self, rbody: Rigidbody) -> None:
        return  # 单次碰撞检测的终点

    def insert(self, rbody: Rigidbody) -> None:
        # 此处的rbody已经离开窗口，进行有关刚体删除的工作（其实等待gc就行）
        rbody.destroyed = True

    def append(self, rbody: Rigidbody) -> None:  # World调用用来添加刚体
        self._root.insert(rbody)

    def update(self, screen: Tuple[float, float], force: List[Callable[[Rigidbody], Vector]]) -> None:
        self._root.update(force)
        self._root.check()
        self._root.collideCheck()
        self._root.solveEdge(screen)

    def render(self, screen: Surface) -> None:
        self._root.render(screen)


class Node(metaclass=abc.ABCMeta):
    def __init__(self, parent: Parent, proxy: NodeProxy, layer: int,
                 start: Tuple[float, float], end: Tuple[float, float]):
        self._parent: Parent = parent
        self._proxy: NodeProxy = proxy
        self._layer: int = layer
        self._start: Tuple[float, float] = start
        self._end: Tuple[float, float] = end
        self._storage: List[Rigidbody] = []

    def __len__(self) -> int:
        return len(self._storage)

    def insert(self, rbody: Rigidbody) -> None:
        self._storage.append(rbody)

    def contains(self, rbody: Rigidbody) -> bool:
        return rbody.position.x + rbody.shape.radius <= self._end[0] and \
               rbody.position.x - rbody.shape.radius >= self._start[0] and \
               rbody.position.y + rbody.shape.radius <= self._end[1] and \
               rbody.position.y - rbody.shape.radius >= self._start[1]

    def collideCheck(self) -> None:
        for i in range(len(self._storage)):
            for j in range(i + 1, len(self._storage)):
                contact.contactCheck(self._storage[i], self._storage[j])
        for obj in self._storage:
            self._parent.collide(obj)

    def collide(self, rbody: Rigidbody) -> None:
        for obj in self._storage:
            contact.contactCheck(obj, rbody)
        self._parent.collide(rbody)

    def solveEdge(self, screen: Tuple[float, float]) -> None:
        for obj in self._storage:
            contact.solveEdge(screen, obj)

    def update(self, force: List[Callable[[Rigidbody], Vector]]) -> None:
        for rbody in self._storage:
            for f in force:
                rbody.force += f(rbody)
            rbody.update()

    def render(self, screen: Surface) -> None:
        for rbody in self._storage:
            rbody.render(screen)

    def check(self) -> None:
        remove = 0
        for i in range(len(self._storage)):
            if self._storage[i - remove].destroyed or not self.contains(self._storage[i - remove]):
                self._parent.insert(self._storage[i - remove])
                self._storage.remove(self._storage[i - remove])
                remove += 1


class Branch(Node):
    def __init__(self, parent: Parent, proxy: NodeProxy, layer: int,
                 start: Tuple[float, float], end: Tuple[float, float], storage: List[Rigidbody]):
        super().__init__(parent, proxy, layer, start, end)
        self._lu: NodeProxy = NodeProxy(proxy, layer + 1, start, ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2))
        self._ru: NodeProxy = NodeProxy(proxy, layer + 1, ((start[0] + end[0]) / 2, start[1]),
                                        (end[0], (start[1] + end[1]) / 2))
        self._ld: NodeProxy = NodeProxy(proxy, layer + 1, (start[0], (start[1] + end[1]) / 2),
                                        ((start[0] + end[0]) / 2, end[1]))
        self._rd: NodeProxy = NodeProxy(proxy, layer + 1, ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2), end)
        self._storage: List[Rigidbody] = storage

    def __len__(self) -> int:
        return super().__len__() + len(self._lu) + len(self._ru) + len(self._ld) + len(self._rd)

    def insert(self, rbody: Rigidbody) -> None:
        if DrawEdge:
            rbody.shape.color = (127, 127, 127)  # 染色
        super().insert(rbody)

    def update(self, force: List[Callable[[Rigidbody], Vector]]) -> None:
        super().update(force)
        self._lu.update(force)
        self._ru.update(force)
        self._ld.update(force)
        self._rd.update(force)

    def render(self, screen: Surface) -> None:
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

    def collideCheck(self) -> None:
        self._lu.collideCheck()
        self._ru.collideCheck()
        self._ld.collideCheck()
        self._rd.collideCheck()
        super().collideCheck()

    def check(self) -> None:
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

    def solveEdge(self, screen: Tuple[float, float]) -> None:
        super().solveEdge(screen)
        self._lu.solveEdge(screen)
        self._ru.solveEdge(screen)
        self._ld.solveEdge(screen)
        self._rd.solveEdge(screen)


class Leaf(Node):
    def check(self) -> None:
        if self._layer < MaxLayer and len(self._storage) > DivideCount:
            self._proxy.rebuild(Branch(self._parent, self._proxy, self._layer, self._start, self._end, self._storage))
            self._proxy.check()
        else:
            super().check()
