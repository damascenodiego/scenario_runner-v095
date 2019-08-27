#!/usr/bin/env python

# Copyright (c) 2019 University of Leicester
# Copyright (c) 2019 University of Sao Paulo
# authors: Diego Damasceno (damascenodiego@usp.br)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Scenarios designed for the OpenDay @ Uni of Leicester 2019
"""

from __future__ import print_function
import sys

import py_trees
import carla

from srunner.scenariomanager.atomic_scenario_behavior import *
from srunner.scenariomanager.atomic_scenario_criteria import *
from srunner.scenariomanager.timer import TimeOut
from srunner.scenarios.basic_scenario import *


ROYALSOCIETY_SCENARIOS = [
    "Town03GasStation",
    "Town03TrainTrack",
    "Town01Restaurant",
    "Town04ParkingLot",
    "Town07Farm"

]


class Town03GasStation(BasicScenario):

    """
    This class holds everything required for a scenario,
    in which an other vehicle takes priority from the ego
    vehicle, by running a red traffic light (while the ego
    vehicle has green)
    """

    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 30
    _cyclist_location_of_collision = carla.Location(78, -104)

    # car parameters
    _car_trigger_distance_from_ego = 40
    _car_location_of_collision = carla.Location(-8, 127)

    score = 0

    def __init__(self, world, ego_vehicle, other_actors, town, randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self._config = config
        self._target = None
        self._route = None
        self.timeout = config.timeout
        ScenarioInfo.cameraTransform = carla.Transform(carla.Location(x=135.5, y=-34.7, z=220.5), carla.Rotation(yaw=-178.9, pitch=-66.3, roll=2.5))

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town03GasStation, self).__init__("Town03GasStation", ego_vehicle, other_actors, town, world, int(config.timeout), debug_mode, True)

    def _create_behavior(self):
        """
        Basic behavior do nothing, i.e. Idle
        """

        # Build behavior tree
        root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        timeout = TimeOut(self.timeout*10, display=False)

        # leaf nodes
        cyclist_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[0],
            self.ego_vehicle,
            self._cyclist_trigger_distance_from_ego)
        cyclist_collision = TriggerCollision(
            self.other_actors[0],
            self.ego_vehicle,
            self._cyclist_location_of_collision,
            [-1, 0],
            True)
        car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[4],
            self.ego_vehicle,
            self._car_trigger_distance_from_ego)
        car_collision = TriggerCollision(
            self.other_actors[4],
            self.ego_vehicle,
            self._car_location_of_collision,
            [1, 0],
            True)

        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        cyclist_sequence = py_trees.composites.Sequence()
        car_sequence = py_trees.composites.Sequence()

        # building the tress
        cyclist_root.add_child(cyclist_sequence)
        cyclist_sequence.add_child(cyclist_trigger_distance)
        cyclist_sequence.add_child(cyclist_collision)

        car_root.add_child(car_sequence)
        car_sequence.add_child(car_trigger_distance)
        car_sequence.add_child(car_collision)

        root.add_child(cyclist_root)
        root.add_child(car_root)
        root.add_child(timeout)

        self.plotTrajectory()

        return root

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """

        root = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        root_sequence = py_trees.composites.Sequence()
        timeout = TimeOut(self.timeout, display=True)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=10.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        test_criteria.add_child(completion_criterion)
        test_criteria.add_child(timeout)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion, timeout, completion_criterion]
        score_counter = ComputeScore(criteria, self.ego_vehicle, self.name)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)


        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.2)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [0, 1])


