using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    public class RandomStrategy : Strategy
    {
        public override List<Word> desiredSteals(Game game, Player player, List<Word> possibleSteals)
        {
            List<Word> desiredSteals = new List<Word>();
            if (possibleSteals.Count == 0) { return desiredSteals; }
            Random random = new Random();
            int randomIndex = random.Next(possibleSteals.Count);
            Word randomSteal = possibleSteals[randomIndex];
            desiredSteals.Add(randomSteal);
            return desiredSteals;
        }
    }
}
