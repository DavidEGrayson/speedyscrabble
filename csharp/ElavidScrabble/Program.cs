using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace Elavid.SpeedyScrabble
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            ScrabbleDictionary.init();
            CommonWords.init();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainWindow());
        }
    }
}
