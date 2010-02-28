using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    public class Player
    {
        public bool human;
        public string name;
        public string possessiveName;

        public List<Word> words = new List<Word>();

        public Player(bool human, string name, string possessiveName)
        {
            this.human = human;
            this.name = name;
            this.possessiveName = possessiveName;
        }
    }
}
