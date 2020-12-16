from datetime import datetime
import paho.mqtt.client as mqtt
import threading
import logging
import math
import bluetooth as bt
import bluetooth._bluetooth as bluez
from queue import Queue
from device_classes import device_classes
from inqrssi import device_inquiry_with_with_rssi, read_inquiry_mode, write_inquiry_mode

from bluetooth.ble import DiscoveryService
from bluetooth.ble import BeaconService


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class BTProxMQTT:
    def __init__(self, host, port=1883, base_topic='sensors/Bluetooth/', username=None, password=None, ):
        self.base_topic = base_topic
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._inquiry_queue = Queue()

        self.client = mqtt.Client()
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def run(self):
        RepeatTimer(10.0, self.discover_bt).start()
        RepeatTimer(10.0, self.discover_btle).start()
        RepeatTimer(5.0, self.discover_beacons).start()
        RepeatTimer(25.0, self.detailed_inquiry).start()

    def send_reading(self, topic, value):
        self.client.publish(self.base_topic + topic, value)

    def calculate_distance(self, txpower, rssi):
        return math.sqrt(math.pow(10, (txpower - rssi) / 10))

    def detailed_inquiry(self):
        while not self._inquiry_queue.empty():
            address = self._inquiry_queue.pop()
            if not address:
                continue

        # We want to get the RSSI and the name at the very least
        # for every device

    def queue_detailed_inquiry(self, address):
        self._inquiry_queue.put(address)

    def discover_bt(self):
        logging.info("Scanning bluetooth devices")
        devices = bt.discover_devices(duration=10, flush_cache=True, lookup_names=True, lookup_class=True)
        timestamp = datetime.now().isoformat()
        logging.info("Discovered %d devices" % len(devices))
        for address, name, devclass in devices:
            self.queue_detailed_inquiry(address)
            self.send_reading('/'.join([address, "name"]), name)
            self.send_reading('/'.join([address, "class"]), device_classes[str(devclass)])
            self.send_reading('/'.join([address, "le"]), False)
            self.send_reading('/'.join([address, "last_seen"]), timestamp)

        sock = bluez.hci_open_dev(0)
        mode = read_inquiry_mode(sock)
        if mode != 1:
            results = write_inquiry_mode(sock, 1)
        results = device_inquiry_with_with_rssi(sock)
        for (address, rssi) in results:
            # Power isn't returned so we guess it's 23
            self.send_reading('/'.join([address, "rssi"]), rssi)
            self.send_reading('/'.join([address, "power"]), 23)
            self.send_reading('/'.join([address, "distance"]), self.calculate_distance(23, rssi))

    def discover_btle(self):
        if DiscoveryService is None:
            return

        logging.info("Scanning lowenergy devices")
        ledevices = DiscoveryService().discover(10)
        timestamp = datetime.now().isoformat()
        logging.info("Discovered %d low energy devices" % len(ledevices.keys()))
        for address, name in ledevices.items():
            if name is not None and len(name) == 0:
                name = None
            if name is not None:
                self.send_reading('/'.join([address, "name"]), name)
            self.send_reading('/'.join([address, "le"]), True)
            self.send_reading('/'.join([address, "last_seen"]), timestamp)

    def discover_beacons(self):
        if BeaconService is None:
            return
        logging.info("Scanning beacon devices")
        beacondevices = BeaconService().scan(5)
        timestamp = datetime.now().isoformat()
        logging.info("Discovered %d beacon devices" % len(beacondevices.keys()))
        for address, data in beacondevices.items():
            self.send_reading('/'.join([address, "uuid"]), data[0])
            self.send_reading('/'.join([address, "major"]), data[1])
            self.send_reading('/'.join([address, "minor"]), data[2])
            self.send_reading('/'.join([address, "power"]), data[3])
            self.send_reading('/'.join([address, "rssi"]), data[4])
            self.send_reading('/'.join([address, "distance"]), self.calculate_distance(data[3], data[4]))
            self.send_reading('/'.join([address, "le"]), True)
            self.send_reading('/'.join([address, "last_seen"]), timestamp)


def main():
    logging.basicConfig(level=logging.DEBUG)
    btmqtt = BTProxMQTT("192.168.1.3")
    btmqtt.run()


if __name__ == '__main__':
    main()
