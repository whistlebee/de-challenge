# DE challenge


1a) From what I can see, the drivers available on github aren't sufficient alone to build a data streaming system.
The drivers can be used to extract the signals from the device but there needs to be a __reliable__ way to convert these to a data stream that we can send over the network.
Especially since the requirement is to send the data to a cloud platform, we'll need to account for network failures.

1b) I see this project needing a near real-time system rather than a true real-time system. Near real time systems can be considered almost like a batch system with short periods.
So in a way, scheduled batch uploads is not too different from a near real-time streaming system.
This project doesn't need a true real-time system as the impact of missing a deadline is low.
There are also additional challenges in building a true real-time system such as requiring almost
real-time operating system (RTOS) that is likely not supported by the joulescope drivers.


2) The data produced by joulescope is several time series signals at most 2 million samples per second.
Users of the data need efficient access into specific time-ranges as well as by other fields such as the device.
With these requirements in mind, I'd consider using a time-series database such as TimescaleDB.
Alternatively, a data-lake approach may work too using tools such as Spark Streaming on top of the kafka stream.

Some people consider a commit-log system like Kafka suitable for persistent storage and that may be true for some usecases.
However, my experience with Kafka was that it's significantly harder to work with if treated this way.
Especially in the age where storage is cheap but engineer-time and compute is expensive,
I feel that using Kafka more for data transport and leaving querying to a relational database will be easier for users to query.

3) I'll build this system using Apache Kafka as I'm most familiar with this.
There are other alternatives such as AWS Kinesis, GCP Pubsub, and Azure Event hubs but I feel that sticking with proven open-source technologies is also generally better
in terms of community support, and being able to test locally without the need of internet access.

For small teams, it's more time-effective for engineers to use managed instances that to operate a kafka cluster (or any other distributed systems).

Therefore deploying to a production system, I'd deploy to one of:
* Confluent Cloud (managed Kafka)
* Azure Event Hubs (using kafka compatible API)
* Deploy a kafka operator to a managed K8s instance.

Specifically for this prototype I'll be using Redpanda, a fully Kafka-compatible system since it's got slightly easier than Apache Kafka for local testing setups.

If I had more time to work on this, I'd fully implement a solution using Kafka Connect to stream changes to a DB like TimescaleDB but Kafka Connect configuration is notoriously finicky and time-consuming.

