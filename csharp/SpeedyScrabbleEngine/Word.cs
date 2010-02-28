using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    /// <summary>
    /// Represents a word (if owned by a player) or a letter
    /// (if in the center of the board).
    /// </summary>
    public class Word
    {
        public readonly string letters;

        public readonly Word[] ancestors;

        public readonly Player owner;

        public Word(char letter)
        {
            this.letters = letter.ToString();
        }

        public Word(string letters, Player owner, Word[] ancestors)
        {
            this.letters = letters;
            this.owner = owner;
            this.ancestors = ancestors;
        }

        public override string ToString()
        {
            return letters;
        }
    }
}
