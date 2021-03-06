from rigidbody import *
from shape import *
from typing import Tuple
import time

EdgeElasticity = 1.
RotateElasticity = .5
checkEdgeSide = [True, True, True, True]

DebugCircleWithPolygon = False


def contactCheck(rbodyA: Rigidbody, rbodyB: Rigidbody) -> None:
    if inContact(rbodyA, rbodyB):
        solve(rbodyA, rbodyB)


def inContact(rbodyA: Rigidbody, rbodyB: Rigidbody) -> bool:
    if not isBoxInContact(rbodyA, rbodyB):
        return False
    if type(rbodyA.shape) is Circle:
        if type(rbodyB.shape) is Circle:
            return inContactCircleWithCircle(rbodyA, rbodyB)
        elif type(rbodyB.shape) is Polygon:
            return inContactCircleWithPolygon(rbodyA, rbodyB)
    elif type(rbodyA.shape) is Polygon:
        if type(rbodyB.shape) is Circle:
            return inContactCircleWithPolygon(rbodyB, rbodyA)
        elif type(rbodyB.shape) is Polygon:
            return inContactPolygonWithPolygon(rbodyA, rbodyB)
    return False


def isBoxInContact(rbodyA: Rigidbody, rbodyB: Rigidbody) -> bool:
    return (rbodyA.shape.radius + rbodyB.shape.radius) ** 2 >= (rbodyA.position - rbodyB.position).magnitudeSqr()


def inContactCircleWithCircle(circleA: Rigidbody, circleB: Rigidbody) -> bool:
    return True  # 同isBoxInContact，前者已经判断过


def inContactCircleWithPolygon(circle: Rigidbody, polygon: Rigidbody) -> bool:
    maxL = 0.
    for i in range(len(polygon.shape.pointsR) - 1):
        maxL = max(maxL, (polygon.shape.pointsR[i].rotate(polygon.rotation) + polygon.position - circle.position) %
                   polygon.shape.normals[i].rotate(polygon.rotation))
    for i in range(1, len(polygon.shape.pointsR)):
        maxL = max(maxL, (polygon.shape.pointsR[i].rotate(polygon.rotation) + polygon.position - circle.position) %
                   polygon.shape.normals[i - 1].rotate(polygon.rotation))
    return maxL <= circle.shape.radius * 3. + polygon.shape.radius


def inContactPolygonWithPolygon(polygonA: Rigidbody, polygonB: Rigidbody) -> bool:
    for polygon in (polygonA, polygonB):
        for axis in polygon.shape.normals:
            b2a = (polygonA.position - polygonB.position) % axis.rotate(polygonA.rotation)
            leftA, rightA = getPolygonProjectionWithAxis(polygonA, axis)
            leftB, rightB = getPolygonProjectionWithAxis(polygonB, axis)
            if not ((leftA < leftB + b2a < rightA) or (leftA < rightB + b2a < rightA)):
                return False
    return True


def solveEdge(screen: Tuple[float, float], rbody: Rigidbody) -> None:
    if type(rbody.shape) is Circle:
        solveEdgeCircle(screen, rbody)
    elif type(rbody.shape) is Polygon:
        solveEdgePolygon(screen, rbody)


def solveEdgeCircle(screen: Tuple[float, float], rbody: Rigidbody) -> None:
    if checkEdgeSide[0] and rbody.position.y - rbody.shape.radius <= 0.:
        rbody.position.y = rbody.shape.radius
        rbody.linearVelocity.y = -rbody.linearVelocity.y * EdgeElasticity
    if checkEdgeSide[1] and rbody.position.y + rbody.shape.radius >= screen[1]:
        rbody.position.y = screen[1] - rbody.shape.radius
        rbody.linearVelocity.y = -rbody.linearVelocity.y * EdgeElasticity
    if checkEdgeSide[2] and rbody.position.x - rbody.shape.radius <= 0.:
        rbody.position.x = rbody.shape.radius
        rbody.linearVelocity.x = -rbody.linearVelocity.x * EdgeElasticity
    if checkEdgeSide[3] and rbody.position.x + rbody.shape.radius >= screen[0]:
        rbody.position.x = screen[0] - rbody.shape.radius
        rbody.linearVelocity.x = -rbody.linearVelocity.x * EdgeElasticity


