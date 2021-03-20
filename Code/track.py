from enum import Enum, IntEnum, auto
from typing import Tuple, List
import math
import matplotlib.pyplot as plt
import numpy as np


class Angle(IntEnum):
    Degree0 = 0
    # Degree45 = 45
    Degree90 = 90
    # Degree135 = 135
    Degree180 = 180
    # Degree225 = 225
    Degree270 = 270
    # Degree315 = 315

    @classmethod
    def rotate(self, enterAngle, rotation):
        return Angle((enterAngle.value + rotation) % 360)

    # Clockwise (NOTE: NOT COUNTERCLOCKWISE) Sine and Cosine Functions, Integer Dicts to Prevent Radian Rounding Errors
    @classmethod
    def csin(self, angle):
        csinDeg = {
            Angle.Degree0: 0,
            Angle.Degree90: -1,
            Angle.Degree180: 0,
            Angle.Degree270: 1
        }
        return csinDeg[angle]

    @classmethod
    def ccos(self, angle):
        ccosDeg = {
            Angle.Degree0: 1,
            Angle.Degree90: 0,
            Angle.Degree180: -1,
            Angle.Degree270: 0
        }
        return ccosDeg[angle]


class Curve(Enum):
    Straight = 0
    Left = -1
    Right = 1
    @classmethod
    def fromRoll(self, roll):
        roll2Curve = {
            Roll.Left: Curve.Left,
            Roll.Right: Curve.Right
        }
        return roll2Curve[roll]


class Roll(IntEnum):
    Level = 0
    Left = - 1
    Right = 1


class Slope(IntEnum):
    Level = 0
    Down = -1
    Up = 1


class Piece(Enum):
    Straight = auto()
    SmallCurve = auto()
    RegularCurve = auto()
    # LargeCurve = auto()
    StationPlatform = auto()
    SBend = auto()
    # HelixSmall = auto()
    # HelixLarge = auto()
    # Brakes = auto()
    # Booster = auto()


TrackPiece = Tuple[Piece, Curve, Slope, Roll]
# X, Y, Z
# Positive X -> Right, Positive Y -> Up, Positive Z -> Out of Page
Position = Tuple[int, int, int]
# TrackPosition, Track Rotation Angle, Track Slope, Track Roll
TrackState = Tuple[Position, Angle, Slope, Roll]
# Rotation Angle 0  deg -> Point to positive X, Right-Hand Rotation Positive


def calculateExitState(track: TrackPiece, enterState: TrackState):
    piece, pieceCurve, pieceSlope, pieceRoll = track
    enterPosition, enterRotation, enterSlope, enterRoll = enterState
    enterX, enterY, enterZ = enterPosition

    # Assumes Right-Hand Curve
    pieceExitDeltaXZR = {
        Piece.Straight: (1, 0, 0),
        Piece.SmallCurve: (1, 2, 90),
        Piece.RegularCurve: (2, 3, 90),
        Piece.StationPlatform: (1, 0, 0),
        Piece.SBend: (3, 1, 0),
        # Piece.HelixSmall: (-1, 3, 180),
        # Piece.HelixLarge: (-1, 5, 180)
        # Piece.Brakes: (1, 0, 0),
    }
    pieceExitDeltaY = {
        Piece.StationPlatform: 0,
        Piece.Straight: 1,
        Piece.SmallCurve: 2,
        Piece.RegularCurve: 4,
        # Piece.HelixSmall: 1,
        # Piece.HelixLarge: 1
        # Piece.Brakes: 0,
    }

    deltaX, deltaZ, deltaRotation = pieceExitDeltaXZR[piece]
    # Account for Left-Hand Curve
    deltaZ = deltaZ * pieceCurve.value
    deltaRotation = deltaRotation * pieceCurve.value
    # Account for Rotation
    exitRotation = Angle.rotate(enterRotation, deltaRotation)
    sinRotate = Angle.csin(enterRotation)
    cosRotate = Angle.ccos(enterRotation)
    deltaX, deltaZ = cosRotate * deltaX + sinRotate * \
        deltaZ, (-sinRotate) * deltaX + cosRotate * deltaZ
    deltaY = pieceExitDeltaY[piece] * pieceSlope.value

    exitX = enterX + deltaX
    exitY = enterY + deltaY
    exitZ = enterZ + deltaZ
    exitPosition = (exitX, exitY, exitZ)

    exitSlope = pieceSlope
    exitRoll = pieceRoll
    exitState = (exitPosition, exitRotation, exitSlope, exitRoll)
    return exitState


