using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    public static class ScrabbleDictionary
    {
        static Dictionary<String, List<String>> data = new Dictionary<String,List<String>>();

        static int privateMaxWordSize = 0;

        public static int maxWordSize
        {
            get
            {
                return privateMaxWordSize;
            }
        }

        public static void init()
        {
            string[] words = Resource1.twl98.Split('\n');
            foreach (string word in words)
            {
                if (word.Length > privateMaxWordSize)
                {
                    privateMaxWordSize = word.Length;
                }

                string lso = StringHelper.sort(word);
                if (!data.ContainsKey(lso))
                {
                    data[lso] = new List<String>();
                }
                data[lso].Add(word);
            }
        }

        /// <summary>
        /// Performs a basic lookup operation: taking a sorted string and
        /// returning a list of words in the dictionary that can be made out
        /// of those letters.  Returns null if there are none.
        /// </summary>
        public static List<String> lookup(string sortedString)
        {
            string lso = StringHelper.sort(sortedString);
            if (data.ContainsKey(lso))
            {
                // TODO: try removing the AsReadOnly part and see if it
                // decreases performance.
                return data[lso];
            }
            return null;
        }

        public static bool isWord(string maybeWord)
        {
            string lso = StringHelper.sort(maybeWord);
            if (!data.ContainsKey(lso))
            {
                return false;
            }

            foreach (String word in data[lso])
            {
                if (word == maybeWord)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
