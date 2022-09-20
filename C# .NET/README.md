# Delsys API - Basic Streaming (C#) #

## Overview ##

An application showcasing core Data streaming functionalities of the Delsys API, these features include:
* Pair/Configure Trigno Sensors
* Device Streaming
* Export Data to CSV

The purpose of this repository is to familiarize yourself with how the Delsys API is used to stream Trigno data in real time through code examples. 

**Hardware Requirements**:

Trigno Basestation/Lite

https://delsys.com/systems/

**Software Requirements**:

Microsoft Visual Studio:
https://visualstudio.microsoft.com/

Delsys API:
https://delsys.com/api/
*Users must have an active key/license to run the API & this application.

## Getting Started ##

1) Enter your key/license strings into DeviceStreaming.xaml.cs 
2) Build & Run the solution
3) Choose Device Streaming then click Load Trigno Device (See console output to see initalizing steps)
4) (Optional) If it is your first time with the system, click Pair Additional Sensors then proceed with pairing the sensors. Click Finish and Scan to complete pairing process. 
   Note: Once sensors have been paired to the system you will only need to run a scan to find them, even after the program has been closed.
5) Once scan is complete, all of your sensors will be listed in the Paired Sensors window. Use checkbox to select sensors for streaming (unselected sensors will not output data).
6) (Optional) Change sensor mode by using the selection dropdown.
7) Click Arm Pipeline once sensors have been selected and modes are set. 
8) Start Stream to begin data collection
9) Once Stopped, you can either stream again, export the data to CSV, or reset the pipeline. 
    Note: The pipeline must be reset if you want to pair/scan/select sensors again. If you are using the same sensor configuration, you may start/stop the data streaming continuously without resetting.



