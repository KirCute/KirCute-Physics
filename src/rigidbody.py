import abc
from pygame import Surface, draw
from common import *


class Rigidbody:
    def __init__(self, invMass: float, s, pos: Vector, rotation: float = 0., elasticity: float = 1.):
        self.invMass = invMass
        self.invInertia = .1
        self.shape = s
        self.position = pos
        self.rotation = rotation
        self.elasticity = elasticity
        self.linearVelocity = Vector(0., 0.)
        self.angularVelocity = 0.
        self.force = Vector(0., 0.)

    def render(self, screen: Surface):
        self.shape.render(screen, self.position, self.rotation)

    def update(self):
        self.linearVelocity += self.force
        self.force.x = 0.
        self.force.y = 0.
        self.position += self.linearVelocity
        self.rotation += self.angularVelocity

    def impulse(self, position: Vector, value: Vector):
        if position.x == 0. and position.y == 0.:
            self.linearVelocity += value
        else:
            direction = position - self.position
            linear, angular = value.decomposeVertical(direction)
            self.linearVelocity += linear * self.invMass
            self.angularVelocity += math.sqrt(angular.magnitudeSqr() * direction.magnitudeSqr()) * self.invInertia

    def collideCheck(self, rbody):
        if not self.__broadPhase(rbody):
            return
        ret, impulse, shift, otherImpulse, otherShift = self.__narrowPhase(rbody)
        if ret:
            self.position += shift
            self.impulse(impulse[0], impulse[1])
            rbody.position += otherShift
            rbody.impulse(otherImpulse[0], otherImpulse[1])

    def __broadPhase(self, rbody) -> bool:
        return (self.shape.radius + rbody.shape.radius) ** 2 >= (self.position - rbody.position).magnitudeSqr()

    def __narrowPhase(self, rbody) -> (bool, (Vector, Vector), Vector, (Vector, Vector), Vector):
        return self.shape.collide(self, rbody)

    def checkEdge(self, screen: tuple):
        ret, impulse, shift = self.shape.edgeCollide(screen, self)
        if ret:
            self.position += shift
            self.impulse(impulse[0], impulse[1])


class Shape(metaclass=abc.ABCMeta):
    def __init__(self, radius: float):
        self.radius = radius
        self.color = (127, 127, 127)

    @abc.abstractmethod
    def render(self, screen: Surface, position: Vector, rotation: float):
        pass

    @abc.abstractmethod
    def collide(self, rbody: Rigidbody, other: Rigidbody) -> (bool, (Vector, Vector), Vector, (Vector, Vector), Vector):
        pass  # TODO

    @abc.abstractmethod
    def edgeCollide(self, screen: tuple, rbody: Rigidbody) -> (bool, (Vector, Vector), Vector):
        pass  # TODO


