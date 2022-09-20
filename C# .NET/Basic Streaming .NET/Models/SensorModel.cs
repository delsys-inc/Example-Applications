using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Basic_Streaming.NET.Models
{
    public class SensorModel : INotifyPropertyChanged
    {

        private string _sensorName;

        public string SensorName
        {
            get { return _sensorName; }
            set
            {
                _sensorName = value;
                RaisePropertyChanged("SensorName");
            }
        }

        private int _sensorId;

        public int SensorId
        {
            get { return _sensorId; }
            set
            {
                _sensorId = value;
                RaisePropertyChanged("SensorId");
            }
        }

        private int _pairNum;

        public int PairNum
        {
            get { return _pairNum; }
            set
            {
                _pairNum = value;
                RaisePropertyChanged("PairNum");
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
