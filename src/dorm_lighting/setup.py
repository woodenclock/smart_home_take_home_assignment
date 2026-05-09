from setuptools import find_packages, setup

package_name = 'dorm_lighting'

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
    maintainer='Lee Sungmin',
    maintainer_email='luckyisland3710@gmail.com',
    description='Scheduled smart lighting controller bridging ROS 2 and MQTT for NTU dorm rooms.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'light_controller = dorm_lighting.light_controller:main',   # Create ROS executable command
        ],                                                              # dorm_lighting/light_controller.py → main()
    },
)
