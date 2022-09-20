using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Basic_Streaming.NET.Models
{
    public class StreamInfoModel : INotifyPropertyChanged
    {

        private string _deviceName;

        public string DeviceName
        {
            get { return _deviceName; }
            set
            {
                _deviceName = value;
                RaisePropertyChanged("DeviceName");
            }
        }

        private string _pipelineStatus;

        public string PipelineStatus
        {
            get { return _pipelineStatus; }
            set
            {
                _pipelineStatus = value;
                RaisePropertyChanged("PipelineStatus");
            }
        }

        private int _sensorsConnected;

        public int SensorsConnected
        {
            get { return _sensorsConnected; }
            set
            {
                _sensorsConnected = value;
                RaisePropertyChanged("SensorsConnected");
            }
        }

        private int _totalChannels;

        public int TotalChannels
        {
            get { return _totalChannels; }
            set
            {
                _totalChannels = value;
                RaisePropertyChanged("TotalChannels");
            }
        }

        private string _streamTime;

        public string StreamTime
        {
            get { return _streamTime; }
            set
            {
                _streamTime = value;
                RaisePropertyChanged("StreamTime");
            }
        }

        private int _packetsLost;

        public int PacketsLost
        {
            get { return _packetsLost; }
            set
            {
                _packetsLost = value;
                RaisePropertyChanged("PacketsLost");
            }
        }

        private int _framesCollected;

        public int FramesCollected
        {
            get { return _framesCollected; }
            set
            {
                _framesCollected = value;
                RaisePropertyChanged("FramesCollected");
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected void RaisePropertyChanged(string propertyName)
        {
            PropertyChangedEventHandler handler = PropertyChanged;
            if (handler != null)
            {
                handler(this, new PropertyChangedEventArgs(propertyName));
            }
        }

        public override bool Equals(object obj)
        {
            return base.Equals(obj);
        }

        public override int GetHashCode()
        {
            return base.GetHashCode();
        }
    }
}
