import argparse
import datetime
import json
import os
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
        producer.send(
            'joulescope_sensor_data',
            key=device_id.encode('utf-8'),
            value={'data': data}
        )
        time.sleep(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--device_id', required=False, default=os.environ.get('DEVICE_ID'))
    parser.add_argument('-b', '--boostrap_server', required=False, default=os.environ.get('BOOTSTRAP_SERVER'))
    args = parser.parse_args()
    if not args.device_id or not args.boostrap_server:
        raise ValueError('Device ID or bootstrap server not configured')
    run(args.device_id, args.boostrap_server)
