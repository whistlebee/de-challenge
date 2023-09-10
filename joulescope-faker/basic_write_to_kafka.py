# example of writing some data to a test topic
# note that this is for outside docker, need to change the server if I run it inside docker

import json

from kafka import KafkaProducer


if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers='localhost:19092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    for i in range(100):
        producer.send('test', {'msg': 'hello' + str(i)})

    producer.flush()

