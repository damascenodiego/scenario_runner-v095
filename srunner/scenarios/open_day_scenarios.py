#!/usr/bin/env python

# Copyright (c) 2019 University of Leicester
# Copyright (c) 2019 University of Sao Paulo
# authors: Diego Damasceno (damascenodiego@usp.br)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Scenarios designed to the OpenDay @ Uni of Leicester 2019
"""

from __future__ import print_function
import sys

import py_trees
import carla

from srunner.scenariomanager.atomic_scenario_behavior import *
from srunner.scenariomanager.atomic_scenario_criteria import *
from srunner.scenariomanager.timer import TimeOut
from srunner.scenarios.basic_scenario import *


OPEN_DAY_SCENARIOS = [
    "OpenDay"
]


class OpenDay(BasicScenario):

    """
    This class holds everything required for a scenario,
    in which an other vehicle takes priority from the ego
    vehicle, by running a red traffic light (while the ego
    vehicle has green)
    """

    category = "OpenDay"
    radius = 10.0           # meters
    timeout = 300           # Timeout of scenario in seconds

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

        super(OpenDay, self).__init__("OpenDay", ego_vehicle, other_actors, town, world, debug_mode, True)

    def _create_behavior(self):
        """
        Basic behavior do nothing, i.e. Idle
        """

        # Build behavior tree
        sequence = py_trees.composites.Sequence("Sequence Behavior")
        timeout = TimeOut(self.timeout)
        sequence.add_child(timeout)

        return sequence

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
        parallel_criteria.add_child(target_criterion)
        parallel_criteria.add_child(route_criterion)
        parallel_criteria.add_child(wrong_way_criterion)
        parallel_criteria.add_child(red_light_criterion)


        return parallel_criteria