class Town03TrainTrack(BasicScenario):
    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 22
    _cyclist_location_of_collision = carla.Location(-114.5, 27.4)

    # car parameters
    _car_trigger_distance_from_ego = 45
    _car_location_of_collision = carla.Location(-9.5, 136.3)

    # driveway car parameters
    _driveway_car_trigger_distance_from_ego = 27
    _driveway_car_location_of_collision = carla.Location(109.1, 131)

    score = 0

    def __init__(self, world, ego_vehicle, other_actors, town, randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self._config = config
        self._target = None
        self._route = None
        self.timeout = config.timeout

        ScenarioInfo.cameraTransform = carla.Transform(carla.Location(x=87.0, y=171.1, z=300.8), carla.Rotation(yaw=-89.9, pitch=-69.2, roll=0))

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town03TrainTrack, self).__init__("Town03TrainTrack", ego_vehicle, other_actors, town, world, int(config.timeout), debug_mode, True)

    def _create_behavior(self):
        """
        Basic behavior do nothing, i.e. Idle
        """

        # Build behavior tree
        root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        timeout = TimeOut(self.timeout*10)

        # leaf nodes
        cyclist_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[0],
            self.ego_vehicle,
            self._cyclist_trigger_distance_from_ego)
        cyclist_collision = TriggerCollision(
            self.other_actors[0],
            self.ego_vehicle,
            self._cyclist_location_of_collision,
            [0, 1],
            False)

        car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[1],
            self.ego_vehicle,
            self._car_trigger_distance_from_ego)
        car_collision = TriggerCollision(
            self.other_actors[1],
            self.ego_vehicle,
            self._car_location_of_collision,
            [0, 1],
            True)

        driveway_car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[2],
            self.ego_vehicle,
            self._driveway_car_trigger_distance_from_ego)
        driveway_car_collision = TriggerCollision(
            self.other_actors[2],
            self.ego_vehicle,
            self._driveway_car_location_of_collision,
            [0, 1],
            True)

        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        driveway_car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        cyclist_sequence = py_trees.composites.Sequence()
        car_sequence = py_trees.composites.Sequence()
        driveway_car_sequence = py_trees.composites.Sequence()

        # building the tress
        cyclist_root.add_child(cyclist_sequence)
        cyclist_sequence.add_child(cyclist_trigger_distance)
        cyclist_sequence.add_child(cyclist_collision)

        car_root.add_child(car_sequence)
        car_sequence.add_child(car_trigger_distance)
        car_sequence.add_child(car_collision)

        driveway_car_root.add_child(driveway_car_sequence)
        driveway_car_sequence.add_child(driveway_car_trigger_distance)
        driveway_car_sequence.add_child(driveway_car_collision)

        root.add_child(cyclist_root)
        root.add_child(car_root)
        root.add_child(driveway_car_root)
        root.add_child(timeout)

        self.plotTrajectory()

        return root

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """

        root = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        root_sequence = py_trees.composites.Sequence()
        timeout = TimeOut(self.timeout, display=True)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=10.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        test_criteria.add_child(completion_criterion)
        test_criteria.add_child(timeout)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion, timeout, completion_criterion]
        score_counter = ComputeScore(criteria, self.ego_vehicle, self.name)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)

        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.2)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [1, 0])


class Town01Restaurant(BasicScenario):
    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters

    # driveway car parameters
    _driveway_car_trigger_distance_from_ego = 25
    _driveway_car_location_of_collision = carla.Location(334, 95.2)

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 25
    _cyclist_location_of_collision = carla.Location(202, 129)

    # car parameters
    _car_trigger_distance_from_ego = 25
    _car_location_of_collision = carla.Location(92, 133)



    score = 0

    def __init__(self, world, ego_vehicle, other_actors, town, randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self._config = config
        self._target = None
        self._route = None
        self.timeout = config.timeout

        ScenarioInfo.cameraTransform = carla.Transform(carla.Location(x=455.1, y=260.2, z=205.4), carla.Rotation(yaw=-157.8, pitch=-52.5, roll=-1.4))
        ScenarioInfo.mandatoryWrongLane = 1


        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town01Restaurant, self).__init__("Town01Restaurant", ego_vehicle, other_actors, town, world, int(config.timeout), debug_mode, True)

    def _create_behavior(self):
        """
        Basic behavior do nothing, i.e. Idle
        """

        # Build behavior tree
        root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        timeout = TimeOut(self.timeout*10)

        # leaf nodes
        driveway_car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[0],
            self.ego_vehicle,
            self._driveway_car_trigger_distance_from_ego)
        driveway_car_collision = TriggerCollision(
            self.other_actors[0],
            self.ego_vehicle,
            self._driveway_car_location_of_collision,
            [1, 0],
            True)
        cyclist_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[2],
            self.ego_vehicle,
            self._cyclist_trigger_distance_from_ego)
        cyclist_collision = TriggerCollision(
            self.other_actors[2],
            self.ego_vehicle,
            self._cyclist_location_of_collision,
            [0, 1],
            True)
        car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[4],
            self.ego_vehicle,
            self._car_trigger_distance_from_ego)
        car_collision = TriggerCollision(
            self.other_actors[4],
            self.ego_vehicle,
            self._car_location_of_collision,
            [0, 1],
            True)



        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        driveway_car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        cyclist_sequence = py_trees.composites.Sequence()
        car_sequence = py_trees.composites.Sequence()
        driveway_car_sequence = py_trees.composites.Sequence()

        # building the tress
        cyclist_root.add_child(cyclist_sequence)
        cyclist_sequence.add_child(cyclist_trigger_distance)
        cyclist_sequence.add_child(cyclist_collision)

        car_root.add_child(car_sequence)
        car_sequence.add_child(car_trigger_distance)
        car_sequence.add_child(car_collision)

        driveway_car_root.add_child(driveway_car_sequence)
        driveway_car_sequence.add_child(driveway_car_trigger_distance)
        driveway_car_sequence.add_child(driveway_car_collision)

        root.add_child(cyclist_root)
        root.add_child(car_root)
        root.add_child(driveway_car_root)
        root.add_child(timeout)

        self.plotTrajectory()

        return root

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """

        root = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        root_sequence = py_trees.composites.Sequence()
        timeout = TimeOut(self.timeout, display=True)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=10.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        test_criteria.add_child(completion_criterion)
        test_criteria.add_child(timeout)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion, timeout, completion_criterion]
        score_counter = ComputeScore(criteria, self.ego_vehicle, self.name)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)

        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.2)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [0, 1])


