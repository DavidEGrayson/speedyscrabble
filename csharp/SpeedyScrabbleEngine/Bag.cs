using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    /// <summary>
    /// Represents a bag of scrabble tiles.
    /// </summary>
    public class Bag
    {
        readonly List<Char> letters = new List<Char>(100);

        public Bag()
        {
            List<Char> sortedLetters = new List<char> {
                'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B',
                'B', 'C', 'C', 'D', 'D', 'D', 'D', 'E', 'E', 'E',
                'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'F',
                'F', 'G', 'G', 'G', 'H', 'H', 'I', 'I', 'I', 'I',
                'I', 'I', 'I', 'I', 'I', 'J', 'K', 'L', 'L', 'L',
                'L', 'M', 'M', 'N', 'N', 'N', 'N', 'N', 'N', 'P',
                'O', 'O', 'O', 'O', 'O', 'O', 'O', 'P', 'P', 'Q',
                'R', 'R', 'R', 'R', 'R', 'R', 'S', 'S', 'S', 'S',
                'T', 'T', 'T', 'T', 'T', 'T', 'U', 'U', 'U', 'U',
                'V', 'V', 'W', 'W', 'X', 'Y', 'Y', 'Z' };

            Random random = new Random();

            while (sortedLetters.Count > 0)
            {
                int index = random.Next(sortedLetters.Count);
                letters.Add(sortedLetters[index]);
                sortedLetters.RemoveAt(index);
            }           
        }

        public int letterCount
        {
            get
            {
                return letters.Count;
            }
        }

        public Boolean empty
        {
            get
            {
                return letterCount == 0;
            }
        }

        public Char draw()
        {
            if (letters.Count == 0)
            {
                throw new Exception("Unable to draw another letter: the bag is empty.");
            }

            Char letter = letters[0];
            letters.RemoveAt(0);
            return letter;
        }

    }
}
