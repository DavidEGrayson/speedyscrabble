using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    public class StandardStrategy : Strategy
    {
        public override List<Word> desiredSteals(Game game, Player player, List<Word> possibleSteals)
        {
            uint favoriteStealFrequencyClass = uint.MaxValue;
            Word favoriteSteal = null;
            foreach (Word steal in possibleSteals)
            {
                uint frequencyClass = CommonWords.frequencyClass(steal.letters);

                // If it's not a common word, don't pick it.
                if (frequencyClass == uint.MaxValue)
                {
                    continue;
                }

                if (frequencyClass < favoriteStealFrequencyClass)
                {
                    favoriteSteal = steal;
                }
            }
            if (favoriteSteal == null)
            {
                return new List<Word>();
            }

            return new List<Word>{favoriteSteal};
        }
    }
}
