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

