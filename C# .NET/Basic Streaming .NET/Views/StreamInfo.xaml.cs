using Basic_Streaming.NET.Models;
using Basic_Streaming.NET.ViewModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace Basic_Streaming.NET.Views
{
    /// <summary>
    /// Interaction logic for StreamInfo.xaml
    /// </summary>
    public partial class StreamInfo : UserControl
    {

        public StreamInfoModel Model;

        public StreamInfo()
        {
            InitializeComponent();

            // Build StreamInfo data model

            StreamInfoVM vm = new StreamInfoVM();

            Model = new StreamInfoModel
            {
                DeviceName = "N/A",
                SensorsConnected = 0,
                TotalChannels = 0,
                PipelineStatus = "N/A",
                StreamTime = "0.0 seconds",
                PacketsLost = 0,
                FramesCollected = 0
            };

            vm.StreamInfo = Model;

            StreamInfoGrid.DataContext = vm;
        }
    }
}
