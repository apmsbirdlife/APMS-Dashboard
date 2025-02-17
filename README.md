--------------------------------------------------------------------------------------------------
APMS (Automated Penguin Monitoring System)
--------------------------------------------------------------------------------------------------
This repository contains the software needed to run the APMS (Automated Penguin Monitoring System).
The system consists of two scales that send continuous weight readings at 100 Hz to a Raspberry Pi 4.
There is also a monitoring circuit, consisting of common off-the-shelf components, to monitor system health.
The system is connected to an RFID detection system designed by BioMark. The BioMark system sends out data via the serial port when an RFID tag is detected.
When a penguin walks over the scales, the data is recorded in a CSV file. Every night, the data is uploaded to the cloud (AWS S3).
System stats can be displayed on a Grafana dashboard that uses InfluxDB to store data.
The system is still very much in beta and can now be used as a platform for further development.

Check the APMS Manual for more information.
--------------------------------------------------------------------------------------------------


