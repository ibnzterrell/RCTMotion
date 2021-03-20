from track import *
from PriorityQueue import *
import matplotlib.pyplot as plt
import numpy as np
# Start State
startPos = (0, 0, 0)
startAngle = Angle.Degree0
startSlope = Slope.Level
startRoll = Roll.Level
startState = (startPos, startAngle, startSlope, startRoll)

# Closed Path, Goal State = Initial Start State
goalState = startState

# Start with a Station and a Spiral Lift Hill
stationTrack = (Piece.StationPlatform, Curve.Straight, Slope.Level, Roll.Level)
stationSequence = [stationTrack for i in range(6)]
straightSlopeUp = (Piece.Straight, Curve.Straight, Slope.Up, Roll.Level)
spiralSlopeUp = (Piece.SmallCurve, Curve.Right, Slope.Up, Roll.Level)
spiralLiftHillSequence = [straightSlopeUp] + [spiralSlopeUp for i in range(5)]

stationSpiralLiftHillSequence = stationSequence + spiralLiftHillSequence
trackSequence = []
trackSequence.extend(stationSpiralLiftHillSequence)

startHillState = simulateTrackSequence(startState, trackSequence)
print("VALIDATION", validateCollision(startState, startHillState,
                                      trackSequence[:-1], trackSequence[-1]))


def astar_search(searchStartState, goalState):
    frontier = PriorityQueue()
    frontier.put(searchStartState, 0)
    came_from: Dict[TrackState, Optional[TrackState]] = {}
    transition: Dict[(TrackState, TrackState), Optional[TrackPiece]] = {}
    cost_so_far: Dict[TrackState, int] = {}
    came_from[searchStartState] = None
    cost_so_far[searchStartState] = 0

    while not frontier.empty():
        currentState: TrackState = frontier.get()

        if currentState == goalState:
            print("SOLUTION FOUND")
            break

        for track in generatePossibleTracks(currentState):
            if (currentState != searchStartState):
                currentPath = stationSpiralLiftHillSequence + \
                    reconstruct_path(came_from, startHillState,
                                     currentState, transition)
                if not validateTrack(startState, currentState, currentPath, track):
                    continue
            new_cost = cost_so_far[currentState] + getTrackPieceCost(track)
            nextState = simulateTrackSequence(currentState, [track])
            if nextState not in cost_so_far or new_cost < cost_so_far[nextState]:
                cost_so_far[nextState] = new_cost
                priority = new_cost + \
                    manhattanStateHeuristic(currentState, goalState)
                frontier.put(nextState, priority)
                came_from[nextState] = currentState
                transition[(currentState, nextState)] = track
    return came_from, cost_so_far, transition


def reconstruct_path(came_from, startState, goalState, transition) -> List[TrackPiece]:
    currentState = goalState
    path = []

    # Because Python doesn't suppprt do-while ¯\_(ツ)_/¯
    condition = True
    while condition:
        lastState = came_from[currentState]
        path.append(transition[(lastState, currentState)])
        currentState = lastState
        condition = currentState != startState
    path.reverse()
    return path


print("SEARCHING")
came_from, cost_so_far, transition = astar_search(startHillState, goalState)
print("SEARCH FINISHED")
path = reconstruct_path(came_from, startHillState, goalState, transition)
trackSequence.extend(path)
print(path)
verifyState = simulateTrackSequence(startState, trackSequence)
print(verifyState)

state = startState
print(state)
for track in trackSequence:
    print(track)
    state = simulateTrackSequence(state, [track])
    print(state)

colliders = generateColliders(startState, trackSequence)
visualizeColliders(colliders)
