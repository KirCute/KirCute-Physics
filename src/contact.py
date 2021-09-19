from rigidbody import *
from shape import *
from pygame import Surface

"""
注意：以下代码十分瞎眼
本来是因为发生碰撞的两个物体种类不同所以把处理碰撞单独放在这里
后来边界判定等可以OOP的代码也放在这里导致这个文件看起来十分不OOP
然后我懒得重构了
"""

EdgeElasticity = 1.
ignoreList = []


def contactCheck(rbodyA: Rigidbody, rbodyB: Rigidbody):
    if isIgnored(rbodyA, rbodyB):
        if not inContact(rbodyA, rbodyB):
            recheck(rbodyA, rbodyB)
    else:
        if inContact(rbodyA, rbodyB):
            solve(rbodyA, rbodyB)


def isIgnored(rbodyA: Rigidbody, rbodyB: Rigidbody) -> bool:
    return (rbodyA, rbodyB) in ignoreList or (rbodyB, rbodyA) in ignoreList


def recheck(rbodyA: Rigidbody, rbodyB: Rigidbody):
    if (rbodyA, rbodyB) in ignoreList:
        ignoreList.remove((rbodyA, rbodyB))
    if (rbodyB, rbodyA) in ignoreList:
        ignoreList.remove((rbodyB, rbodyA))


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
    return maxL <= circle.shape.radius + polygon.shape.radius


def inContactPolygonWithPolygon(polygonA: Rigidbody, polygonB: Rigidbody) -> bool:
    return False  # TODO


def solveEdge(screen: Surface, rbody: Rigidbody):
    if type(rbody.shape) is Circle:
        solveEdgeCircle(screen, rbody)
    elif type(rbody.shape) is Polygon:
        solveEdgePolygon(screen, rbody)


def solveEdgeCircle(screen: Surface, rbody: Rigidbody):
    if rbody.position.y - rbody.shape.radius <= 0. or rbody.position.y + rbody.shape.radius >= screen.get_height():
        rbody.linearVelocity.y = -rbody.linearVelocity.y * EdgeElasticity
    elif rbody.position.x - rbody.shape.radius <= 0. or rbody.position.x + rbody.shape.radius >= screen.get_width():
        rbody.linearVelocity.x = -rbody.linearVelocity.x * EdgeElasticity


def solveEdgePolygon(screen: Surface, rbody: Rigidbody):
    if rbody.position.y + rbody.shape.radius < screen.get_height() and \
            rbody.position.y - rbody.shape.radius > 0. and \
            rbody.position.x - rbody.shape.radius > 0. and \
            rbody.position.x + rbody.shape.radius < screen.get_width():
        return
    for p in rbody.shape.points:
        point = p.rotate(rbody.rotation) + rbody.position
        if point.y < 0. or point.y > screen.get_height():
            rbody.linearVelocity.y = -rbody.linearVelocity.y * EdgeElasticity
            rbody.angularVelocity = -rbody.angularVelocity
            break
        elif point.x < 0. or point.x > screen.get_width():
            rbody.linearVelocity.x = -rbody.linearVelocity.x * EdgeElasticity
            rbody.angularVelocity = -rbody.angularVelocity
            break


def solve(rbodyA: Rigidbody, rbodyB: Rigidbody):
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


def solveCircleWithCircle(circleA: Rigidbody, circleB: Rigidbody):
    direction = circleA.position - circleB.position
    if direction.magnitudeSqr() == 0.:
        return
    ovdirA, keepA = circleA.linearVelocity.decomposeVertical(direction)
    ovdirB, keepB = circleB.linearVelocity.decomposeVertical(direction)
    vdirA = (ovdirA * (circleA.mass - circleB.mass) + ovdirB * 2. * circleB.mass) / (circleA.mass + circleB.mass)
    vdirB = (ovdirB * (circleB.mass - circleA.mass) + ovdirA * 2. * circleA.mass) / (circleA.mass + circleB.mass)
    circleA.linearVelocity = keepA + vdirA * circleB.elasticity
    circleB.linearVelocity = keepB + vdirB * circleA.elasticity
    ignoreList.append((circleA, circleB))


def solveCircleWithPolygon(circle: Rigidbody, polygon: Rigidbody):
    minSqr = circle.shape.radius ** 2
    closestPoint = None
    for p in polygon.points:
        point = p.rotate(polygon.rotation) + polygon.position
        distance = (point - circle.position).magnitudeSqr()
        if distance < minSqr:
            minSqr = distance
            closestPoint = point
    # TODO


def solvePolygonWithPolygon(polygonA: Rigidbody, polygonB: Rigidbody):
    return  # TODO
