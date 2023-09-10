import argparse
import datetime
import json
import time

import numpy as np
from fake_streambuffer import FakeStreamBuffer
from kafka import KafkaProducer


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def run(device_id: str, bootstrap_server: str):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_server,
        value_serializer=lambda v: json.dumps(v, cls=NumpyEncoder).encode('utf-8')
    )

    while True:
        streambuf = FakeStreamBuffer(datetime.datetime.now())
        data = streambuf.samples_get(0, 10)
        producer.send('joulescope_sensor_data', {
            'device_id': device_id,
            'data': data
        })
        time.sleep(10)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('device_id')
    parser.add_argument('boostrap_server')
    args = parser.parse_args()
    run(args.device_id, args.boostrap_server)
