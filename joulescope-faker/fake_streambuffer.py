# a fake instance of the StreamBuffer API
import numpy as np
from datetime import timedelta, datetime
import json


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


value_serializer=lambda v: json.dumps(v, cls=NumpyEncoder).encode('utf-8')


class FakeStreamBuffer:
    def __init__(self, start_time):
        self._start_time = start_time

    def samples_get(self, start, stop, fields=None):
        # start/stop are second offsets from the start time
        # data is randomly generated
        input_sampling_frequency = 1
        output_sampling_frequency = 1

        if fields is None:
            fields = ['current', 'voltage']

        units = {
            'current': 'A',
            'voltage': 'V'
        }
        t1 = self._start_time.timestamp()
        t2 = (self._start_time + timedelta(seconds=stop - start)).timestamp()

        result = {
            'time': {
                'range': {'value': [t1, t2], 'units': 's'},
                'delta': {'value': t2 - t1, 'units': 's'},
                'sample_id_range': {'value': [start, stop], 'units': 'samples'},
                'samples': {'value': stop - start, 'units': 'samples'},
                'input_sampling_frequency': {'value': input_sampling_frequency, 'units': 'Hz'},
                'output_sampling_frequency': {'value': output_sampling_frequency, 'units': 'Hz'},
                'sampling_frequency': {'value': output_sampling_frequency, 'units': 'Hz'},
            },
            'signals': {},
        }

        for f in fields:
            d = np.random.random(stop - start)
            result['signals'][f] = {'value': d, 'units': units.get(f)}
        return result


if __name__ == '__main__':
    fsb = FakeStreamBuffer(datetime.now())
    print(json.dumps({'data': fsb.samples_get(0, 10)}, cls=NumpyEncoder))
