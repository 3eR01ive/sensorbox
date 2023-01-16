from obd import Obd
# from devices import Devices
# from sensors import Sensors
#
# devices = Devices()
#
# for device in devices.get_devices():
#     for pin in device.pins():
#         print(f"channel: {pin.channel}, type: {pin.type}, value: {pin.get_value()}")
#
# sensors = Sensors()
# for name in sensors.get_sensors_names():
#     sensor = sensors.get_sensor(name)
#     channel = sensor.get_channel()
#     pin = devices.get_pin_by_channel(channel=channel)
#     pin_value = pin.get_value()
#
#     sensor.set_input(pin_value)
#
#     sensor_value = sensor.get_value()
#     print(f"sensor name: {name}, channel: {channel}, input: {pin_value}, value: {sensor_value}")


obd = Obd()
obd.loop()