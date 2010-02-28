namespace Elavid.SpeedyScrabble
{
    partial class MainWindow
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.thinkButton = new System.Windows.Forms.Button();
            this.statusBox = new System.Windows.Forms.TextBox();
            this.flipButton = new System.Windows.Forms.Button();
            this.logBox = new System.Windows.Forms.TextBox();
            this.wordEntryBox = new System.Windows.Forms.TextBox();
            this.statusLabel = new System.Windows.Forms.Label();
            this.stuffButton = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // thinkButton
            // 
            this.thinkButton.Location = new System.Drawing.Point(12, 14);
            this.thinkButton.Name = "thinkButton";
            this.thinkButton.Size = new System.Drawing.Size(75, 23);
            this.thinkButton.TabIndex = 0;
            this.thinkButton.Text = "Think";
            this.thinkButton.UseVisualStyleBackColor = true;
            this.thinkButton.Click += new System.EventHandler(this.thinkButton_Click);
            // 
            // statusBox
            // 
            this.statusBox.Location = new System.Drawing.Point(218, 14);
            this.statusBox.Multiline = true;
            this.statusBox.Name = "statusBox";
            this.statusBox.ReadOnly = true;
            this.statusBox.Size = new System.Drawing.Size(483, 328);
            this.statusBox.TabIndex = 1;
            // 
            // flipButton
            // 
            this.flipButton.Location = new System.Drawing.Point(12, 51);
            this.flipButton.Name = "flipButton";
            this.flipButton.Size = new System.Drawing.Size(75, 23);
            this.flipButton.TabIndex = 2;
            this.flipButton.Text = "Flip";
            this.flipButton.UseVisualStyleBackColor = true;
            this.flipButton.Click += new System.EventHandler(this.flipButton_Click);
            // 
            // logBox
            // 
            this.logBox.Location = new System.Drawing.Point(12, 80);
            this.logBox.Multiline = true;
            this.logBox.Name = "logBox";
            this.logBox.ReadOnly = true;
            this.logBox.Size = new System.Drawing.Size(200, 262);
            this.logBox.TabIndex = 3;
            // 
            // wordEntryBox
            // 
            this.wordEntryBox.Location = new System.Drawing.Point(218, 351);
            this.wordEntryBox.Name = "wordEntryBox";
            this.wordEntryBox.Size = new System.Drawing.Size(483, 20);
            this.wordEntryBox.TabIndex = 4;
            this.wordEntryBox.KeyDown += new System.Windows.Forms.KeyEventHandler(this.wordEntryBox_KeyDown);
            // 
            // statusLabel
            // 
            this.statusLabel.AutoSize = true;
            this.statusLabel.Location = new System.Drawing.Point(93, 19);
            this.statusLabel.Name = "statusLabel";
            this.statusLabel.Size = new System.Drawing.Size(61, 13);
            this.statusLabel.TabIndex = 5;
            this.statusLabel.Text = "statusLabel";
            // 
            // stuffButton
            // 
            this.stuffButton.Location = new System.Drawing.Point(93, 51);
            this.stuffButton.Name = "stuffButton";
            this.stuffButton.Size = new System.Drawing.Size(75, 23);
            this.stuffButton.TabIndex = 6;
            this.stuffButton.Text = "Time Trial";
            this.stuffButton.UseVisualStyleBackColor = true;
            this.stuffButton.Click += new System.EventHandler(this.stuffButton_Click);
            // 
            // MainWindow
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(713, 383);
            this.Controls.Add(this.stuffButton);
            this.Controls.Add(this.statusLabel);
            this.Controls.Add(this.wordEntryBox);
            this.Controls.Add(this.logBox);
            this.Controls.Add(this.flipButton);
            this.Controls.Add(this.statusBox);
            this.Controls.Add(this.thinkButton);
            this.Name = "MainWindow";
            this.Text = "Speedy Scrabble";
            this.Shown += new System.EventHandler(this.MainWindow_Shown);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button thinkButton;
        private System.Windows.Forms.TextBox statusBox;
        private System.Windows.Forms.Button flipButton;
        private System.Windows.Forms.TextBox logBox;
        private System.Windows.Forms.TextBox wordEntryBox;
        private System.Windows.Forms.Label statusLabel;
        private System.Windows.Forms.Button stuffButton;
    }
}

