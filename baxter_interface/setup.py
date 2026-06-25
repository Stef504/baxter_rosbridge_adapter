from setuptools import find_packages, setup
import os 
from glob import glob

package_name = 'baxter_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='theengineroom1',
    maintainer_email='theengineroom1@todo.todo',
    description='Baxter SDK interface classes (rosbridge/roslibpy based) for ROS 2',
    license='BSD-3-Clause',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # The analog_io / camera / digital_io / gripper / head / limb /
            # navigator / robot_enable / robust_controller / settings modules
            # are library classes (no main()), imported via `import baxter_interface`.
            # Only calibrate_arm is a runnable node.
            'Calibrate = baxter_interface.calibrate_arm:main',
        ],
    },
)
