# Delsys API RF integration with Unity

## Requirements
1. Unity version 2021.3.0f1 or greater
2. DelsysAPI version 2.5.3+
3. Trigno sensors and Base Station/Lite running on latest firmware. You can follow the guide [here](http://data.delsys.com/DelsysServicePortal/api/web-examples/updating-firmware.html)

4. An active DelsysAPI key/license. Contact [support](https://delsys.com/support/) if you have any issues.

## Description of the Sample App using Delsys API in RF mode:
1. Open ..\Assets\UnityExample.cs and paste key/license strings (lines 22-23)
1. Open project in Unity Editor; Open Sample Scene located at */Assets/Scenes 
2. Run from editor (play button) or build and run; Text will display "Data source loaded and ready to Scan." if initialization was successful 
3. Click Scan to scan for previously paired sensors or click Pair to pair a sensor to the base (you always have to scan before running a collection)
4. Select sensors by clicking "Select" button once the "Scan Complete" text is displayed 
3. Click "Start" to start data streaming and "Stop" to stop data streaming (UI counter indicates the amount of data packets received from the API - see CollectionDataReady event inside of UnityExample.cs to show parsing of collection data in real-time)


