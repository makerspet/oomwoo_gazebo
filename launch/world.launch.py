#!/usr/bin/env python3
#
# Copyright 2023-2025 KAIA.AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, re
import xacro
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription, LaunchContext
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, OpaqueFunction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node
from kaiaai import config


pkg_ros_gz_sim = get_package_share_path('ros_gz_sim')

def make_nodes(context: LaunchContext, robot_model, use_sim_time, x_pose, y_pose, world, headless, odom_source):
    robot_model_str = context.perform_substitution(robot_model)
    use_sim_time_str = context.perform_substitution(use_sim_time)
    x_pose_str = context.perform_substitution(x_pose)
    y_pose_str = context.perform_substitution(y_pose)
    world_str = context.perform_substitution(world)
    headless_bool = context.perform_substitution(headless).lower() == 'true'
    odom_source_str = context.perform_substitution(odom_source)

    if len(robot_model_str) == 0:
      robot_model_str = config.get_var('robot.model')

    urdf_path_name = os.path.join(
      get_package_share_path(robot_model_str), 'urdf', 'robot.urdf.xacro'
    )

    # odom_source (ground_truth|robot_wheels) selects which odometry owns /odom
    # + /tf; both are always published (the other on /odom_wheel or /odom_truth).
    # enable_* turn heavy rendering sensors off to speed up Gazebo (cameras and
    # the front ToF cost the most). Read straight from the launch context.
    mappings = {'odom_source': odom_source_str}
    for name in ('enable_lidar', 'enable_ranges', 'enable_tof',
                 'enable_cameras', 'enable_imu'):
        mappings[name] = context.perform_substitution(LaunchConfiguration(name))
    # robot_description = ParameterValue(Command(['xacro ', urdf_path_name]), value_type=str)
    robot_description = xacro.process_file(
      urdf_path_name, mappings=mappings).toxml()

    # sdf_path_name = os.path.join(
    #     get_package_share_path(robot_model_str),
    #     'sdf',
    #     robot_model_str,
    #     'model.sdf'
    # )

    gz_bridge_params_path_name = os.path.join(
      get_package_share_path(robot_model_str),
      'config',
      'gz_bridge.yaml'
    )

    # pkg_gazebo_ros = get_package_share_path('gazebo_ros')
    world_path_name = os.path.join(get_package_share_path('oomwoo_gazebo'), 'worlds', world_str)
    model_path_name = os.path.join(get_package_share_path('oomwoo_gazebo'), 'models')

    print('URDF  file name : {}'.format(urdf_path_name))
    # print('SDF   file name : {}'.format(sdf_path_name))
    print('World file name : {}'.format(world_path_name))

    # Headless: server-only (-s) + offscreen rendering, with forced software GL so
    # the GPU-LiDAR renders under Docker/CI without a display. Otherwise the GUI runs.
    gz_args = ('-s -r --headless-rendering -v 4 ' if headless_bool
               else '-r -v 4 ') + world_path_name

    # Keep locally vendored world assets self-contained for Gazebo Sim.  This
    # also preserves an existing user resource path for other worlds.
    env = [
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            model_path_name + os.pathsep + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
        )
    ]
    if headless_bool:
        env = [
            SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
            SetEnvironmentVariable('GALLIUM_DRIVER', 'llvmpipe'),
        ]

    return env + [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={
                'gz_args': gz_args,
                'on_exit_shutdown': 'true'
            }.items()
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            output='screen',
            arguments=[
                '--ros-args',
                '-p',
                f'config_file:={gz_bridge_params_path_name}',
            ]
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time_str.lower() == 'true',
                'robot_description': robot_description
            }]
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', robot_model_str,
                '-topic', 'robot_description',
                '-timeout', '180',
                '-x', x_pose_str,
                '-y', y_pose_str,
                '-g', ' ',
                # '-z', z_pose_str,
                # '-R', roll_pose_str,
                # '-P', pitch_pose_str,
                # '-Y', yaw_pose_str,
                '-allow_renaming', 'false'
            ],
            output='screen'
        )
    ]

def generate_launch_description():

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='true',
            choices=['true', 'false'],
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            name='robot_model',
            default_value='',
            description='Robot description package name'
        ),
        DeclareLaunchArgument(
            name='x_pose',
            default_value='-2.0',
            description='Robot starting x position'
        ),
        DeclareLaunchArgument(
            name='y_pose',
            default_value='-0.5',
            description='Robot starting y position'
        ),
        DeclareLaunchArgument(
            name='world',
            # default_value='living_room.world',
            default_value='living_room.world',
            description='World file name'
        ),
        DeclareLaunchArgument(
            name='headless',
            default_value='false',
            choices=['true', 'false'],
            description='Run Gazebo headless: server-only, offscreen rendering, software GL (no GUI)'
        ),
        DeclareLaunchArgument(
            name='odom_source',
            default_value='ground_truth',
            choices=['ground_truth', 'robot_wheels'],
            description='Which odometry owns /odom + /tf: ground_truth = true '
                        'model pose (slip-free); robot_wheels = wheel-encoder '
                        'odometry (slip drifts). Both are always published; the '
                        'other is on /odom_wheel or /odom_truth for comparison.'
        ),
        # Per-sensor on/off (default all on). Turn heavy rendering sensors off to
        # speed up Gazebo: cameras and the front ToF cost the most, then the side
        # ranges and the LiDAR. The sensor links stay in the model; only the gz
        # sensor (render cost) is dropped.
        DeclareLaunchArgument(
            name='enable_lidar', default_value='true',
            choices=['true', 'false'], description='2D LiDAR /scan'),
        DeclareLaunchArgument(
            name='enable_ranges', default_value='true',
            choices=['true', 'false'], description='side distance /range_left|right'),
        DeclareLaunchArgument(
            name='enable_tof', default_value='true',
            choices=['true', 'false'], description='front ToF /tof_front/points'),
        DeclareLaunchArgument(
            name='enable_cameras', default_value='false',
            choices=['true', 'false'],
            description='stereo cameras /camera_left|right (off by default: heavy, unused for now)'),
        DeclareLaunchArgument(
            name='enable_imu', default_value='true',
            choices=['true', 'false'], description='IMU /imu'),
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(
        #         os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        #     ),
        # ),
        OpaqueFunction(function=make_nodes, args=[
            LaunchConfiguration('robot_model'),
            LaunchConfiguration('use_sim_time'),
            LaunchConfiguration('x_pose'),
            LaunchConfiguration('y_pose'),
            LaunchConfiguration('world'),
            LaunchConfiguration('headless'),
            LaunchConfiguration('odom_source')
        ])
    ])
