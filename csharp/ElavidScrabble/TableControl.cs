using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace Elavid.SpeedyScrabble
{
    public partial class TableControl : UserControl
    {
        Pen letterBorderPen = new Pen(Color.Black, 1);
        public Game game;

        public TableControl()
        {
            InitializeComponent();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            if (!Visible || this.Disposing)
            {
                return;
            }

            using (Graphics graphics = CreateGraphics())
            {
                draw(graphics);
            }
        }

        private void draw(Graphics graphics)
        {
            int x;
            int y;

            const int xStart = 10;

            using(Pen pen = new Pen(Color.Black, 5))
            {
                graphics.DrawRectangle(pen, new Rectangle(0, 0, Width, Height));
            }

            if (game == null)
            {
                return;
            }

            x = xStart;
            y = 10;

            foreach (Word word in game.tableWords)
            {
                const int wordHorizontalMargin = 14;
                int drawWidth = wordWidthPx(word);
                if (x > xStart)
                {
                    x += wordHorizontalMargin;

                    if (x + drawWidth > Width)
                    {
                        // This line is full so go on to the next line.
                        x = xStart;
                        y += 25;
                    }
                }

                drawWord(graphics, word, x, y);

                x += drawWidth;
            }

            x = xStart;
            y += 25;
            foreach (Player player in game.players)
            {
                graphics.DrawString(player.name, new Font(FontFamily.GenericSansSerif, 12), Brushes.Black, x, y);

                float wordY = y + 28;

                foreach (Word word in player.words)
                {
                    drawWord(graphics, word, x, wordY);
                    wordY += 27;
                }

                x += 200;
            }
        }

        private int wordWidthPx(Word word)
        {
            return word.letters.Length * 22;
        }

        private void drawWord(Graphics graphics, Word word, float x, float y)
        {
            for (int i = 0; i < word.letters.Length; i++)
            {
                drawLetter(graphics, word.letters[i], x + 22 * i, y);
            }
        }

        private void testAlphabet(Graphics graphics)
        {
            for (int i = 0; i <= 'Z' - 'A'; i++)
            {
                drawLetter(graphics, (char)('A' + i), 30 + i * 22, 30);
            }
        }

        private void drawLetter(Graphics graphics, char letter, float x, float y)
        {
            graphics.FillRectangle(Brushes.LightSalmon, x, y, 20, 22);
            graphics.DrawRectangle(letterBorderPen, x, y, 20, 22);
            graphics.DrawString(letter.ToString(),
                new Font(FontFamily.GenericSansSerif, 12),
                Brushes.Black,
                new RectangleF(x+2, y+1, 16, 20),
                StringFormat.GenericDefault);
        }

        //protected override void OnPaintBackground(PaintEventArgs e)
        //{
            // disable background painting
        //}

        //protected override void OnVisibleChanged(EventArgs e)
        //{
        //    base.OnVisibleChanged(e);
        //}

        public void update()
        {
            Invalidate();
        }

        
        protected override void OnResize(EventArgs e)
        {
            Invalidate();
            base.OnResize(e);
        }

        public void updateAfterFlip(Word letter, List<Word> steals)
        {
            update();
        }

        public void updateAfterFlip(Word letter)
        {
            update();
        }

        public void updateAfterSteal(Word finalSteal)
        {
            update();
        }
    }
}
