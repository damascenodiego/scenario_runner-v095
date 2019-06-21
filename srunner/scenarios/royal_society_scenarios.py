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
    "Town04ParkingLot"
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
    timeout = 900           # Timeout of scenario in seconds

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

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town03GasStation, self).__init__("Town03GasStation", ego_vehicle, other_actors, town, world, debug_mode, True)

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
        timeout = TimeOut(self.timeout)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=30.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        # completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        # test_criteria.add_child(completion_criterion)
        test_criteria.add_child(timeout)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion]
        score_counter = CountScore(criteria, self.ego_vehicle, self.timeout)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)


        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.3)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [0, 1])


class Town03TrainTrack(BasicScenario):
    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters
    timeout = 900           # Timeout of scenario in seconds

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 20
    _cyclist_location_of_collision = carla.Location(-114.5, 27.4)

    # car parameters
    _car_trigger_distance_from_ego = 45
    _car_location_of_collision = carla.Location(-9.5, 136.3)

    # driveway car parameters
    _driveway_car_trigger_distance_from_ego = 25
    _driveway_car_location_of_collision = carla.Location(146.3, 140)

    score = 0

    def __init__(self, world, ego_vehicle, other_actors, town, randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self._config = config
        self._target = None
        self._route = None

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town03TrainTrack, self).__init__("Town03TrainTrack", ego_vehicle, other_actors, town, world, debug_mode, True)

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
            [0, -1],
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
        timeout = TimeOut(self.timeout)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=30.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        # route_percentage_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        # test_criteria.add_child(route_percentage_criterion)
        test_criteria.add_child(timeout)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion]
        score_counter = CountScore(criteria, self.ego_vehicle, self.timeout)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)

        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.3)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [1, 0])


class Town01Restaurant(BasicScenario):
    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters
    timeout = 900           # Timeout of scenario in seconds

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

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town01Restaurant, self).__init__("Town01Restaurant", ego_vehicle, other_actors, town, world, debug_mode, True)

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
        timeout = TimeOut(self.timeout)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=30.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        # route_percentage_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        # test_criteria.add_child(route_percentage_criterion)
        test_criteria.add_child(timeout)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion]
        score_counter = CountScore(criteria, self.ego_vehicle, self.timeout)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)

        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.3)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [0, 1])


class Town04ParkingLot(BasicScenario):
    category = "RoyalSocietyScenarios"
    radius = 5.0           # meters
    timeout = 900           # Timeout of scenario in seconds

    # car parameters
    _car_trigger_distance_from_ego = 30
    _car_location_of_collision = carla.Location(310.9, -172.2)

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 30
    _cyclist_location_of_collision = carla.Location(239, -172.8)

    # driveway car parameters
    _driveway_car_trigger_distance_from_ego = 25
    _driveway_car_location_of_collision = carla.Location(183.7, -246)

    score = 0

    def __init__(self, world, ego_vehicle, other_actors, town, randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self._config = config
        self._target = None
        self._route = None

        if hasattr(self._config, 'route'):
            self._route = self._config.route.data
            self._target = self._route[-1][0]

        super(Town04ParkingLot, self).__init__("Town04ParkingLot", ego_vehicle, other_actors, town, world, debug_mode, True)

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
        timeout = TimeOut(self.timeout)

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        in_route_criterion = InRouteTest(self.ego_vehicle, radius=30.0, route=self._route, offroad_max=100)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,  x=self._target.x, y=self._target.y, radius=self.radius)
        # route_percentage_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)

        test_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        test_criteria.add_child(timeout)
        test_criteria.add_child(collision_criterion)
        test_criteria.add_child(target_criterion)
        test_criteria.add_child(in_route_criterion)
        test_criteria.add_child(wrong_way_criterion)
        test_criteria.add_child(red_light_criterion)
        # test_criteria.add_child(route_percentage_criterion)

        criteria = [collision_criterion, target_criterion, in_route_criterion, wrong_way_criterion, red_light_criterion]
        score_counter = CountScore(criteria, self.ego_vehicle, self.timeout)

        root_sequence.add_child(test_criteria)
        root_sequence.add_child(score_counter)
        root.add_child(root_sequence)

        return root

    def plotTrajectory(self):
        points = []
        for waypoint, _ in self._route:
            points.append(carla.Transform(waypoint))
        draw_waypoints_location(self.ego_vehicle.get_world(), points, 0.3)
        draw_circle(self.ego_vehicle.get_world(), self._target, 0.5, 0, 600, [0, 1])