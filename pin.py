from enum import Enum


# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 2/3


class PinType(Enum):
    PT_VOLTAGE = 0
    PT_RESISTOR = 1
    PT_INVALID = 2


class Pin:
    def __init__(self, ads, channel: int, type: PinType):
        self.__ads = ads
        self.channel = channel
        self.type = type
        assert self.type != PinType.PT_INVALID

    def get_value(self):
        assert self.type != PinType.PT_INVALID
        return self.__to_voltage() if self.type == PinType.PT_VOLTAGE else self.__to_resistor()

    def __to_voltage(self):
        # index = (self.channel - 1) % 4 # forward numeration
        index = 3 - ((self.channel-1) % 4) # reverse numeration
        print(f'read index: {index}')
        value = self.__ads.read_adc(index, gain=GAIN)
        voltage = (value / 32768) * 6.144
        return voltage

    def __to_resistor(self):
        # index = (self.channel - 1) % 4 # forward numeration
        index = 3 - ((self.channel - 1) % 4)  # reverse numeration
        print(f'read index: {index}')
        value = self.__ads.read_adc(index, gain=GAIN)
        R1 = 3300
        voltage = (value / 32768) * 6.144
        Rx = (R1 * voltage) / (5 - voltage)
        return Rx