def generatePossibleTracks(enterState: TrackState) -> List[TrackPiece]:
    enterPosition, enterRotation, enterSlope, enterRoll = enterState
    possibleTracks = []
    if enterSlope == Slope.Level and enterRoll == Roll.Level:
        # Add Tracks that Begin a Slope
        beginSlope = [(Piece.Straight, Curve.Straight, slope, Roll.Level)
                      for slope in [Slope.Down, Slope.Up]]
        possibleTracks.extend(beginSlope)
        # Add Tracks that Begin a Roll
        beginRoll = [(Piece.Straight, Curve.fromRoll(roll), Slope.Level, roll)
                     for roll in [Roll.Left, Roll.Right]]
        possibleTracks.extend(beginRoll)
        # Add Tracks that Match Level Slope / Roll
        matchSlopeRollCurve = [(piece, curve, Slope.Level, Roll.Level) for piece in [
            Piece.SmallCurve, Piece.RegularCurve] for curve in [Curve.Left, Curve.Right]]
        possibleTracks.extend(matchSlopeRollCurve)
        matchSlopeRollStraight = (
            Piece.Straight, Curve.Straight, Slope.Level, Roll.Level)
        possibleTracks.append(matchSlopeRollStraight)
    elif enterSlope != Slope.Level:
        # Add Tracks that Match Current Slope
        matchSlopeCurve = [(piece, curve, enterSlope, Roll.Level) for piece in [
            Piece.SmallCurve, Piece.RegularCurve] for curve in [Curve.Left, Curve.Right]]
        matchSlopeStraight = (
            Piece.Straight, Curve.Straight, enterSlope, Roll.Level)
        possibleTracks.extend(matchSlopeCurve)
        possibleTracks.append(matchSlopeStraight)
        # Add Tracks that Level Out Slope
        levelSlope = [(Piece.Straight, Curve.Straight, Slope.Level, roll)
                      for roll in [Roll.Level, Roll.Left, Roll.Right]]
        possibleTracks.extend(levelSlope)
    elif enterRoll != Roll.Level:
        # Add Tracks that Match Current Roll
        matchRollCurve = [(piece, Curve.fromRoll(enterRoll), Slope.Level, enterRoll)
                          for piece in [Piece.SmallCurve, Piece.RegularCurve]]
        matchRollStraight = (Piece.Straight, Curve.Straight,
                             Slope.Level, enterRoll)
        possibleTracks.extend(matchRollCurve)
        possibleTracks.append(matchRollStraight)
        # Add Tracks that Level out Roll
        levelRoll = [(Piece.Straight, Curve.Straight, slope, Roll.Level)
                     for slope in [Slope.Level, Slope.Down, Slope.Up]]
        possibleTracks.extend(levelRoll)
    return possibleTracks


# goalPosition = (0, 0, 0)
# goalState = (goalPosition, Angle.Degree0, Slope.Level, Roll.Level)

def manhattanPositionHeuristic(statePosition: Position, goalPosition: Position):
    stateX, stateY, stateZ = statePosition
    goalX, goalY, goalZ = goalPosition
    deltaX = abs(stateX - goalX) * 10.5
    deltaY = abs(stateY - goalY) * 5
    deltaZ = abs(stateZ - goalZ) * 10.5
    return deltaX + deltaY + deltaZ


