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
    radius = 10.0           # meters
    timeout = 300           # Timeout of scenario in seconds

    # cyclist parameters
    _cyclist_trigger_distance_from_ego = 25
    _cyclist_location_of_collision = carla.Location(83, -104)
    _cyclist_timeout = 20

    # car parameters
    _car_trigger_distance_from_ego = 40
    _car_location_of_collision = carla.Location(-8, 127)
    _car_timeout = 20

    def __init__(self, world, ego_vehicle, other_actors, town, randomize=False, debug_mode=False, config=None):
        """
        Setup all relevant parameters and create scenario
        """
        self.config = config
        self.target = None
        self.route = None

        if hasattr(self.config, 'target'):
            self.target = self.config.target
        if hasattr(self.config, 'route'):
            self.route = self.config.route.data

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
            self.other_actors[2],
            self.ego_vehicle,
            self._car_trigger_distance_from_ego)
        car_collision = TriggerCollision(
            self.other_actors[2],
            self.ego_vehicle,
            self._car_location_of_collision,
            [1, 0])
        show_route = PlotTrajectory(
             self.ego_vehicle,
             self.route)

        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(
            policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        cyclist_sequence = py_trees.composites.Sequence()
        cyclist_timeout = TimeOut(self._cyclist_timeout)
        car_root = py_trees.composites.Parallel(
            policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        car_sequence = py_trees.composites.Sequence()
        car_timeout = TimeOut(self._car_timeout)

        # building the tress
        #cyclist_root.add_child(cyclist_timeout)
        cyclist_root.add_child(cyclist_sequence)
        cyclist_sequence.add_child(cyclist_trigger_distance)
        cyclist_sequence.add_child(cyclist_collision)

        # car_root.add_child(car_timeout)
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

        collision_criterion = CollisionTest(self.ego_vehicle, terminate_on_failure=True)
        target_criterion = InRadiusRegionTest(self.ego_vehicle,
                                              x=self.target.transform.location.x,
                                              y=self.target.transform.location.y,
                                              radius=self.radius)

        route_criterion = InRouteTest(self.ego_vehicle,
                                      radius=30.0,
                                      route=self.route,
                                      offroad_max=100,
                                      terminate_on_failure=True)

        completion_criterion = RouteCompletionTest(self.ego_vehicle, route=self.route
                                                  , terminate_on_failure=True
                                                  )

        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)

        red_light_criterion = RunningRedLightTest(self.ego_vehicle
                                                  # , terminate_on_failure=True
                                                  )

        parallel_criteria = py_trees.composites.Parallel("group_criteria",
                                                         policy=py_trees.common.ParallelPolicy.SuccessOnOne())

        parallel_criteria.add_child(collision_criterion)
        parallel_criteria.add_child(completion_criterion)
        parallel_criteria.add_child(target_criterion)
        #parallel_criteria.add_child(route_criterion)
        parallel_criteria.add_child(wrong_way_criterion)
        parallel_criteria.add_child(red_light_criterion)


        return parallel_criteria
