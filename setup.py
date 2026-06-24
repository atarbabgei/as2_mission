import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'as2_mission'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        # config files (config.yaml + controller plugin configs)
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
        # mission scripts (so launch/`ros2 run` can find them in the install space)
        (os.path.join('share', package_name, 'missions'),
            glob('as2_mission/missions/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='atarbabgei',
    maintainer_email='atarbabgei@gmail.com',
    description='Bring-up and mission orchestration for an AeroStack2 PX4/Pixhawk drone.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'square_mission = as2_mission.missions.square_mission:main',
        ],
    },
)