def manhattanCostHeuristic(statePosition: Position, goalPosition: Position):
    stateX, stateY, stateZ = statePosition
    goalX, goalY, goalZ = goalPosition
    deltaX = abs(stateX - goalX)
    deltaY = abs(stateY - goalY)
    deltaZ = abs(stateZ - goalZ)
    return (deltaX + deltaY + deltaZ) * 22


def manhattanStateHeuristic(state, goalState):
    statePosition, stateAngle, stateSlope, stateRoll = state
    goalPosition, goalAngle, goalSlope, goalRoll = goalState
    return manhattanPositionHeuristic(statePosition, goalPosition)

# Testing Function - Filters out Possible Tracks to 2D X and Z - Also removes Roll


def flatFilter(track):
    piece, curve, slope, roll = track
    if slope == Slope.Level and roll == Roll.Level:
        return True
    else:
        return False


def validateTrack(startState, currentState, currentPath, track):
    validations = [validateHeight, validateCollision]
    for v in validations:
        if not v(startState, currentState, currentPath, track):
            return False
    return True


def validateHeight(startState, currentState, currentPath, track):
    futureState = simulateTrackSequence(currentState, [track])
    futurePosition, futureAngle, futureSlope, futureRoll = futureState
    futureX, futureY, futureZ = futurePosition
    if (futureY >= 0 and futureY <= 11):
        return True
    return False

# Offsets Collisions to expand bounding box


def generateOffsetColliders(collider):
    newcollider = []
    for pos in collider:
        x, y, z = pos
        newcollider.append((x, y, z))
        newcollider.append((x, y + 1, z))
        newcollider.append((x, y - 1, z))
    return newcollider


pieceLevelSlopeColliders = {
    Piece.Straight: generateOffsetColliders([(0, 0, 0)]),
    Piece.SmallCurve: generateOffsetColliders([(0, 0, 0), (0, 0, 1), (1, 0, 0), (1, 0, 1)]),
    Piece.RegularCurve: generateOffsetColliders([(0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1), (2, 0, 1), (1, 0, 2), ((2, 0, 2))]),
    Piece.StationPlatform: generateOffsetColliders([(0, 0, 0)]),
    Piece.SBend: [(0, 0, 0), (1, 0, 0), (1, 0, 1), (2, 0, 1)]
    # Piece.Brakes: offsetCollisions([(0, 0, 0)]),
}

pieceUpSlopeColliders = {
    Piece.Straight: generateOffsetColliders([(0, 0, 0)]),
    Piece.SmallCurve: generateOffsetColliders([(0, 0, 0), (1, 2, 1)]) + [(1, 1, 0), (0, 1, 1)],
    Piece.RegularCurve: generateOffsetColliders([(0, 0, 0),  (2, 4, 2)]) + [(0, 1, 1), (0, 1, 1), (1, 1, 0), (1, 1, 0),
                                                                            (2, 3, 1), (2, 3, 1), (1,
                                                                                                   3, 2), (1, 3, 2),
                                                                            (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1)],
    # Piece.HelixSmall
    # Piece.HelixLarge
}

pieceDownSlopeColliders = {
    Piece.Straight: generateOffsetColliders([(0, 0, 0)]),
    Piece.SmallCurve: generateOffsetColliders([(0, 0, 0), (1, -2, 1)]) + [(1, -1, 0), (0, -1, 1)],
    Piece.RegularCurve: generateOffsetColliders([(0, 0, 0),  (2, -4, 2)]) + [(0, -1, 1), (0, -1, 1), (1, -1, 0), (1, -1, 0),
                                                                             (2, -3, 1), (2, -3, 1), (1,
                                                                                                      -3, 2), (1, -3, 2),
                                                                             (1, -1, 1), (1, -2, 1), (1, -3, 1), (1, -4, 1)],
    # Piece.HelixSmall
    # Piece.HelixLarge
}


