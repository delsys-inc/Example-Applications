classdef Channel < handle
    %Channel class wrapper for FileReaderAPI%   
    
    properties (Access = private)
       channel;
    end
    
    methods  
        function obj = Channel(channel)
        %Returns channel object%
        
           obj.channel = channel;
        end
        
        function name = Name(obj)
        %Channel Name - This name can be set prior to a data stream%
        
            name = string(obj.channel.Name);
        end
        
        function sampleRate = SampleRate(obj)
        %Channel Sample Rate - The amount data points per second this
        %channel was collected at%
        
            sampleRate = double(obj.channel.SampleRate);
        end
        
        function units = Units(obj)
        %Channel Unit - The unit of measurement for this channel%
        
            units = string(obj.channel.Units);
        end
        
        function rangeMin = RangeMin(obj)
        %Channel Minimum Range - The minimum value a data point can be%
        
            rangeMin = double(obj.channel.RangeMin);
        end
        
        function rangeMax = RangeMax(obj)
        %Channel Maximum Range - The maximum value a data point can be%
        
            rangeMax = double(obj.channel.RangeMax);
        end
        
        function logChannel = LogThisChannel(obj)
        %Channel Logging - Was this channel displayed during data collection%
        
            logChannel = obj.channel.LogThisChannel;
        end
        
        function internalName = InternalName(obj)
        %Channel Logging - Was this channel displayed during data collection%
        
            internalName = string(obj.channel.InternalName);
        end
        
        function channelType = ChannelType(obj)
        %Channel Type - Type of channel (ie. EMG, ACC, GYRO)%
        
            channelType = string(obj.channel.ChannelType);
        end
        
        function samplesPerFrame = SamplesPerFrame(obj)
        %Channel Samples Per Frame - Amount of data points received on this channel per frame%
        
            samplesPerFrame = double(obj.channel.SamplesPerFrame);
        end
        
        
        function localChannelNumber = LocalChannelNumber(obj)
        %Channel Local Index - Channel index based on all the sensor component channels%
        
            localChannelNumber = double(obj.channel.LocalChannelNumber);
        end
        
        function parsedData = Data(obj)
        %Channel Data - All of the data associated with this channel during the collection%
        
            data = obj.channel.Data;
            frameCount = data.Count();
            firstFrameData = data.Item(0).Item2;
            dataCountEachFrame = firstFrameData.Count();
            
            parsedData = zeros(1,frameCount*dataCountEachFrame);
            for frame = 1:frameCount
                frameDataTuple = data.Item(frame-1);
                frameData = frameDataTuple.Item2();
                for dataPoint = 1:dataCountEachFrame
                    frameIndexOffset = (frame-1)*dataCountEachFrame;
                    parsedData(frameIndexOffset + dataPoint) = frameData.Item(dataPoint-1);
                end
            end
        end
    end
end

