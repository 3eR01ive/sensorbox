import time
import serial

from bluetooth import *

from pids import Pids
from devices import Devices
from sensors import Sensors


ECU_ADDR_H = "7E2"  # HVECU address (Hybrid contol module)
ECU_R_ADDR_H = "7EA"  # Responses sent by HVECU (Hybrid contol module) 7E2/7EA
ECU_ADDR_E = "7E0"  # Engine ECU address
ECU_R_ADDR_E = "7E8"  # Responses sent by Engine ECU - ECM (engine control module) 7E0/7E8
ECU_ADDR_T = "7E1"  # Transmission ECU address (transmission control module)
ECU_R_ADDR_T = "7E9"  # Responses sent by Transmission ECU - TCM (transmission control module) 7E1/7E9
ECU_ADDR_I = "7C0"  # ICE ECU address
ECU_R_ADDR_I = "7C8"  # Responses sent by ICE ECU address 7C0/7C8
ECU_ADDR_B = "7E3"  # Traction Battery ECU address
ECU_R_ADDR_B = "7EB"  # Responses sent by Traction Battery ECU - 7E3/7EB
ECU_ADDR_P = "7C4"  # Air Conditioning
ECU_R_ADDR_P = "7CC"  # Responses sent by Air Conditioning ECU - 7C4/7CC
ECU_ADDR_S = "7B0"  # Skid Control address ECU
ECU_R_ADDR_S = "7B8"  # Responses sent by 7B0 Skid Control ECU 7B0/7B8

ELM_R_OK = "OK\r"
ELM_MAX_RESP = '[0123456]?$'


