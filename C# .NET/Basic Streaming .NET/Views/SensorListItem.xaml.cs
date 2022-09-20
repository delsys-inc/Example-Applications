using Basic_Streaming.NET.ViewModels;
using Basic_Streaming.NET.Models;
using DelsysAPI.Components.TrignoRf;
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
    /// Interaction logic for SensorListItem.xaml
    /// </summary>
    public partial class SensorListItem : UserControl
    {

        public SensorModel Model;

        public SensorListItem(SensorTrignoRf sensor)
        {
            InitializeComponent();
            SensorListItemVM vm = new SensorListItemVM();

            Model = new SensorModel
            {
                SensorName = sensor.FriendlyName,
                PairNum = sensor.PairNumber,
                SensorId = sensor.Properties.Sid
            };

            vm.Sensor = Model;
            ListItem.DataContext = vm;

            ModesListVM modeVM = new ModesListVM();

            List<Mode> modeList = new List<Mode>();
            int modeIndex = 0;
            foreach (var mode in sensor.Configuration.SampleModes)
            {
                Mode modeModel = new Mode
                {
                    ModeName = mode,
                    ModeIndex = modeIndex
                };

                modeList.Add(modeModel);
                modeIndex++;
            }

            modeVM.Modes = modeList;

            ModeList.DataContext = modeVM;
        }
    }
}
