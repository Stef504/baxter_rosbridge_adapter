from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'baxter_ik'

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
    description='Baxter inverse-kinematics and tactile-experiment client (roslibpy/rosbridge based)',
    license='BSD-3-Clause',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ik_baxter = baxter_ik.ik_baxter:main',
            'position_kinematics = baxter_ik.position_kinematics:main',
            'repetitive_ik = baxter_ik.repetitive_ik:main',
            'test = baxter_ik.test:main',
            'daimon_sensor = baxter_ik.daimon_sensor:main',
        ],
    },
)
