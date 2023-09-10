import argparse
import datetime
import json
import os
import time
import numpy as np

from fake_streambuffer import FakeStreamBuffer, NumpyEncoder, value_serializer
from kafka import KafkaProducer


def splitter(sample_data: dict):
    start = sample_data['time']['range']['value'][0]
    end = sample_data['time']['range']['value'][1]

    num_measurements = len(sample_data['signals']['current']['value'])
    yield from (
        {'timestamp': timestamp, 'current': current, 'voltage': voltage}
        for timestamp, current, voltage in
        zip(
            np.linspace(start, end, num_measurements),
            sample_data['signals']['current']['value'],
            sample_data['signals']['voltage']['value'],
        )
    )


def run(device_id: str, bootstrap_server: str):
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_server,
        value_serializer=value_serializer
    )

    while True:
        streambuf = FakeStreamBuffer(datetime.datetime.now())
        data = streambuf.samples_get(0, 10)
        for msg in splitter(data):
            producer.send(
                'joulescope_sensor_data',
                key=device_id.encode('utf-8'),
                value=msg
            )
        time.sleep(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--device_id', required=False, default=os.environ.get('DEVICE_ID'))
    parser.add_argument('-b', '--boostrap_server', required=False, default=os.environ.get('BOOTSTRAP_SERVER'))
    args = parser.parse_args()
    if not args.device_id or not args.boostrap_server:
        raise ValueError('Device ID or bootstrap server not configured')
    print(f'{args.device_id=} {args.boostrap_server=}')
    run(args.device_id, args.boostrap_server)