def solveEdgePolygon(screen: Tuple[float, float], rbody: Rigidbody) -> None:
    if rbody.position.y + rbody.shape.radius < screen[1] and \
            rbody.position.y - rbody.shape.radius > 0. and \
            rbody.position.x - rbody.shape.radius > 0. and \
            rbody.position.x + rbody.shape.radius < screen[0]:
        return
    for p in rbody.shape.points:
        point = p.rotate(rbody.rotation) + rbody.position
        if checkEdgeSide[0] and point.y < 0.:
            rbody.position.y = rbody.shape.radius
            rbody.linearVelocity.y = -rbody.linearVelocity.y * EdgeElasticity
            rbody.angularVelocity = -rbody.angularVelocity * RotateElasticity
        if checkEdgeSide[1] and point.y > screen[1]:
            rbody.position.y = screen[1] - rbody.shape.radius
            rbody.linearVelocity.y = -rbody.linearVelocity.y * EdgeElasticity
            rbody.angularVelocity = -rbody.angularVelocity * RotateElasticity
        if checkEdgeSide[2] and point.x < 0.:
            rbody.position.x = rbody.shape.radius
            rbody.linearVelocity.x = -rbody.linearVelocity.x * EdgeElasticity
            rbody.angularVelocity = -rbody.angularVelocity * RotateElasticity
        if checkEdgeSide[3] and point.x > screen[0]:
            rbody.position.x = screen[0] - rbody.shape.radius
            rbody.linearVelocity.x = -rbody.linearVelocity.x * EdgeElasticity
            rbody.angularVelocity = -rbody.angularVelocity * RotateElasticity


def solve(rbodyA: Rigidbody, rbodyB: Rigidbody) -> None:
    if type(rbodyA.shape) is Circle:
        if type(rbodyB.shape) is Circle:
            solveCircleWithCircle(rbodyA, rbodyB)
        elif type(rbodyB.shape) is Polygon:
            solveCircleWithPolygon(rbodyA, rbodyB)
    elif type(rbodyA.shape) is Polygon:
        if type(rbodyB.shape) is Circle:
            solveCircleWithPolygon(rbodyB, rbodyA)
        elif type(rbodyB.shape) is Polygon:
            solvePolygonWithPolygon(rbodyA, rbodyB)
    for trigger in rbodyA.triggers:
        trigger(rbodyA, rbodyB)
    for trigger in rbodyB.triggers:
        trigger(rbodyB, rbodyA)


def simpleImpact(rbodyA: Rigidbody, rbodyB: Rigidbody, direction: Vector) -> None:
    ovdirA, keepA = rbodyA.linearVelocity.decomposeVertical(direction)
    ovdirB, keepB = rbodyB.linearVelocity.decomposeVertical(direction)
    vdirA = (ovdirA * (rbodyA.mass - rbodyB.mass) + ovdirB * 2. * rbodyB.mass) / (rbodyA.mass + rbodyB.mass)
    vdirB = (ovdirB * (rbodyB.mass - rbodyA.mass) + ovdirA * 2. * rbodyA.mass) / (rbodyA.mass + rbodyB.mass)
    rbodyA.linearVelocity = keepA + vdirA * rbodyB.elasticity
    rbodyB.linearVelocity = keepB + vdirB * rbodyA.elasticity


def moveAway(rbodyA: Rigidbody, rbodyB: Rigidbody) -> None:
    direction = rbodyA.position - rbodyB.position
    magnitude = (rbodyA.shape.radius + rbodyB.shape.radius - direction.magnitude()) / 4. + .01
    normalize = direction.normalize() * magnitude
    rbodyA.position += normalize
    rbodyB.position -= normalize


def solveCircleWithCircle(circleA: Rigidbody, circleB: Rigidbody) -> None:
    direction = circleA.position - circleB.position
    if direction.magnitudeSqr() == 0.:
        return
    simpleImpact(circleA, circleB, direction)
    moveAway(circleA, circleB)


def getEdgeImpactDirection(rbody: Rigidbody, polygon: Rigidbody) -> Tuple[Vector, float]:
    originDirection = polygon.position - rbody.position
    minAngle = 2.
    minEdge = None
    for normal in polygon.shape.normals:
        angle = math.acos(originDirection.included(normal))
        if minAngle > angle:
            minAngle = angle
            minEdge = normal
    return minEdge, minAngle


def solveCircleWithPolygon(circle: Rigidbody, polygon: Rigidbody) -> None:
    if DebugCircleWithPolygon:
        print(time.time())
        return
    direction, angle = getEdgeImpactDirection(circle, polygon)
    polygon.angularVelocity += angle * circle.mass / polygon.mass
    polygon.angularVelocity *= RotateElasticity
    simpleImpact(circle, polygon, direction)
    moveAway(circle, polygon)


def solvePolygonWithPolygon(polygonA: Rigidbody, polygonB: Rigidbody) -> None:
    directionB, angleB = getEdgeImpactDirection(polygonA, polygonB)
    directionA, angleA = getEdgeImpactDirection(polygonB, polygonA)
    polygonA.angularVelocity += angleA * polygonB.mass / polygonA.mass
    polygonA.angularVelocity *= RotateElasticity
    polygonB.angularVelocity += angleB * polygonA.mass / polygonB.mass
    polygonB.angularVelocity *= RotateElasticity
    simpleImpact(polygonA, polygonB, directionA - directionB)
    moveAway(polygonA, polygonB)


def getPolygonProjectionWithAxis(polygon: Rigidbody, axis: Vector) -> Tuple[float, float]:
    minD = 0.
    maxD = 0.
    for point in polygon.shape.points:
        num = point.rotate(polygon.rotation) % axis.rotate(polygon.rotation)
        minD = min(minD, num)
        maxD = max(maxD, num)
    return minD, maxD
