classdef Component < handle
    %Component class wrapper for FileReaderAPI% 
    
    properties (Access = private)
       component;
    end
    
    methods  
        function obj = Component(component)
        %Returns component object%
        
           obj.component = component;
        end
        
        function channel = Channel(obj, selectedChannel)
        %Returns channel object at selectedChannels index%
        
            tempChannel = obj.component.Channels.Item(ShiftIndexing(obj, selectedChannel));
            channel = Channel(tempChannel);
        end
        
        function sensorId = SensorId(obj)
        %Component/Sensor ID - Unique ID of the sensor component%
        
            sensorId = double(obj.component.SensorId);
        end

        function componentType = Type(obj)
        %Component Type - Number id associated with the sensor type%
            componentType = double(obj.component.Type);
        end
        
        function modeNumber = ModeNumber(obj)
        %Component Mode - Number id associated with the sensor mode%
        
            modeNumber = double(obj.component.ModeNumber);
        end

        function sensorNumber = SensorNumber(obj)
        %Component/Sensor Pair Number - Assigned number for this sensor during a collection%
        
            sensorNumber = double(obj.component.SensorNumber);
        end

        function batteryPercent = BatteryPercent(obj)
        %Component/Sensor Battery Percent - Battery Percent at time of collection%
        
            batteryPercent = double((obj.component.BatteryPercent / 1)*100);
        end

        function powerOnCount = PowerOnCount(obj)
        %Component/Sensor Power On Count - Amount of times the sensor has been powered on%
        
            powerOnCount = double(obj.component.PowerOnCount);
        end

        function powerOnTime = PowerOnTime(obj)
        %Component/Sensor Power On Time - Amount of time the sensor has been on%
        
            powerOnTime = double(obj.component.PowerOnTime);
        end
        
        function componentName = Name(obj)
        %Component/Sensor Name - This name can be set prior to a data stream%
        
            componentName = string(obj.component.Name);
        end
        
        function firmwareVersion = FirmwareVersion(obj)
        %Component/Sensor Firmware Version - A sensors firmware version at the time of collection%
        
            firmwareVersion = string(obj.component.FirmwareVersion);
        end
        
        
        function channelCount = ChannelCount(obj)
        %Component/Sensor Channel Count - Amount of channels collected by this sensor component%
        
            channelCount = double(obj.component.Channels.Count());
        end

        function data = GetAllData(obj)
        %Return an array of all channel data from this sensor component%
                    
            channelCount = obj.ChannelCount();
            data = cell(channelCount);
            for i = 1:channelCount
                channel = obj.Channel(i);
                data{i} = channel.Data();
            end
        end

        function names = GetAllChannelNames(obj)
        %Return an array of all channel names for this sensor component%
        
            channelCount = obj.ChannelCount();
            names = cell(channelCount);
            for i = 1:channelCount
                channel = obj.Channel(i);
                names{i} = channel.Name();
            end
        end

        function sampleRates = GetAllSampleRates(obj)
        %Return an array of all channel sample rates for this sensor component%
        
            channelCount = obj.ChannelCount();
            sampleRates = cell(channelCount);
            for i = 1:channelCount
                channel = obj.Channel(i);
                sampleRates{i} = channel.SampleRate();
            end
        end
    
        function units = GetAllUnits(obj)
        %Return an array of all channel units for this sensor component%
        
            channelCount = obj.ChannelCount();
            units = cell(channelCount);
            for i = 1:channelCount
                channel = obj.Channel(i);
                units{i} = channel.Units();
            end
        end
    end
    
    methods(Access = private)
        
        % Shifts indexes left by 1 to adjust for the C# language that
        % starts indexing at 0 instead of 1 like matlab
        function shiftedIndex = ShiftIndexing(obj, index)
            shiftedIndex = index - 1;
        end
    end
end

