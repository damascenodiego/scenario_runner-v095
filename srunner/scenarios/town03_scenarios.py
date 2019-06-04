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


TOWN03_SCENARIOS = [
    "Town03GasStation"
]


class Town03GasStation(BasicScenario):

    """
    This class holds everything required for a scenario,
    in which an other vehicle takes priority from the ego
    vehicle, by running a red traffic light (while the ego
    vehicle has green)
    """

    category = "Town03Scenarios"
    radius = 5.0           # meters
    timeout = 900           # Timeout of scenario in seconds

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 30
    _cyclist_location_of_collision = carla.Location(78, -104)

    # car parameters
    _car_trigger_distance_from_ego = 40
    _car_location_of_collision = carla.Location(-8, 127)

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
        timeout = TimeOut(self.timeout)

        # leaf nodes
        cyclist_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[0],
            self.ego_vehicle,
            self._cyclist_trigger_distance_from_ego)
        cyclist_collision = TriggerCollision(
            self.other_actors[0],
            self.ego_vehicle,
            self._cyclist_location_of_collision,
            [-1, 0])
        car_trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[4],
            self.ego_vehicle,
            self._car_trigger_distance_from_ego)
        car_collision = TriggerCollision(
            self.other_actors[4],
            self.ego_vehicle,
            self._car_location_of_collision,
            [1, 0])
        show_route = PlotTrajectory(
             self.ego_vehicle,
             self._route)

        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(
            policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        cyclist_sequence = py_trees.composites.Sequence()
        car_root = py_trees.composites.Parallel(
            policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        car_sequence = py_trees.composites.Sequence()

        # building the tress
        cyclist_root.add_child(cyclist_sequence)
        cyclist_sequence.add_child(cyclist_trigger_distance)
        cyclist_sequence.add_child(cyclist_collision)

        car_root.add_child(car_sequence)
        car_sequence.add_child(car_trigger_distance)
        car_sequence.add_child(car_collision)

        root.add_child(show_route)
        root.add_child(cyclist_root)
        root.add_child(car_root)
        root.add_child(timeout)

        return root

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """

        collision_criterion = CollisionTest(self.ego_vehicle)
        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)
        red_light_criterion = RunningRedLightTest(self.ego_vehicle)
        route_criterion = InRouteTest(self.ego_vehicle, radius=30.0, route=self._route, offroad_max=100)
        completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self._route)
        target_criterion = InRadiusRegionTest(self.ego_vehicle, x=self._target.x, y=self._target.y, radius=self.radius)

        parallel_criteria = py_trees.composites.Parallel("group_criteria", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        parallel_criteria.add_child(collision_criterion)
        parallel_criteria.add_child(completion_criterion)
        parallel_criteria.add_child(target_criterion)
        parallel_criteria.add_child(route_criterion)
        parallel_criteria.add_child(wrong_way_criterion)
        parallel_criteria.add_child(red_light_criterion)

        return parallel_criteria
