from setuptools import setup

setup(
    name='tempcontrol',
    version='1.1',
    packages=['tempcontrol'],
    include_package_data=True,
    install_requires=[
        'flask', 'matplotlib', 'paho-mqtt', 'python-gammu',
    ],
)
