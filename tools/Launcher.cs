using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;

internal static class App {
    internal static readonly string Root = AppDomain.CurrentDomain.BaseDirectory;
    internal static readonly string SettingsPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "KoeiTecmo", "ArnosurgeDX", "Setting.ini");
    [STAThread] static void Main() {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        try {
            if (Path.GetFileNameWithoutExtension(Application.ExecutablePath).EndsWith("_Env", StringComparison.OrdinalIgnoreCase))
                Application.Run(new Settings(SettingsPath));
            else Application.Run(new Launcher());
        } catch (Exception e) { MessageBox.Show(e.Message, "Ar nosurge DX", MessageBoxButtons.OK, MessageBoxIcon.Error); }
    }
    internal static Button Button(string caption, EventHandler click) {
        var b = new Button { Text = caption, AutoSize = true, MinimumSize = new Size(95,32), Margin = new Padding(4) };
        b.Click += click; return b;
    }
    internal static void Start(string name) {
        Process.Start(new ProcessStartInfo(name) { WorkingDirectory = Root, UseShellExecute = true });
    }
}
internal class Launcher : Form {
    internal Launcher() {
        Text = "Ar nosurge DX — Launcher"; Font = new Font("Segoe UI",10);
        AutoScaleMode = AutoScaleMode.Dpi; StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedDialog; MaximizeBox = false;
        ClientSize = new Size(485,245);
        var title = new Label { Text = "Ar nosurge DX", Font = new Font("Segoe UI",23), Location = new Point(24,18), AutoSize = true };
        var sub = new Label { Text = "Ode to an Unborn Star", Location = new Point(29,67), AutoSize = true };
        Controls.Add(title); Controls.Add(sub);
        var row = new FlowLayoutPanel { Location = new Point(25,105), Size = new Size(445,55) };
        var play = App.Button("Play", (s,e) => Open(Path.Combine(App.Root,"ArnosurgeDX.exe"),true));
        var settings = App.Button("Settings", (s,e) => { try { using (var f = new Settings(App.SettingsPath)) f.ShowDialog(this); } catch (Exception ex) { Error(ex); } });
        row.Controls.Add(play); row.Controls.Add(settings); Controls.Add(row); AcceptButton=play;
        var links = new FlowLayoutPanel { Location = new Point(26,181), Size = new Size(440,45) };
        foreach (var pair in new[] {new[]{"Manual (Japanese)","https://www.gamecity.ne.jp/manual/arnosurge/jp/"}, new[]{"Game notes (Japanese)",Path.Combine(App.Root,"Readme","Readme_Arno_JP.txt")} }) {
            var link=new LinkLabel { Text=pair[0], AutoSize=true, Margin=new Padding(4,7,16,4) };
            var target=pair[1]; link.LinkClicked+=(s,e)=>Open(target,false); links.Controls.Add(link);
        }
        Controls.Add(links);
    }
    void Open(string name,bool close) { try { App.Start(name); if (close) Close(); } catch(Exception e) {Error(e);} }
    void Error(Exception e) { MessageBox.Show(this,e.Message,"Unable to open",MessageBoxButtons.OK,MessageBoxIcon.Error); }
}
internal class Ini {
    internal readonly List<string> Lines;
    internal Ini(string path) { Lines=File.Exists(path)?File.ReadAllLines(path).ToList():new List<string>(); }
    int Find(string section,string key,out int insert) {
        bool active=false; insert=-1;
        for(int i=0;i<Lines.Count;i++) {
            string text=Lines[i].Trim();
            if(text.StartsWith("[") && text.EndsWith("]")) active=String.Equals(text,"["+section+"]",StringComparison.OrdinalIgnoreCase);
            else if(active) { int eq=text.IndexOf('='); if(eq>=0 && String.Equals(text.Substring(0,eq).Trim(),key,StringComparison.OrdinalIgnoreCase)) return i; }
            if(active) insert=i+1;
        }
        return -1;
    }
    internal string Get(string section,string key,string fallback) { int insert;int i=Find(section,key,out insert);return i<0?fallback:Lines[i].Substring(Lines[i].IndexOf('=')+1).Trim(); }
    internal void Set(string section,string key,string value) {
        int insert;int i=Find(section,key,out insert);string text=key+"="+value;
        if(i>=0) Lines[i]=text;
        else if(insert>=0) Lines.Insert(insert,text);
        else {Lines.Add("["+section+"]");Lines.Add(text);}
    }
    internal void Save(string path) {
        Directory.CreateDirectory(Path.GetDirectoryName(path));
        string temp=path+"."+Guid.NewGuid().ToString("N")+".tmp";
        try { File.WriteAllLines(temp,Lines,new UTF8Encoding(false)); if(File.Exists(path))File.Replace(temp,path,null);else File.Move(temp,path); }
        finally {if(File.Exists(temp))File.Delete(temp);}
    }
}
internal class Settings : Form {
    [StructLayout(LayoutKind.Explicit, Size=156)]
    struct DisplayMode {
        [FieldOffset(36)] public ushort Size;
        [FieldOffset(108)] public int Width;
        [FieldOffset(112)] public int Height;
    }
    [DllImport("user32.dll", EntryPoint="EnumDisplaySettingsA")]
    static extern bool EnumDisplaySettings(string device,int mode,ref DisplayMode settings);
    static Size DesktopSize() {
        var mode=new DisplayMode { Size=156 };
        return EnumDisplaySettings(null,-1,ref mode) ? new Size(mode.Width,mode.Height) : Screen.PrimaryScreen.Bounds.Size;
    }
    readonly string path;
    readonly Ini initial;
    readonly Dictionary<string,Func<string>> readers=new Dictionary<string,Func<string>>();
    readonly Dictionary<string,string> baseline=new Dictionary<string,string>();
    readonly Dictionary<string,Action> defaults=new Dictionary<string,Action>();
    internal Settings(string config) {
        path=config;initial=new Ini(path); Text="Ar nosurge DX Settings"; Font=new Font("Segoe UI",10);
        AutoScaleMode=AutoScaleMode.Dpi;StartPosition=FormStartPosition.CenterScreen;
        ClientSize=new Size(615,565);MinimumSize=new Size(510,420);
        var tabs=new TabControl {Dock=DockStyle.Fill};Controls.Add(tabs);
        var video=Page(tabs,"Display and controls");var keys=Page(tabs,"Key bindings");
        Number(video,"Output width (px)","Graphics","ScreenWidth",1920);
        Number(video,"Output height (px)","Graphics","ScreenHeight",1080);
        List(video,"Display mode","Window","FullScreen","0","0|Windowed","1|Exclusive fullscreen","2|Borderless fullscreen");
        var screenMode=(ComboBox)video.Controls.Find("FullScreen",true).Single();
        var width=(TextBox)video.Controls.Find("ScreenWidth",true).Single();
        var height=(TextBox)video.Controls.Find("ScreenHeight",true).Single();
        int initialScale;
        if(!int.TryParse(initial.Get("Graphics","RenderScale","100"),out initialScale) || initialScale<100 || initialScale>200)initialScale=100;
        var scale=new NumericUpDown { Minimum=100,Maximum=200,Increment=1,Value=initialScale };
        Add(video,"Render scale (%)",scale);
        Track("Graphics","RenderScale",()=>((int)scale.Value).ToString(),()=>scale.Value=100,scale);
        var preview=new Label { Name="RenderPreview",AutoSize=true,TextAlign=ContentAlignment.MiddleLeft };
        Add(video,"Render resolution",preview);
        var desktop=DesktopSize();
        Func<Size> outputSize=()=>{
            if(screenMode.SelectedIndex==2)return desktop;
            int x,y;
            return int.TryParse(width.Text,out x)&&int.TryParse(height.Text,out y)&&x>0&&y>0&&x<=65535&&y<=65535 ? new Size(x,y) : Size.Empty;
        };
        Func<Size> renderSize=()=>{
            Size size=outputSize();
            return new Size((size.Width*(int)scale.Value+50)/100,(size.Height*(int)scale.Value+50)/100);
        };
        EventHandler updateDisplay=(s,e)=>{
            bool automatic=screenMode.SelectedIndex==2;
            width.Enabled=height.Enabled=!automatic;
            var size=renderSize();
            preview.Text=size.IsEmpty ? "—" : size.Width+" × "+size.Height+(automatic ? "\nPrimary display · "+desktop.Width+" × "+desktop.Height : "");
        };
        screenMode.SelectedIndexChanged+=updateDisplay;width.TextChanged+=updateDisplay;height.TextChanged+=updateDisplay;scale.ValueChanged+=updateDisplay;
        updateDisplay(this,EventArgs.Empty);
        checkScale=()=>{
            var size=renderSize();
            if(scale.Value>100 && (size.Width>16384 || size.Height>16384))throw new FormatException("The render size exceeds 16,384 pixels. Lower the render scale or output resolution.");
        };
        List(video,"Character outlines","Graphics","Outline","1","0|Off","1|On");
        List(video,"Shadows","Graphics","Shadow","2","0|Low","1|Medium","2|High","3|Off");
        List(video,"Mouse controls","Mouse","MOUSE_ENABLE","1","0|Off","1|On");
        List(video,"Xbox menu buttons","Pad","AB_SET","1","1|A confirms, B goes back","0|B confirms, A goes back");
        var menuButtons = (ComboBox)video.Controls.Find("AB_SET",true).Single();
        defaults["Pad/AB_SET"] = () => menuButtons.SelectedIndex = 0;
        var choices=new List<string>{"|Unassigned","ENTER|Enter","UP_ARROW|Up arrow","DOWN_ARROW|Down arrow","LEFT_ARROW|Left arrow","RIGHT_ARROW|Right arrow"};
        for(char c='A';c<='Z';c++)choices.Add(c.ToString());
        for(int i=1;i<=11;i++) choices.Add("F"+i);
        for(int i=1;i<=9;i++) choices.Add("KEY_"+i+"|"+i);
        for(int i=0;i<=9;i++) choices.Add("KPAD_"+i+"|Numpad "+i);
        var bindings=new[]{"UP|Menu up|UP_ARROW","DOWN|Menu down|DOWN_ARROW","LEFT|Menu left|LEFT_ARROW","RIGHT|Menu right|RIGHT_ARROW","CIRCLE|A · Confirm|L","CROSS|B · Cancel|K","SQUARE|X|J","TRIANGLE|Y|I","L1|LB|Q","L2|LT|U","L3|Left stick button|F","R1|RB|E","R2|RT|O","R3|Right stick button|H","START|Start|ENTER","SELECT|Select|N","MOVE_UP|Move up|W","MOVE_DOWN|Move down|S","MOVE_LEFT|Move left|A","MOVE_RIGHT|Move right|D","CAMERA_UP|Camera up|T","CAMERA_DOWN|Camera down|G","CAMERA_LEFT|Camera left|R","CAMERA_RIGHT|Camera right|Y"};
        foreach(var spec in bindings){var v=spec.Split('|');List(keys,v[1],"Input",v[0],v[2],choices.ToArray());}
        var pad=new[]{"A","B","X","Y","L|LB","R|RB","LT","RT","L Stick Button|Left stick button","R Stick Button|Right stick button","View|View","Menu","UP|Up","DOWN|Down","LEFT|Left","RIGHT|Right"};
        List(keys,"Left click emulates","Input","MOUSE_LEFT","A",pad);
        List(keys,"Right click emulates","Input","MOUSE_RIGHT","B",pad);
        List(keys,"Middle click emulates","Input","MOUSE_CENTER","X",pad);
        var buttons=new FlowLayoutPanel {Dock=DockStyle.Bottom,Height=54,FlowDirection=FlowDirection.RightToLeft,Padding=new Padding(4)};
        var ok=App.Button("OK",(s,e)=>{if(Commit())Close();});
        var cancel=App.Button("Cancel",(s,e)=>Close());
        buttons.Controls.Add(ok);buttons.Controls.Add(cancel);buttons.Controls.Add(App.Button("Apply",(s,e)=>Commit()));
        buttons.Controls.Add(App.Button("Defaults",(s,e)=>{foreach(var reset in defaults.Values)reset();}));
        Controls.Add(buttons);AcceptButton=ok;CancelButton=cancel;
    }
    static TableLayoutPanel Page(TabControl tabs,string name) {
        var page=new TabPage(name){AutoScroll=true,Padding=new Padding(12)};tabs.TabPages.Add(page);
        var table=new TableLayoutPanel{Dock=DockStyle.Top,AutoSize=true,ColumnCount=2};
        table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,52));table.ColumnStyles.Add(new ColumnStyle(SizeType.Percent,48));
        page.Controls.Add(table);return table;
    }
    static void Add(TableLayoutPanel t,string label,Control field) {
        int row=t.RowCount++;t.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        t.Controls.Add(new Label{Text=label,AutoSize=true,Anchor=AnchorStyles.Left,Margin=new Padding(3,8,3,8)},0,row);
        field.Dock=DockStyle.Fill;field.Margin=new Padding(3,5,12,5);t.Controls.Add(field,1,row);
    }
    void Track(string section,string key,Func<string> read,Action reset,Control control) {
        string id=section+"/"+key; control.Name=key; readers[id]=read; baseline[id]=read(); defaults[id]=reset;
    }
    void Number(TableLayoutPanel t,string label,string section,string key,int def) {
        var tb=new TextBox{Text=initial.Get(section,key,def.ToString())};Add(t,label,tb);
        Track(section,key,()=>{int v;if(!Int32.TryParse(tb.Text,out v)||v<1||v>65535)throw new FormatException(label+" must be between 1 and 65,535.");return v.ToString();},()=>tb.Text=def.ToString(),tb);
    }
    void List(TableLayoutPanel t,string label,string section,string key,string def,params string[] options) {
        var cb=new ComboBox{DropDownStyle=ComboBoxStyle.DropDownList};var values=new List<string>();
        foreach(var opt in options){var pair=opt.Split('|');values.Add(pair[0]);cb.Items.Add(pair[pair.Length-1]);}
        var current=initial.Get(section,key,def);if(!values.Contains(current)){values.Add(current);cb.Items.Add(current);}
        cb.SelectedIndex=values.IndexOf(current);Add(t,label,cb);
        Track(section,key,()=>values[cb.SelectedIndex],()=>cb.SelectedIndex=values.IndexOf(def),cb);
    }
    readonly Action checkScale;
    internal bool Commit() {
        try {checkScale();var latest=new Ini(path); var next=readers.ToDictionary(p=>p.Key,p=>p.Value()); bool missing=!File.Exists(path),changed=false;
            foreach(var p in next){if(!missing && baseline[p.Key]==p.Value)continue;var sk=p.Key.Split('/');latest.Set(sk[0],sk[1],p.Value);changed=true;}
            if(changed)latest.Save(path);foreach(var p in next)baseline[p.Key]=p.Value;return true;
        } catch(Exception ex){MessageBox.Show(this,ex.Message,"Settings could not be saved",MessageBoxButtons.OK,MessageBoxIcon.Error);return false;}
    }
}
