from track import *
import matplotlib.pyplot as plt
import numpy as np

startState = ((0, 0, 0), Angle.Degree0, Slope.Level, Roll.Level)

# Lift Hill Test
stationTrack = (Piece.StationPlatform, Curve.Straight, Slope.Level, Roll.Level)
stationSequence = [stationTrack for i in range(6)]
straightSlopeUp = (Piece.Straight, Curve.Straight, Slope.Up, Roll.Level)
spiralSlopeUp = (Piece.SmallCurve, Curve.Right, Slope.Up, Roll.Level)
spiralLiftHillSequence = [straightSlopeUp] + [spiralSlopeUp for i in range(5)]

trackSequence = []
trackSequence.extend(stationSequence)
trackSequence.extend(spiralLiftHillSequence)

currentState = ((0, 0, 0), Angle.Degree0, Slope.Level, Roll.Level)
# print(currentState)
for track in trackSequence:
    #    print(track)
    currentState = calculateExitState(track, currentState)
#    print(currentState)

# Closed Track Test
# stationTrack = (Piece.StationPlatform, Curve.Straight, Slope.Level, Roll.Level)
# stationSequence = [stationTrack for i in range(6)]

# turnTrack = (Piece.SmallCurve, Curve.Right, Slope.Level, Roll.Level)
# turnSequence = [turnTrack for i in range(2)]

# straightTrack = (Piece.Straight, Curve.Straight, Slope.Level, Roll.Level)
# straightSequence = [straightTrack for i in range(6)]

# trackSequence = []
# trackSequence.extend(stationSequence)
# trackSequence.extend(turnSequence)
# trackSequence.extend(straightSequence)
# trackSequence.extend(turnSequence)

# currentState = startState
# for track in trackSequence:
#     # print(track)
#     currentState = calculateExitState(track, currentState)
#     # print(currentState)

colliders = generateColliders(startState, trackSequence)
print(colliders)


# minusState = simulateTrackSequence(startState, trackSequence[:-1])
# print(validateCollision(startState, minusState,
#                         trackSequence[:-1], trackSequence[-1]))
for i in range(len(trackSequence) - 1):
    minusState = simulateTrackSequence(startState, trackSequence[:-i])
    print(validateCollision(startState, minusState,
                            trackSequence[:-i], trackSequence[-i]))
# print(pieceLevelColliders[Piece.Straight])
