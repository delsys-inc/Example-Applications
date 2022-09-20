using System.Windows;
using System.Windows.Controls;

namespace Basic_Streaming.NET.Views
{
    /// <summary>
    /// Interaction logic for LoadingIcon.xaml
    /// </summary>
    public partial class LoadingIcon : UserControl
    {

        public LoadingIcon(string msg, int[]? IconMargin = null, int[]? msgMargin = null)
        {
            InitializeComponent();
            LoadMsg.Text = msg;
            pairSensorsTextAndIconMarginSettings(msgMargin: msgMargin, IconMargin: IconMargin);
        }

        /// <summary>
        /// Displays message without icon, used when no components are found in scan/pair request 
        /// </summary>
        /// <param name="msg"></param>
        public void JustShowMessage(string msg, int[]? msgMargin = null)
        {
            this.Dispatcher.Invoke(() =>
            {
                Icon.Visibility = Visibility.Collapsed;
                LoadMsg.Text = msg;
            });
            pairSensorsTextAndIconMarginSettings(msgONLYMargin: msgMargin);
        }

        private void pairSensorsTextAndIconMarginSettings(int[]? msgMargin = null, int[]? IconMargin = null, int[]? msgONLYMargin = null)
        {
            if (IconMargin != null)
            {
                Icon.Margin = new Thickness(IconMargin[0], IconMargin[1], IconMargin[2], IconMargin[3]);
            }

            if (msgMargin != null)
            {
                Grid.SetRow(LoadMsg, 0);
                LoadMsg.VerticalAlignment = VerticalAlignment.Top;
                LoadMsg.Margin = new Thickness(msgMargin[0], msgMargin[1], msgMargin[2], msgMargin[3]);
            }
            else if (msgONLYMargin == null && msgMargin == null)
            {
                Grid.SetRow(LoadMsg, 1);
            }

            if (msgONLYMargin != null)
            {
                LoadMsg.Margin = new Thickness(msgONLYMargin[0], msgONLYMargin[1], msgONLYMargin[2], msgONLYMargin[3]);
            }
        }
    }
}
