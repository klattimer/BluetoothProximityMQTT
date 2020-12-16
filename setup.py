from setuptools import setup
import setuptools

BTPROXMQTT_VERSION = '0.9'
BTPROXMQTT_DOWNLOAD_URL = (
    'https://github.com/klattimer/btproxmqtt/tarball/' + BTPROXMQTT_VERSION
)

setup(
    name='btproxmqtt',
    packages=setuptools.find_packages(),
    version=BTPROXMQTT_VERSION,
    description='Identify presence and hopefully proximity (relative to obstructions) of nearby bluetooth devices.',
    long_description='',
    license='MIT',
    author='Karl Lattimer',
    author_email='karl@qdh.org.uk',
    url='https://github.com/klattimer/BluetoothProximityMQTT',
    download_url=BTPROXMQTT_DOWNLOAD_URL,
    entry_points={
        'console_scripts': [
            'btproxmqtt=btproxmqtt:main'
        ]
    },
    keywords=[
        'smarthome', 'raspberry-pi', 'sensor', 'bluetooth', 'presence', 'distance'
    ],
    install_requires=[
        'paho-mqtt',
        'pybluez',
        'gattlib'
    ],
    data_files=[
        [('etc/systemd/system/', ['data/btproxmqtt.service'])]
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
    ],
)