def generateTrackColliders(enterState, track):
    piece, pieceCurve, pieceSlope, pieceRoll = track
    enterPosition, enterRotation, enterSlope, enterRoll = enterState
    enterX, enterY, enterZ = enterPosition

    colliders = []

    colliderSelect = {
        Slope.Level: pieceLevelSlopeColliders,
        Slope.Up: pieceUpSlopeColliders,
        Slope.Down: pieceDownSlopeColliders
    }

    colliders = colliderSelect[pieceSlope][piece].copy()

    dColliders = []
    for c in colliders:
        deltaX, deltaY, deltaZ = c
        # Account for Left-Hand Curve
        deltaZ = deltaZ * pieceCurve.value
        # Account for Rotation
        sinRotate = Angle.csin(enterRotation)
        cosRotate = Angle.ccos(enterRotation)
        deltaX, deltaZ = cosRotate * deltaX + sinRotate * \
            deltaZ, (-sinRotate) * deltaX + cosRotate * deltaZ
        dColliders.append((deltaX, deltaY, deltaZ))

    colliders = [(enterX + dx, enterY + dy, enterZ + dz)
                 for (dx, dy, dz) in dColliders]
    # print(colliders)
    return colliders


def generateColliders(startState, currentPath):
    currentState = startState
    colliders = set({})
    for track in currentPath:
        trackColliders = generateTrackColliders(currentState, track)
        for c in trackColliders:
            colliders.add(c)
        currentState = simulateTrackSequence(currentState, [track])
    return colliders


def validateCollision(startState, currentState, currentPath, track):
    colliders = generateColliders(startState, currentPath)
    # print(colliders)
    trackColliders = generateTrackColliders(currentState, track)
    # print(trackColliders)
    for c in trackColliders:
        if c not in colliders:
            colliders.add(c)
        else:
            #print("Collision Validation FAILED")
            # print(currentPath)
            return False
    return True


def simulateTrackSequence(currentState, trackSequence):
    for track in trackSequence:
        currentState = calculateExitState(track, currentState)
    return currentState


def visualizeColliders(colliders):
    x3d = []
    y3d = []
    z3d = []

    for c in colliders:
        x, y, z = c
        x3d.append(x)
        y3d.append(y)
        z3d.append(z)

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    # Note Matplotlib does not support vertical y-axis, so we switch y and z data/labels
    ax.scatter(x3d, z3d, y3d)
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zlabel('y')
    scaling = np.array([getattr(ax, 'get_{}lim'.format(dim))()
                        for dim in 'xyz'])
    ax.auto_scale_xyz(*[[np.min(scaling), np.max(scaling)]]*3)
    # Reverse so Z-axis (Y-axis) positive is out of page
    ax.invert_yaxis()
    plt.show()


def getTrackPieceCost(track: TrackPiece):
    # NOTE This only considers base (zero support structure / ground level) cost
    # TODO Add increasing support structure cost for distance above ground (~2 per support per 5ft of height)

    piece, pieceCurve, pieceSlope, pieceRoll = track
    costLevel = {
        Piece.Straight: 22,
        Piece.SmallCurve: 53,
        Piece.RegularCurve: 88,
        Piece.StationPlatform: 33,
        Piece.SBend: 78,
        # Piece.Brakes: 30,
        # Piece.Booster: 26,
        # Piece.BlockBrakes: 26,
    }
    costSlope = {
        Piece.Straight: 25,
        Piece.SmallCurve: 96,
        Piece.RegularCurve: 125
    }
    costRoll = {
        Piece.Straight: 23,
        Piece.SmallCurve: 60,
        Piece.RegularCurve: 103,
    }
    costHelix = {
        # TODO
    }

    if pieceSlope == Slope.Level and pieceRoll == Roll.Level:
        return costLevel[piece]
    elif pieceSlope != Slope.Level and pieceRoll == Roll.Level:
        return costSlope[piece]
    elif pieceSlope == Slope.Level and pieceRoll != Roll.Level:
        return costRoll[piece]
    else:
        return costHelix[piece]
