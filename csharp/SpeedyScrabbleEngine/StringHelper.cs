using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    public static class StringHelper
    {
        public static String mergeSort(String sortedString1, String sortedString2)
        {
            //String s = "";

            // TODO: more efficient implementation here
            return sort(sortedString1 + sortedString2);
        }

        public static String sort(String input)
        {
            var chars = new List<Char>(input.ToCharArray());
            chars.Sort();
            string output = "";
            foreach(Char c in chars)
            {
                output += c;
            }
            return output;
        }
    }
}