class Circle(Shape):
    def render(self, screen: Surface, position: Vector, rotation: float):
        draw.circle(screen, self.color, position.tuple(), self.radius, 0)

    def collide(self, rbody: Rigidbody, other: Rigidbody) -> (bool, (Vector, Vector), Vector, (Vector, Vector), Vector):
        if type(other.shape) == Circle:
            impactPos = (rbody.position - other.position) / 2.
            if impactPos.magnitudeSqr() == 0.:
                return False, None, None, None, None
            vls, _ = rbody.linearVelocity.decomposeVertical(impactPos)
            vlo, _ = other.linearVelocity.decomposeVertical(impactPos)
            vr = (vls - vlo) / (rbody.invMass + other.invMass)
            shift = impactPos.normalize() * ((rbody.shape.radius + other.shape.radius) / 2.) - impactPos
            return True, (impactPos, vr.opposite()), shift.opposite(), (impactPos.opposite(), vr), shift
        elif type(other.shape) == Polygon:
            maxL = 0.
            direction = other.position - rbody.position
            for i in range(len(other.shape.pointsR) - 1):
                maxL = max(maxL, (other.shape.pointsR[i].rotate(other.rotation) + direction) %
                           other.shape.normals[i].rotate(other.rotation))
            for i in range(1, len(other.shape.pointsR)):
                maxL = max(maxL, (other.shape.pointsR[i].rotate(other.rotation) + direction) %
                           other.shape.normals[i - 1].rotate(other.rotation))
            if maxL > rbody.shape.radius + other.shape.radius:
                return False, None, None, None, None
            del maxL
            minAngle = 0.
            impactDirection = None
            for normal in other.shape.normals:
                angle = direction.included(normal)
                if minAngle > angle:
                    minAngle = angle
                    impactDirection = normal
            del minAngle
            minDot = rbody.shape.radius
            for p in other.shape.points:
                dot = (p.rotate(other.rotation) - direction) % impactDirection
                minDot = min(minDot, -dot)
            impactPos = (rbody.position - impactDirection).normalize() * minDot
            impactPosForPolygon = impactPos - direction
            vls, _ = rbody.linearVelocity.decomposeVertical(impactPos)
            vlo, _ = other.linearVelocity.decomposeVertical(impactPos) + rbody.angularVelocity * impactPosForPolygon
            vr = (vls - vlo) / (rbody.invMass + other.invMass)
            shift = (rbody.position - impactDirection) - impactPos
            return True, (impactPos, vr.opposite), shift.opposite(), (impactPosForPolygon, vr), shift

    def edgeCollide(self, screen: tuple, rbody: Rigidbody) -> (bool, (Vector, Vector), Vector):
        if rbody.position.y - self.radius <= 0.:
            return True, (rbody.position, Vector(0., -rbody.linearVelocity.y * 2. / rbody.invMass)), Vector(0.,
                                                                                                            self.radius - rbody.position.y)
        elif rbody.position.y + self.radius >= screen[1]:
            return True, (rbody.position, Vector(0., -rbody.linearVelocity.y * 2. / rbody.invMass)), Vector(0., screen[
                1] - rbody.position.y - self.radius)
        elif rbody.position.x - self.radius <= 0.:
            return True, (rbody.position, Vector(-rbody.linearVelocity.x * 2. / rbody.invMass, 0.)), Vector(
                self.radius - rbody.position.x, 0.)
        elif rbody.position.x + self.radius >= screen[0]:
            return True, (rbody.position, Vector(-rbody.linearVelocity.y * 2. / rbody.invMass, 0.)), Vector(0., screen[
                0] - rbody.position.x - self.radius)
        else:
            return False, None, None


class Polygon(Shape):
    def __init__(self, halfL: float, points: list):
        super().__init__(halfL * math.sqrt(2))
        self.pointsR = []
        for p in points:
            self.pointsR.append(p * halfL)
        self.pointsR.append(self.pointsR[0])
        self.points = []
        self.normals = []
        for i in range(len(self.pointsR) - 1):
            self.points.append(self.pointsR[i])
            s = self.pointsR[i]
            e = self.pointsR[i + 1]
            direction = (e - s).rotate(math.pi / 2.)
            direction *= (direction % s)
            self.normals.append(direction.normalize())

    def render(self, screen: Surface, position: Vector, rotation: float):
        location = []
        for point in self.points:
            location.append((point.rotate(rotation) + position).tuple())
        draw.polygon(screen, self.color, location, 0)

    def collide(self, rbody: Rigidbody, other: Rigidbody) -> (bool, (Vector, Vector), Vector, (Vector, Vector), Vector):
        if type(other.shape) == Circle:
            ret, o, os, s, ss = other.shape.collide(other, rbody)
            return ret, s, ss, o, os
        elif type(other.shape) == Polygon:
            return False, None, None, None, None  # TODO

    def edgeCollide(self, screen: tuple, rbody: Rigidbody) -> (bool, (Vector, Vector), Vector):
        return False, None, None
