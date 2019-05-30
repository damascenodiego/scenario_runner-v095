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

    # other vehicle parameters
    _cyclist_target_velocity = -10
    _cyclist_trigger_distance_from_ego = 15
    _cyclist_max_throttle = 1
    _cyclist_max_brake = 1.0
    _cyclist_location_of_collision = carla.Location(x=85, y=-104, z=8)

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
        root = py_trees.composites.Parallel(policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        sequence = py_trees.composites.Sequence("Sequence Behavior")
        timeout = TimeOut(self.timeout)

        # leaf nodes
        trigger_distance = InTriggerDistanceToVehicle(
            self.other_actors[1],
            self.ego_vehicle,
            self._cyclist_trigger_distance_from_ego)
        start_other = KeepVelocity(
            self.other_actors[0],
            self._cyclist_target_velocity)
        # trigger_other = InTriggerRegion(
        #     self.other_actors[0],
        #     70, 75,
        #     -109, -112)
        instant_vel = SetInstantVelocity(
            self.other_actors[0],
            carla.Vector3D(self._cyclist_target_velocity,0,0))
        show_route = PlotTrajectory(
            self.ego_vehicle,
            self.route)
        # timeout_other = TimeOut(3)
        # sync_arrival = SyncArrival(
        #     self.other_actors[0], self.ego_vehicle, self._cyclist_location_of_collision)
        # sync_arrival_stop = InTriggerDistanceToVehicle(self.other_actors[0],
        #                                                self.ego_vehicle,
        #                                                15)

        # non leaf nodes
        cyclist_root = py_trees.composites.Parallel(
            policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        scenario_sequence = py_trees.composites.Sequence()
        keep_velocity_other = py_trees.composites.Parallel(
            policy=py_trees.common.ParallelPolicy.SuccessOnOne())
        # sync_arrival_parallel = py_trees.composites.Parallel(
        #     "Synchronize arrival times",
        #     policy=py_trees.common.ParallelPolicy.SuccessOnOne())

        # building the tress
        cyclist_root.add_child(scenario_sequence)
        scenario_sequence.add_child(trigger_distance)
        # scenario_sequence.add_child(sync_arrival_parallel)
        scenario_sequence.add_child(keep_velocity_other)
        # scenario_sequence.add_child(stop_other)
        # scenario_sequence.add_child(timeout_other)
        keep_velocity_other.add_child(instant_vel)
        # sync_arrival_parallel.add_child(sync_arrival)
        # sync_arrival_parallel.add_child(sync_arrival_stop)

        sequence.add_child(cyclist_root)
        sequence.add_child(timeout)

        # root.add_child(show_route)
        root.add_child(sequence)

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
                                                  #, terminate_on_failure=True
                                                  )

        wrong_way_criterion = WrongLaneTest(self.ego_vehicle)

        red_light_criterion = RunningRedLightTest(self.ego_vehicle
                                                  # , terminate_on_failure=True
                                                  )

        parallel_criteria = py_trees.composites.Parallel("group_criteria",
                                                         policy=py_trees.common.ParallelPolicy.SuccessOnOne())

        parallel_criteria.add_child(collision_criterion)
        parallel_criteria.add_child(completion_criterion)
        #parallel_criteria.add_child(target_criterion)
        #parallel_criteria.add_child(route_criterion)
        parallel_criteria.add_child(wrong_way_criterion)
        parallel_criteria.add_child(red_light_criterion)


        return parallel_criteria
