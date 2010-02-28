using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    public abstract class Strategy
    {
        public abstract List<Word> desiredSteals(Game game, Player player, List<Word> possibleSteals);
    }
}
