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

If I had more time to work on this, I'd implement a solution using Kafka Connect to stream changes to a DB like TimescaleDB but Kafka Connect configuration is notoriously finicky and time-consuming.

For deploying this to more computers, I'd use Ansible for deploying the kafka producers on the device.


4) For any message-level transformations, I'd consider using Kafka Streams if the tranformations need to be done before it gets to the users. For data validation, message level checking can be done in kafka streams or if it requires checking against external data sources, it's probably best to do this in a DB.

5) Depends on the bottleneck. If all 100 devices are running in an on-prem network, there's a high chance that the network could be a bottleneck before it gets to Kafka. In this this case, I'd think about implementing message level compression, and try and get a better network switch.

If the bottleneck is in Kafka, it can be scaled horizontally relatively easily by increasing the number of kafka nodes.

If TimescaleDB was adopted, I'd make sure that it is horizonally scaled in an HA configuration.

6) To answer the question of "Load waveforms produced by two different enery reduction algorithms", we need to know which device, and which algorithm it was running. The easiest way would be to embed this information along with the message sent to Kafka. If that's not possible to do from the the kafka producer, I'd add that information into another topic and join it at query time (i.e. in the DB).

7) Firstly for data integrity in storage, that would rely on the managed Kafka setup as Kafka already provies several strategies for better integrity. Kafka is a distributed immutable log that ensures the replicated data to be in consensus using the Raft algorithm.

For transit, I'd implement a different serializer/deserializer that includes a checksum to the message.

