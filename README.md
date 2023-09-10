# DE challenge


## 1

### a
From what I can see, the drivers available on github aren't sufficient alone to build a data streaming system.
The drivers can be used to extract the signals from the device but there needs to be a __reliable__ way to convert these to a data stream that we can send over the network.
Especially since the requirement is to send the data to a cloud platform, we'll need to account for network failures.

### b
I see this project needing a near real-time system rather than a true real-time system. Near real time systems can be considered almost like a batch system with short periods.
So in a way, scheduled batch uploads is not too different from a near real-time streaming system.
This project doesn't need a true real-time system as the impact of missing a deadline is low.
There are also additional challenges in building a true real-time system such as requiring almost
real-time operating system (RTOS) that is likely not supported by the joulescope drivers.


## 2
The data produced by joulescope is several time series signals at most 2 million samples per second.
Users of the data need efficient access into specific time-ranges as well as by other fields such as the device.
With these requirements in mind, I'd consider using a time-series database such as TimescaleDB.
Alternatively, a data-lake approach may work too using tools such as Spark Streaming on top of the kafka stream.

Some people consider a commit-log system like Kafka suitable for persistent storage and that may be true for some usecases.
However, my experience with Kafka was that it's significantly harder to work with if treated this way.
Especially in the age where storage is cheap but engineer-time and compute is expensive,
I feel that using Kafka more for data transport and leaving querying to a relational database will be easier for users to query.

## 3
I'll build this system using Apache Kafka as I'm most familiar with this.
There are other alternatives such as AWS Kinesis, GCP Pubsub, and Azure Event hubs but I feel that sticking with proven open-source technologies is also generally better
in terms of community support, and being able to test locally without the need of internet access.

For small teams, it's more time-effective for engineers to use managed instances that to operate a kafka cluster (or any other distributed systems).

Therefore deploying to a production system, I'd deploy to one of:
* Confluent Cloud (managed Kafka)
* Azure Event Hubs (using kafka compatible API)
* Deploy a kafka operator to a managed K8s instance.

Specifically for this prototype I'll be using Redpanda, a fully Kafka-compatible system since it's got slightly easier than Apache Kafka for local testing setups.

For deploying this to more computers, I'd use Ansible for deploying the kafka producers on the device.

### How to run the code

Prerequisites

* Linux/macOS
* Docker Compose
* curl
* A Postgres client psql, datagrip etc.

How to run:

```console
$ mkdir connect-plugins
$ curl -s -L https://repo1.maven.org/maven2/org/apache/camel/kafkaconnector/camel-postgresql-sink-kafka-connector/3.18.2/camel-postgresql-sink-kafka-connector-3.18.2-package.tar.gz | tar xvz - -C connect-plugins/
$ curl -s -L -o connect-plugins/camel-postgresql-sink-kafka-connector/postgres-42.4.3.jar https://repo1.maven.org/maven2/org/postgresql/postgresql/42.4.3/postgresql-42.4.3.jar
$ docker-compose up -d
$ curl localhost:8083/connectors -H 'Content-Type: application/json' -d @connector-config.json
```
A topic should be created in kafka. See http://localhost:8080/topics/joulescope_sensor_data?p=-1&s=50&o=-1#messages

Check using your postgres client. Example using `pgcli`:

```
(joulescope-faker) hjkim@deskbee:~/projects/de-challenge$ PGPASSWORD=password pgcli -h localhost -p 5432 -U postgres
Server: PostgreSQL 14.7 (Ubuntu 14.7-1.pgdg22.04+1)
Version: 3.5.0
Home: http://pgcli.com
postgres@localhost:postgres> select * from joulescale_measurements limit 100;
+-------------------------------+-----------------------+----------------------+-------------------------------+
| timestamp                     | current               | voltage              | _loaded_at                    |
|-------------------------------+-----------------------+----------------------+-------------------------------|
| 2023-09-10 07:30:09.399441+00 | 0.46759152223353384   | 0.5594680268607981   | 2023-09-10 08:24:17.701904+00 |
| 2023-09-10 07:30:10.510552+00 | 0.0719368457217967    | 0.14434397408735467  | 2023-09-10 08:24:17.713782+00 |
| 2023-09-10 07:30:11.621663+00 | 0.2250360432956735    | 0.8104905345235046   | 2023-09-10 08:24:17.717303+00 |
| 2023-09-10 07:30:12.732774+00 | 0.7623198239510987    | 0.9640394220807117   | 2023-09-10 08:24:17.720812+00 |
| 2023-09-10 07:30:13.843885+00 | 0.62344599997776      | 0.29048972151238384  | 2023-09-10 08:24:17.72379+00  |
```

## 4

For any message-level transformations, I'd consider using Kafka Streams if the tranformations need to be done before it gets to the users. For data validation, message level checking can be done in kafka streams or if it requires checking against external data sources, it's probably best to do this in a DB.

## 5

Depends on the bottleneck. If all 100 devices are running in an on-prem network, there's a high chance that the network could be a bottleneck before it gets to Kafka. In this this case, I'd think about implementing message level compression, and try and get a better network switch.

If the bottleneck is in Kafka, it can be scaled horizontally relatively easily by increasing the number of kafka nodes.

If TimescaleDB was adopted, I'd make sure that it is horizonally scaled in an HA configuration.

## 6

To answer the question of "Load waveforms produced by two different enery reduction algorithms", we need to know which device, and which algorithm it was running. The easiest way would be to embed this information along with the message sent to Kafka. If that's not possible to do from the the kafka producer, I'd add that information into another topic and join it at query time (i.e. in the DB).

## 7
Firstly for data integrity in storage, that would rely on the managed Kafka setup as Kafka already provies several strategies for better integrity. Kafka is a distributed immutable log that ensures the replicated data to be in consensus using the Raft algorithm.

For transit, I'd implement a different serializer/deserializer that includes a checksum to the message.

To handle data transmission failures, I'd implement a small in-memory circular buffer to store the failed transmissions that gets retried with exponential backoff. For a more resilient solution, it should persist to disk.


## 8

For using this system for other applications, a most of the infrastructure will be reusuable. I'd just make sure to document the procedure for reproducing this, and add recommendations on things like naming-conventations, splitting up usecases by schema (Timescale) etc.

On the producer side, I'd make an internal library for other applications to reuse the common code.
