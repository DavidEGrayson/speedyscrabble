using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Elavid.SpeedyScrabble
{
    public class Game
    {
        public readonly Bag bag = new Bag();
        public List<Word> tableWords = new List<Word>();
        public List<Player> players;

        public Game(List<Player> players)
        {
            this.players = players;
        }

        public Word draw()
        {
            Word word = new Word(bag.draw());
            tableWords.Add(word);
            return word;
        }

        /// <summary>
        /// Puts the word in to the correct list and removes
        /// all of its ancestors from their lists, after checking
        /// that this is a valid move.
        /// </summary>
        public void addWord(Word word)
        {
            if (word.ancestors.Length < 2)
            {
                throw new Exception("To make a new word, you must combine at least two groups of letters (e.g. a word and a letter).");
            }

            if (!substringRuleObeyed(word))
            {
                throw new Exception("A new word must not contain any of the words you made it from.");
            }

            foreach (Word oldWord in word.ancestors)
            {
                if (!wordIsOnTable(oldWord))
                {
                    throw new Exception(oldWord + " is no longer on the table so you can't make a word with it.");
                }
            }

            foreach(Word oldWord in word.ancestors)
            {
                wordList(oldWord).Remove(oldWord);
            }
            wordList(word).Add(word);
        }


        public Word steal(Word finalSteal, Player owner)
        {
            Word newWord = new Word(finalSteal.letters, owner, finalSteal.ancestors);
            addWord(newWord);
            return newWord;
        }

        private List<Word> wordList(Word word)
        {
            if (word.owner == null)
            {
                return this.tableWords;
            }
            else
            {
                return word.owner.words;
            }
        }

        public bool wordIsOnTable(Word word)
        {
            if (word.owner == null)
            {
                return tableWords.IndexOf(word) != -1;
            }
            else
            {
                return players.IndexOf(word.owner) != -1 && word.owner.words.IndexOf(word) != -1;
            }
        }

        public List<Word> computePossibleSteals()
        {
            // Put all the words on the table in to one big list.
            List<Word> words = new List<Word>();
            words.AddRange(this.tableWords);
            foreach (Player player in this.players){ words.AddRange(player.words); }

            List<Word> steals = new List<Word>();

            computePossibleSteals(steals, new List<Word>(), words);

            return steals;
        }

        private void computePossibleSteals(List<Word> steals, List<Word> yesWords, List<Word> maybeWords)
        {
            // We can change yesWords and maybeWords in this function, but we must restore them
            // to their original contents before returning.  (Order does not matter.)

            // Compute yesWordsSum
            string yesWordsSum = "";
            foreach (Word yesWord in yesWords) { yesWordsSum += yesWord.letters; }

            // Base case, the maybeWords list is empty.
            if (maybeWords.Count == 0)
            {
                if (yesWords.Count < 2) { return; }

                List<String> stringWords = ScrabbleDictionary.lookup(StringHelper.sort(yesWordsSum));

                if (stringWords == null) { return; }

                foreach (String stringWord in stringWords)
                {
                    if (substringRuleObeyed(stringWord, yesWords))
                    {
                        Word steal = new Word(stringWord, null, yesWords.ToArray());
                        steals.Add(steal);
                        //Console.WriteLine("New steal: " + stringWord);
                    }
                }

                return;
            }

            // How close are we to reaching the size limit?
            int freeSize = ScrabbleDictionary.maxWordSize - yesWordsSum.Length;
            
            // Recursive case: call this function once or twice, with each call
            // having one fewer maybeWords than this call had.
            Word firstMaybeWord = maybeWords[0];
            maybeWords.Remove(firstMaybeWord);

            computePossibleSteals(steals, yesWords, maybeWords);

            if (firstMaybeWord.letters.Length <= freeSize)
            {
                yesWords.Add(firstMaybeWord);
                computePossibleSteals(steals, yesWords, maybeWords);
                yesWords.Remove(firstMaybeWord);
            }

            maybeWords.Add(firstMaybeWord);
        }

        static bool substringRuleObeyed(Word steal)
        {
            return substringRuleObeyed(steal.letters, steal.ancestors);
        }

        static bool substringRuleObeyed(string steal, ICollection<Word> ancestors)
        {
            foreach (Word ancestor in ancestors)
            {
                if (ancestor.letters.Length > 1 && steal.IndexOf(ancestor.letters) != -1)
                {
                    return false;
                }
            }
            return true;
        }

    }
}
