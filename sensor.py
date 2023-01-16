class Sensor:
    def __init__(self, name, channel, inputs, values):

        assert len(inputs) >= 2
        assert len(values) >= 2
        assert len(inputs) == len(values)

        self.__name = name
        self.__channel = channel
        self.__inputs = inputs
        self.__values = values
        self.__current_input = 0

    def get_channel(self):
        return self.__channel

    def set_input(self, input):
        self.__current_input = input

    def get_value(self):
        return self.__convert_input_to_value(self.__current_input)

    def __linear_interpolate(self, value, _from, _to):
        assert _from < _to
        assert 0 <= _from <= len(self.__inputs)
        assert 0 <= _to <= len(self.__inputs)

        input_from = self.__inputs[_from]
        input_to = self.__inputs[_to]

        assert value >= input_from
        assert value <= input_to
        assert input_to - input_from > 0

        multiplier = (value - input_from) / (input_to - input_from)

        value_from = self.__values[_from]
        value_to = self.__values[_to]

        interpolated_value = value_from + ((value_to - value_from) * multiplier)

        return interpolated_value

    def __convert_input_to_value(self, input_value):
        # _from = 0
        # _to = len(self.__inputs) - 1

        # for i, input in enumerate(self.__inputs):
        #     if input_value >= input:
        #         _from = i
        #         break
        #
        # for i, input in reversed(list(enumerate(self.__inputs))):
        #     if input_value <= input:
        #         _to = i
        #         break

        for i in range(0, len(self.__inputs) - 1):
            a = self.__inputs[i]
            b = self.__inputs[i + 1]

            def beetween(x, a, b):
                return a <= x <= b or a >= x >= b

            if beetween(input_value, a, b):
                return self.__linear_interpolate(input_value, i, i + 1)

        return -1