class Obd:
    def __init__(self):
        self.sensors = Sensors()

        # sensor = self.sensors.get_sensor("coolant")
        # sensor.set_input(137)
        # print(sensor.get_value())

        self.devices = Devices()
        self.pids = Pids()

        for device in self.devices.get_devices():
            for pin in device.pins():
                print(f"channel: {pin.channel}, type: {pin.type}, value: {pin.get_value()}")

        for name in self.sensors.get_sensors_names():
            sensor = self.sensors.get_sensor(name)
            channel = sensor.get_channel()
            pin = self.devices.get_pin_by_channel(channel=channel)
            pin_value = pin.get_value()

            sensor.set_input(pin_value)

            sensor_value = sensor.get_value()
            print(f"sensor name: {name}, channel: {channel}, input: {pin_value}, value: {sensor_value}")


        self.linefeeds = False
        self.echo = False
        self.headers = False
        self.socket = None
        self.rfcomm = '/dev/rfcomm0'

        self.connected = False

        self.silent_command = set()
        self.silent_command.add("010D")
        self.silent_command.add("010C")

        self.responce = dict()
        self.responce['ATZ'] = "ELM327 v1.5\n"
        self.responce['ATE0'] = "OK"
        self.responce['ATM0'] = "OK"
        self.responce['ATL0'] = "OK"
        self.responce['ATST62'] = "OK"
        self.responce['ATS0'] = "OK"
        self.responce['AT@1'] = "OBDII to RS232 Interpreter"
        self.responce['ATI'] = "ELM327/ELM-USB v1.0 (c) SECONS Ltd.\n"
        self.responce['ATH0'] = "OK"
        self.responce['ATH1'] = "OK"
        self.responce['ATAT1'] = "OK"
        self.responce['ATAT2'] = "OK"
        self.responce['ATDPN'] = "A0"

        self.responce['ATSP0'] = "NO DATA"
        self.responce['ATSP1'] = "NO DATA"
        self.responce['ATSP2'] = "NO DATA"
        self.responce['ATSP3'] = "NO DATA"
        self.responce['ATSP4'] = "NO DATA"
        self.responce['ATSP5'] = "NO DATA"
        self.responce['ATSP6'] = "OK"
        self.responce['ATSP7'] = "NO DATA"
        self.responce['ATSP8'] = "NO DATA"

        self.responce['0100'] = '41 00 FF FF FF FF\r'  # list pids
        self.responce['0120'] = '41 20 FF FF FF FF\r'  # list pids
        self.responce['0140'] = '41 40 FF FF FF FF\r'  # list pids
        self.responce['0160'] = '41 60 FF FF FF FF\r'  # list pids

        self.responce['01781'] = '41 78 10 11\r'  # EGT 1
        self.responce['01791'] = '41 79 00 00\r'  # EGT 2

        self.responce['01701'] = '41 70 00 00 00 00 17\r'  # boost

        # self.responce['0178'] = '41 78 10 11 \r' # EGT 1
        # self.responce['0179'] = '41 79 08 55 \r' # EGT 2
        # self.responce['0170'] = '41 70 00 FF \r' # boost

        self.responce['015C'] = '41 5C 30\r'  # oil temp
        self.responce['015C1'] = '41 5C 30\r'  # oil temp

        self.responce['0114'] = '41 14 FF'  # afr custom (A*(0.06)) + 7.35
        self.responce['0111'] = '41 11 FF'  # asd

        self.responce['010D1'] = '41 0D 30\r'  # speed
        self.responce['010C1'] = '41 0C 11 00\r'  # rpm

        self.responce['010C'] = '41 0C 11 00\r'  # rpm
        self.responce['010D'] = '41 0D 30\r'  # speed
        self.responce['0105'] = '41 05 64\r'  # coolant

        self.responce['010B'] = '41 0B 00\r'  # Intake manifold absolute pressure
        self.responce['0110'] = '41 10 00 00\r'  # Mass air flow sensor (MAF) air flow rate
        self.responce['0133'] = '41 33 00\r'  # Absolute Barometric Pressure
        self.responce['010A'] = '41 0A 55\r'  # Fuel Pressure

    def __connect(self, full=False):

        if full:
            print('creating server socket...')
            server_sock = BluetoothSocket(RFCOMM)
            server_sock.bind(("", PORT_ANY))
            server_sock.listen(1)

            port = server_sock.getsockname()[1]
            print('server socket created!')

            print('advertising device...')
            uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
            advertise_service(server_sock, "Obd",
                              service_id=uuid,
                              service_classes=[uuid, SERIAL_PORT_CLASS],
                              profiles=[SERIAL_PORT_PROFILE]
                              )

            print('device advertised!')

            print
            "Waiting for connection on RFCOMM channel %d" % port

            client_sock, client_info = server_sock.accept()
            print
            "Accepted connection from ", client_info
            self.socket = client_sock
            return

        self.connected = False
        print('connecting...')

        while not self.connected:
            try:
                com = serial.Serial(self.rfcomm, 19200, timeout=1)
                com.close()
                self.connected = True
                print('connected!')
            except:
                time.sleep(1)
                print('retry connecting...')

        self.socket = serial.Serial(self.rfcomm, 19200, timeout=1)

    def __write(self, resp):

        n = "\r\n" if self.linefeeds else "\r"

        resp += n + ">"

        # if self.echo:
        #     resp = echo_cmd + n + resp

        if 'write' in dir(self.socket):
            self.socket.write(resp)
        else:
            self.socket.send(resp)

    def __read(self):
        buffer = ""

        while True:

            if 'read' in dir(self.socket):
                c = self.socket.read().decode()
            else:
                c = self.socket.recv(1).decode()
            if c == '\n':
                break

            if c == '\r':
                break

            buffer += c

        return buffer

    def __setup_settings(self, command):
        if command == "ATL0":
            self.linefeeds = False
        if command == "ATL1":
            self.linefeeds = True
        if command == "ATH0":
            self.headers = False
        if command == "ATH1":
            self.headers = True
        if command == "ATE0":
            self.echo = False
        if command == "ATE1":
            self.echo = True

    def loop(self):
        while True:
            time.sleep(0)

            try:
                command = self.__read()

                if command == '':
                    continue

                if command not in self.silent_command:
                    print("< {}".format(command))

                if self.pids.has_pid_by_key(command):

                    self.__setup_settings(command)

                    pid = self.pids.get_pid_by_key(command)
                    sensor = self.sensors.get_sensor(pid.name)

                    channel = sensor.get_channel()
                    pin = self.devices.get_pin_by_channel(channel=channel)
                    pin_value = pin.get_value()

                    print(f"pin({channel}) value: {pin_value}")

                    sensor.set_input(pin_value)

                    sensor_value = sensor.get_value()

                    print(f"sensor({pid.name}) value: {sensor_value}")

                    pid_value = pid.encode(sensor_value)

                    print(f"pid({pid.name}) value: {pid_value}")

                    res = "41 " + pid.key[2:4] + " " + str(hex(int(pid_value))[2:]) # tmp for only A value in formula

                    self.__write(res)

                    if command not in self.silent_command:
                        print("> {}".format(res))

                elif command in self.responce:

                    self.__setup_settings(command)

                    res = self.responce[command]

                    self.__write(res)

                    if command not in self.silent_command:
                        print("> {}".format(res))
                else:
                    self.__write("NO DATA")
                    print("(new) > {}".format("False"))

            except Exception as e:
                print(e)

                self.connected = False
                self.__connect(full=True)
