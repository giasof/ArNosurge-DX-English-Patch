using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text;
using System.Windows.Forms;

internal sealed class PatchSetup : Form {
    private readonly string root = AppDomain.CurrentDomain.BaseDirectory;
    private readonly TextBox game = new TextBox();
    private readonly TextBox donor = new TextBox();
    private readonly TextBox log = new TextBox();
    private readonly FlowLayoutPanel actions = new FlowLayoutPanel();
    private Process worker;

    [STAThread] private static void Main() {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new PatchSetup());
    }

    private PatchSetup() {
        Text = "Ar nosurge DX English Patch";
        Font = new Font("Segoe UI", 10);
        StartPosition = FormStartPosition.CenterScreen;
        MinimumSize = new Size(660, 410);
        ClientSize = new Size(740, 460);
        var grid = new TableLayoutPanel { Dock = DockStyle.Fill, Padding = new Padding(12), ColumnCount = 3, RowCount = 4 };
        grid.ColumnStyles.Add(new ColumnStyle(SizeType.AutoSize));
        grid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        grid.ColumnStyles.Add(new ColumnStyle(SizeType.AutoSize));
        for (int row = 0; row < 3; row++) grid.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        grid.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        AddFolder(grid, 0, "Windows DX folder", game);
        AddFolder(grid, 1, "US Vita Plus folder (PCSE00707)", donor);
        actions.AutoSize = true;
        actions.Dock = DockStyle.Fill;
        AddAction("Check files", "check");
        AddAction("Install patch", "install");
        AddAction("Subtitle movies", "movies");
        AddAction("Restore originals", "restore");
        grid.Controls.Add(actions, 0, 2);
        grid.SetColumnSpan(actions, 3);
        log.Multiline = true;
        log.ReadOnly = true;
        log.ScrollBars = ScrollBars.Vertical;
        log.Dock = DockStyle.Fill;
        grid.Controls.Add(log, 0, 3);
        grid.SetColumnSpan(log, 3);
        Controls.Add(grid);
        FormClosing += (s, e) => {
            if (worker != null) {
                e.Cancel = true;
                MessageBox.Show(this, "Wait for the current operation to finish.", Text);
            }
        };
    }

    private void AddFolder(TableLayoutPanel grid, int row, string title, TextBox field) {
        grid.Controls.Add(new Label { Text = title, AutoSize = true, Anchor = AnchorStyles.Left }, 0, row);
        field.Dock = DockStyle.Fill;
        grid.Controls.Add(field, 1, row);
        var browse = new Button { Text = "Browse…", AutoSize = true };
        browse.Click += (s, e) => {
            using (var dialog = new FolderBrowserDialog { Description = title, ShowNewFolderButton = false }) {
                if (Directory.Exists(field.Text)) dialog.SelectedPath = field.Text;
                if (dialog.ShowDialog(this) == DialogResult.OK) field.Text = dialog.SelectedPath;
            }
        };
        grid.Controls.Add(browse, 2, row);
    }

    private void AddAction(string title, string action) {
        var b = new Button { Text = title, AutoSize = true, Margin = new Padding(3, 8, 3, 8) };
        b.Click += (s, e) => Run(action);
        actions.Controls.Add(b);
    }

    // Windows folder names cannot contain quotes. A trailing backslash must
    // be doubled before the closing quote, including for a drive root.
    private static string QuotePath(string path) {
        var full = Path.GetFullPath(path.Trim());
        return "\"" + full + new string('\\', full.Length - full.TrimEnd('\\').Length) + "\"";
    }

    private void Run(string action) {
        if (!Directory.Exists(game.Text) || (action == "install" && !Directory.Exists(donor.Text))) {
            MessageBox.Show(this, action == "install" ? "Select the Windows DX and US Vita Plus folders." : "Select the Windows DX folder.", Text);
            return;
        }
        if (action == "restore" && MessageBox.Show(this, "Restore the original game files from the patch backup?", Text,
                MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return;
        var process = new Process();
        try {
            string args = "-I -B -u -X utf8 install.py " + action + " --game " + QuotePath(game.Text);
            if (action == "install") args += " --vita " + QuotePath(donor.Text);
            process.StartInfo = new ProcessStartInfo {
                FileName = Path.Combine(root, @"runtime\python.exe"), Arguments = args, WorkingDirectory = root,
                UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true,
                StandardOutputEncoding = Encoding.UTF8, StandardErrorEncoding = Encoding.UTF8
            };
            process.SynchronizingObject = this;
            process.EnableRaisingEvents = true;
            int finished = 0;
            Action finish = () => {
                if (++finished != 3) return;
                log.AppendText(process.ExitCode == 0 ? "Done.\r\n" : "The operation could not be completed.\r\n");
                worker = null; actions.Enabled = true; process.Dispose();
            };
            DataReceivedEventHandler receive = (s, e) => {
                if (e.Data == null) finish();
                else log.AppendText(e.Data + Environment.NewLine);
            };
            process.OutputDataReceived += receive;
            process.ErrorDataReceived += receive;
            process.Exited += (s, e) => finish();
            log.Clear();
            log.AppendText("Running " + action + "…\r\n");
            worker = process; actions.Enabled = false;
            process.Start(); process.BeginOutputReadLine(); process.BeginErrorReadLine();
        } catch (Exception e) {
            worker = null; actions.Enabled = true; process.Dispose();
            log.AppendText(e.Message + Environment.NewLine);
        }
    }
}
