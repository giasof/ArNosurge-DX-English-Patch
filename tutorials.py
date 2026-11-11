from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont

# Coordinates on the inset shown in the game. Work at native DX resolution.
SCALE=2.5
ORIGIN=(276,153)
WID,HEI=540,304
def box(coords):
    return tuple(round(x*SCALE) for x in coords)
def rect(im,coords,color):
    ImageDraw.Draw(im).rectangle(box(coords),fill=color)
def label(im,pos,text,sz=13,bold=False,color='#f7f7f2',anchor='lm'):
    font=ImageFont.truetype(str(Path(os.environ['WINDIR'])/'Fonts')+'/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),round(sz*SCALE))
    ImageDraw.Draw(im).text(box(pos),text,font=font,fill=color,anchor=anchor,stroke_width=0)
def cropfit(src,coords,dest,region):
    x,y,r,b=box(region)
    clip=src.crop(box(coords))
    clip=clip.resize((r-x,b-y),Image.Resampling.LANCZOS)
    dest.paste(clip,(x,y))
def inset(active):
    x,y=ORIGIN
    return active.crop((x,y,x+1350,y+760))
def frame(im,inner):im.paste(inner,ORIGIN)
def header(im,title):
    rect(im,(0,0,WID,42),'#101d24')
    rect(im,(0,40,WID,41),'#549a9a')
    label(im,(15,20),title,18,True)
def footer(im,lines):
    y=HEI-15-len(lines)*18
    rect(im,(0,y-4,WID,HEI),'#101e26')
    rect(im,(0,y-4,3,HEI),'#69c6c9')
    for i,t in enumerate(lines):label(im,(16,y+10+18*i),t,13)
def card(raw,title):
    im=Image.new('RGB',raw.size,'#14252c');header(im,title);return im

def exclusive(n,im):
    raw=inset(im)
    if n=='tu_battle13':
        p=card(raw,'Encyclopedia   /   Help')
        rect(p,(14,59,138,243),'#203137');rect(p,(145,59,314,243),'#26353a')
        for i,t in enumerate(['Battle','Exploration','Purification','Synthesis','Mental World','Hints & Tips','Item Effects','Equipment Effects']):
            if i==0:rect(p,(17,64,135,83),'#275c5d')
            label(p,(23,74+i*21),t,12,bold=i==0)
        for i,t in enumerate(['Combat Basics','Screen Layout',"Hero’s Parameters","Heroine’s Parameters",'Ally Turn','Enemy Turn','End of Battle','Skills']):
            if i==1:rect(p,(148,85,311,104),'#6d591b')
            label(p,(154,74+i*21),t,12,bold=i==1)
        cropfit(raw,(355,82,500,151),p,(324,80,526,176))
        label(p,(426,212),'Screen Layout',14,True,anchor='mm')
        footer(p,['Open Battle in the Help menu to review the combat tutorials.'])
    elif n=='tu_battle14':
        p=card(raw,'Chains')
        cropfit(raw,(58,50,131,97),p,(22,77,176,176))
        label(p,(201,100),'Chain count',17,True)
        label(p,(201,127),'The number rises with each successive hit.',13)
        label(p,(201,164),'Chain gauge',17,True)
        label(p,(201,191),'The bar below the counter shows time left.',13)
        footer(p,['Hit the next enemy before the gauge empties to keep the chain going.'])
    elif n=='tu_battle15':
        p=card(raw,'Break Bonus')
        cropfit(raw,(78,137,438,177),p,(52,62,488,111))
        cropfit(raw,(45,250,137,281),p,(22,152,188,208))
        label(p,(210,159),'Break gauge',17,True)
        label(p,(210,187),'Fill the gauge to break the enemy.',13)
        footer(p,['A Break Bonus gives you another turn to continue attacking.'])
    elif n.startswith('tu_combination2'):
        p=card(raw,'Ultimate Combination   /   Harmo Burst')
        label(p,(25,90),'1',23,True,'#78d7d3')
        label(p,(56,90),'Fill the Harmonics gauge at Level 4.',17,True)
        cropfit(raw,(289,269,504,300),p,(80,122,460,177))
        label(p,(25,222),'2',23,True,'#78d7d3')
        label(p,(56,222),'Open the battle menu and select Harmo Burst.',16,True)
    elif n.startswith('tu_combination3'):
        p=card(raw,'Ultimate Combination   /   Harmo Burst')
        # Preserve the DX portraits of the two different front-line fighters.
        cropfit(raw,(5,112,536,202),p,(5,86,536,176))
        footer(p,['While Harmo Burst is active, the front-line fighter can attack freely',
                  'until the gauge runs out.'])
    elif n.startswith('tu_combination4'):
        p=card(raw,'Ultimate Combination   /   Finishing move')
        cropfit(raw,(9,18,319,141),p,(20,62,337,188))
        label(p,(353,98),'Skill ready',15,True,'#ffdc7a')
        label(p,(353,126),'Last Stand' if n.endswith('a') else 'Dead End',17,True)
        footer(p,['Use the highlighted skill when it lights up to trigger',
                  'an Ultimate Combination.'])
    elif n=='tu_zerodivide':
        p=card(raw,'Advanced Skills   /   Zero Divide')
        cropfit(raw,(15,88,347,211),p,(18,62,522,249))
        footer(p,['Zero Divide strikes a single target multiple times.'])
    else:raise ValueError(n)
    # The original framed screenshots run a few pixels past the inset.
    ImageDraw.Draw(im).rectangle((275,152,1635,919),fill='#32474a')
    frame(im,p)

def shared(n,im,source):
    # Stamp the authentic English illustration over the same DX backdrop.
    native=source.resize(im.size,Image.Resampling.LANCZOS)
    # Some English annotations extend past the inset on both sides.
    im.paste(native.crop((0,145,1920,934)),(0,145))
    inner=inset(im)
    if n=='tu_comuling2':
        rect(inner,(62,8,249,38),'#17222b');label(inner,(155,22),'Residential Zone · Route 1',12,True,anchor='mm')
    if n in ('tu_net_battle2','tu_net_battle4'):
        # The English console build also uses Japanese for this embedded HUD.
        # Keep the actual encounter and its English turn and damage counters.
        cropfit(inner,(9,17,530,213),inner,(0,0,WID,238))
        rect(inner,(0,239,WID,HEI),'#101e26')
        label(inner,(15,270),'Maternal Overseer',18,True)
    if n in ('tu_friend1','tu_friend2','tu_genomap1','tu_genomap2','tu_misogi4','tu_friend4',
             'tu_misogi2','tu_bios3','tu_genometrics4'):
        rect(inner,(262,282,538,303),'#142228')
        if n in ('tu_friend1','tu_friend2','tu_genomap2','tu_genomap1'):
            label(inner,(423,294),'Select    •    Back    •    Confirm',10,False,anchor='mm')
        else:label(inner,(423,294),'Continue',10,False,anchor='mm')
    if n in ('tu_comuling5','tu_comuling6'):
        rect(inner,(338,231,361,255),'#132632')
        label(inner,(350,242),'›',16,True,anchor='mm')
        if n.endswith('6'):
            rect(inner,(207,151,232,181),'#17272c');rect(inner,(300,151,321,181),'#17272c')
            label(inner,(219,166),'LB',9,True,anchor='mm');label(inner,(311,166),'RB',9,True,anchor='mm')
    frame(im,inner)
