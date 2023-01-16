import Adafruit_ADS1x15
from pin import PinType
from pin import Pin


class Device:
    def __init__(self, busnum, address):
        self.__ads = Adafruit_ADS1x15.ADS1115(busnum=busnum, address=address)
        self.__pins = []

    def create_pin(self, channel: int, type: PinType):
        pin = Pin(ads=self.__ads, channel=channel, type=type)
        self.__pins.append(pin)

    def pins(self):
        return self.__pins