class Town04ParkingLot(BasicScenario):
    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters

    # car parameters
    _car_trigger_distance_from_ego = 30
    _car_location_of_collision = carla.Location(310.9, -172.2)

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 22
    _cyclist_location_of_collision = carla.Location(239, -172.8)

    # driveway car parameters
    _driveway_car_trigger_distance_from_ego = 20
    _driveway_car_location_of_collision = carla.Location(183.7, -246)

    score = 0

    def __init__(self, world, ego_vehicle, other_actors, town, randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self._config = config
        self._target = None
        self._route = None
        self.timeout = config.timeout

        ScenarioInfo.cameraTransform = carla.Transform(carla.Location(x=219.2, y=-107.7, z=162.6), carla.Rotation(yaw=-89.1, pitch=-58.9, roll=3.3))
        ScenarioInfo.mandatoryWrongLane = 2

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]
            ScenarioInfo.route = self._route

        super(Town04ParkingLot, self).__init__("Town04ParkingLot", ego_vehicle, other_actors, town, world, int(config.timeout), debug_mode, True)

    def _create_behavior(self):
        """
        Basic behavior do nothing, i.e. Idle
        """

        # Build behavior tree
        root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        timeout = TimeOut(self.timeout*10)

        # leaf nodes
        car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[0],
            self.ego_vehicle,
            self._car_trigger_distance_from_ego)
        car_collision = TriggerCollision(
            self.other_actors[0],
            self.ego_vehicle,
            self._car_location_of_collision,
            [0, 1],
            True)
        cyclist_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[1],
            self.ego_vehicle,
            self._cyclist_trigger_distance_from_ego)
        cyclist_collision = TriggerCollision(
            self.other_actors[1],
            self.ego_vehicle,
            self._cyclist_location_of_collision,
            [0, -1],
            True)
        driveway_car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[8],
            self.ego_vehicle,
            self._driveway_car_trigger_distance_from_ego)
        driveway_car_collision = TriggerCollision(
            self.other_actors[8],
            self.ego_vehicle,
            self._driveway_car_location_of_collision,
            [0, -1],
            False)




        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        driveway_car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        cyclist_sequence = py_trees.composites.Sequence()
        car_sequence = py_trees.composites.Sequence()
        driveway_car_sequence = py_trees.composites.Sequence()

        # building the tress
        cyclist_root.add_child(cyclist_sequence)
        cyclist_sequence.add_child(cyclist_trigger_distance)
        cyclist_sequence.add_child(cyclist_collision)

        car_root.add_child(car_sequence)
        car_sequence.add_child(car_trigger_distance)
        car_sequence.add_child(car_collision)

        driveway_car_root.add_child(driveway_car_sequence)
        driveway_car_sequence.add_child(driveway_car_trigger_distance)
        driveway_car_sequence.add_child(driveway_car_collision)

        root.add_child(cyclist_root)
        root.add_child(car_root)
        root.add_child(driveway_car_root)
        root.add_child(timeout)

        self.plotTrajectory()

        return root

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """

        root = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        root_sequence = py_trees.composites.Sequence()
        timeout = TimeOut(self.timeout, display=True)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=10.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(timeout)
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        test_criteria.add_child(completion_criterion)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion, timeout, completion_criterion]
        score_counter = ComputeScore(criteria, self.ego_vehicle, self.name)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)

        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.2)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [0, 1])


class Town07Farm(BasicScenario):
    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters

    # car parameters
    _car_trigger_distance_from_ego = 35
    _car_location_of_collision = carla.Location(-5.3, -3.1)

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 17
    _cyclist_location_of_collision = carla.Location(-150.8, -3)

    # driveway car parameters
    _driveway_car_trigger_distance_from_ego = 18
    _driveway_car_location_of_collision = carla.Location(-59.0, -63.5)

    score = 0

    def __init__(self, world, ego_vehicle, other_actors, town,  randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self._config = config
        self._target = None
        self._route = None
        self.timeout = config.timeout

        ScenarioInfo.cameraTransform = carla.Transform(carla.Location(x=-179.4, y=-85.0, z=239.7), carla.Rotation(yaw=0.6, pitch=-69.1, roll=3.7))
        ScenarioInfo.mandatoryWrongLane = 5

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town07Farm, self).__init__("Town07Farm", ego_vehicle, other_actors, town, world, int(config.timeout), debug_mode, True)

    def _create_behavior(self):
        """
        Basic behavior do nothing, i.e. Idle
        """

        # Build behavior tree
        root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        timeout = TimeOut(self.timeout*10)

        # leaf nodes
        car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[2],
            self.ego_vehicle,
            self._car_trigger_distance_from_ego)
        car_collision = TriggerCollision(
            self.other_actors[2],
            self.ego_vehicle,
            self._car_location_of_collision,
            [0, 1],
            True)
        cyclist_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[3],
            self.ego_vehicle,
            self._cyclist_trigger_distance_from_ego)
        cyclist_collision = TriggerCollision(
            self.other_actors[3],
            self.ego_vehicle,
            self._cyclist_location_of_collision,
            [1, 0],
            True)
        driveway_car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[5],
            self.ego_vehicle,
            self._driveway_car_trigger_distance_from_ego)
        driveway_car_collision = TriggerCollision(
            self.other_actors[5],
            self.ego_vehicle,
            self._driveway_car_location_of_collision,
            [0, 1],
            True)




        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        driveway_car_root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        cyclist_sequence = py_trees.composites.Sequence()
        car_sequence = py_trees.composites.Sequence()
        driveway_car_sequence = py_trees.composites.Sequence()

        # building the tress
        cyclist_root.add_child(cyclist_sequence)
        cyclist_sequence.add_child(cyclist_trigger_distance)
        cyclist_sequence.add_child(cyclist_collision)

        car_root.add_child(car_sequence)
        car_sequence.add_child(car_trigger_distance)
        car_sequence.add_child(car_collision)

        driveway_car_root.add_child(driveway_car_sequence)
        driveway_car_sequence.add_child(driveway_car_trigger_distance)
        driveway_car_sequence.add_child(driveway_car_collision)

        root.add_child(cyclist_root)
        root.add_child(car_root)
        root.add_child(driveway_car_root)
        root.add_child(timeout)

        self.plotTrajectory()

        return root

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """

        root = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
        root_sequence = py_trees.composites.Sequence()
        timeout = TimeOut(self.timeout, display=True)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=10.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(timeout)
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        test_criteria.add_child(completion_criterion)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion, timeout, completion_criterion]
        score_counter = ComputeScore(criteria, self.ego_vehicle, self.name)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)

        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.2)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [1, 0])