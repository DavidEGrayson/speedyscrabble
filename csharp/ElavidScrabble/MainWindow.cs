using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Threading;

namespace Elavid.SpeedyScrabble
{
    public partial class MainWindow : Form
    {
        Game game;
        Player you;
        Player computer;

        Strategy strategy = new StandardStrategy();

        Thread thinkThread;

        // TODO: lock possibleSteals or something
        List<Word> possibleSteals;

        public MainWindow()
        {
            InitializeComponent();
        }

        private void MainWindow_Shown(object sender, EventArgs e)
        {
            you = new Player(true, "You", "your");
            computer = new Player(false, "Computer", "computer's");
            game = new Game(new List<Player> { you, computer });
            updateGameStatus();

            startThinkThread();
        }

        void stopThinkThread()
        {
            thinkThread.Abort();
            DateTime startTime = DateTime.Now;
            while (true)
            {
                if (thinkThread.ThreadState == ThreadState.Stopped ||
                    thinkThread.ThreadState == (ThreadState.Unstarted | ThreadState.AbortRequested))
                {
                    return;
                }

                //status("Kill... " + thinkThread.ThreadState);                

                if ((DateTime.Now - startTime).TotalMilliseconds > 500)
                {
                    throw new Exception("Unable to kill thinking thread.  Thinking thread is still in state " + thinkThread.ThreadState + ".");
                }
            }
        }

        void startThinkThread()
        {
            possibleSteals = null;
            thinkThread = new Thread(new ThreadStart(thinkThreadMain));
            thinkThread.Start();
        }

        delegate void StringDelegate(string s);

        private void thinkThreadMain()
        {
            /**
            DateTime startTime = DateTime.Now;
            Invoke(new StringDelegate(status), "Tmphaxing...");
            while(true)
            {
                if ((DateTime.Now - startTime).TotalMilliseconds > 3000)
                {
                    break;
                }
            }**/

            DateTime start = DateTime.Now;
            Invoke(new StringDelegate(status), "Thinking...");
            possibleSteals = game.computePossibleSteals();
            Invoke(new StringDelegate(status), "Done in " + (DateTime.Now - start).TotalMilliseconds + " ms");
        }

        private void status(string s)
        {
            statusLabel.Text = s;
        }

        private void flipButton_Click(object sender, EventArgs e)
        {
            if (possibleSteals == null)
            {
                MessageBox.Show("The computer is not done thinking.  Wait a second and try again.");
                return;
            }

            stopThinkThread();

            // Let the computer make his move.
            List<Word> desiredSteals = strategy.desiredSteals(game, computer, possibleSteals);
            foreach (Word steal in desiredSteals)
            {
                Word newWord = game.steal(steal, computer);
                logSteal(newWord);
            }

            Word letter = game.draw();
            startThinkThread();

            if (game.bag.empty)
            {
                flipButton.Enabled = false;
            }

            log("Flip: " + letter);
            updateGameStatus();
        }

        private void log(string message)
        {
            logBox.Text += DateTime.Now.ToString("hh:mm:ss") + ": " + message + "\r\n";
            logBox.SelectionStart = logBox.Text.Length;
            logBox.ScrollToCaret();
        }

        private void logSteal(Word steal)
        {
            // Get a list of all the multi-letter words that went in to this.
            List<Word> words = new List<Word>();
            foreach(Word ancestor in steal.ancestors)
            {
                if (ancestor.letters.Length > 1)
                {
                    words.Add(ancestor);
                }
            }

            string message = steal.owner.name + " made " + steal.letters;
            if (words.Count == 0)
            {
                message += ".";
            }
            else if (words.Count == 1)
            {
                message += " from " + words[0].owner.possessiveName + " " + words[0].letters + ".";
            }
            else
            {
                List<String> list = new List<String>(words.Count);
                foreach(Word word in words)
                {
                    list.Add(word.owner.possessiveName + " " + word.letters);
                }

                message += " from " + String.Join(" and ", list.ToArray()) + "!";
            }

            log(message);
        }

        private void thinkButton_Click(object sender, EventArgs e)
        {
            //possibleSteals = game.computePossibleSteals();
            //updateGameStatus();
            if (possibleSteals == null)
            {
                MessageBox.Show("Not done thinking.");
                return;
            }

            string message = "";
            foreach (Word word in possibleSteals)
            {
                message += word.letters + ", ";
            }
            MessageBox.Show(message);
        }

        public void updateGameStatus()
        {
            string status = "";
            foreach (Word word in game.tableWords)
            {
                status += word + " ";
            }
            status += "\r\n\r\n";

            foreach (Player player in game.players)
            {
                status += player.name + ":\r\n";
                foreach (Word word in player.words)
                {
                    status += "    " + word + "\r\n";
                }
                status += "\r\n";
            }

            statusBox.Text = status;
        }

        private void wordEntryBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                while (possibleSteals == null)
                {
                    // TODO: add a timeout here in case the thinking thread is taking forever
                    Thread.Sleep(1);
                }

                string wordTyped = wordEntryBox.Text.ToUpper().Replace(" ","");

                List<Word> waysToStealWord = new List<Word>();

                foreach (Word steal in possibleSteals)
                {
                    if (steal.letters == wordTyped)
                    {
                        waysToStealWord.Add(steal);
                    }
                }

                Word finalSteal = null;

                if (waysToStealWord.Count == 0)
                {
                    if (ScrabbleDictionary.isWord(wordTyped))
                    {
                        MessageBox.Show("You can not make " + wordTyped + " currently.");
                    }
                    else
                    {
                        MessageBox.Show("Not a word: " + wordTyped + ".");
                    }
                    return;
                }
                else if (waysToStealWord.Count == 1)
                {
                    finalSteal = waysToStealWord[0];
                }
                else
                {
                    // TODO: implement a cool algorithm that picks which way to steal that word
                    // Prefer stealing from other players, prefer stealing from players with
                    // more words.
                    finalSteal = waysToStealWord[0];
                }

                stopThinkThread();
                Word newWord = game.steal(finalSteal, you);
                logSteal(newWord);
                startThinkThread();
                updateGameStatus();
            }
        }

        private void stuffButton_Click(object sender, EventArgs e)
        {
            for (int i = 0; i < 10; i++)
            {
                DateTime startTime = DateTime.Now;
                game = new Game(new List<Player>());

                while (!game.bag.empty)
                {
                    game.draw();

                    while (true)
                    {
                        List<Word> possibleSteals = game.computePossibleSteals();
                        if (possibleSteals.Count == 0) { break; }
                        Word steal = possibleSteals[0];
                        game.addWord(steal);
                    }
                }
                log("Time trial took " + (DateTime.Now - startTime).TotalMilliseconds + " ms.");
                updateGameStatus();
            }
        }


    }
}
