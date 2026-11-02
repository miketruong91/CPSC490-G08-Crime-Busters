"""Export the same nodes/edges as the Mermaid figures to static PNGs.

Run from any directory with Pillow installed: python docs/design/render_diagrams.py
Positions are presentation-only; Mermaid in the design docs is editable source.
If changing the graph, update both this data and the corresponding Mermaid block.
"""
from pathlib import Path
from math import atan2, cos, sin
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
# Fall back to Pillow's bundled font on other operating systems.
def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default(size=size)


def render(name, title, nodes, edges, boundary):
    im = Image.new('RGB', (1500, 1100), 'white')
    d = ImageDraw.Draw(im)
    d.text((50, 25), title, font=font(30), fill='#172c44')
    box, label = boundary
    d.rounded_rectangle(box, radius=18, fill='#f3f7fc', outline='#8aa1bb', width=3)
    d.text((box[0]+20, box[1]+15), label, font=font(24), fill='#172c44')
    for key, (x, y, w, h, text) in nodes.items():
        d.rounded_rectangle((x, y, x+w, y+h), radius=12, fill='white', outline='#315b80', width=3)
        d.multiline_text((x+w/2, y+h/2), text, font=font(23), fill='#172c44', anchor='mm', align='center', spacing=7)
    for start, end, label, label_pos in edges:
        d.line((start,end), fill='#315b80', width=3)
        angle = atan2(end[1]-start[1],end[0]-start[0])
        pts = [end, (end[0]-16*cos(angle-.45),end[1]-16*sin(angle-.45)), (end[0]-16*cos(angle+.45),end[1]-16*sin(angle+.45))]
        d.polygon(pts, fill='#315b80')
        x,y=label_pos
        bbox=d.multiline_textbbox((x,y),label,font=font(20),align='center')
        d.rectangle((bbox[0]-5,bbox[1]-3,bbox[2]+5,bbox[3]+3),fill='white')
        d.multiline_text((x,y),label,font=font(20),fill='#172c44',align='center',spacing=4)
    d.text((50,1050),'PROPOSED — exchanges and integration are not implemented. Conditional basemap provider remains undecided.',font=font(22),fill='#5a4756')
    (ROOT/'diagrams').mkdir(exist_ok=True)
    im.save(ROOT/'diagrams'/f'{name}.png')


render('architecture','Figure 1 — Proposed high-level architecture',{
 'source':(50,130,320,100,'Public data provider\nAdoption/terms pending'),
 'import':(520,130,380,100,'Python import / validation\nNormalization — planned'),
 'db':(520,380,380,100,'SQLite database file\nSchema / loading — planned'),
 'flask':(520,650,380,130,'Python Flask application\nQuery, filter, summarize\nIntegration — planned'),
 'browser':(60,650,320,130,'Browser interface\nHTML / CSS / JavaScript\nLeaflet.js — planned'),
 'tiles':(1060,650,360,130,'Possible basemap provider\nNot selected\nConditional dependency'),
},[
 ((370,180),(520,180),'Source records',(385,120)),
 ((710,230),(710,380),'Validated standardized records',(740,285)),
 ((665,650),(665,480),'Queries',(555,540)),
 ((780,480),(780,650),'Records',(805,540)),
 ((380,685),(520,685),'HTTP requests',(380,625)),
 ((520,750),(380,750),'Pages / JSON',(380,790)),
 ((220,780),(220,920),'Conditional tile requests',(240,865)),
 ((220,920),(1240,920),'',(720,930)),
 ((1240,920),(1240,780),'',(1250,840)),
 ((1060,690),(980,570),'Conditional tiles',(1060,550)),
 ((980,570),(220,570),'',(950,590)),
 ((220,570),(220,650),'',(250,590)),
],((30,290,980,1015),'Localhost application (browser + Flask + local storage)'))
render('system-context','Figure 2 — Proposed system context',{
 'user':(50,170,330,120,'Application user\nExplore local records'),
 'provider':(1070,170,360,120,'Public data provider\nFinal adoption pending'),
 'maintainer':(1070,650,360,120,'Team data maintainer\nPrepare approved dataset'),
 'system':(510,410,440,180,'Crime Busters\nBrowser + Flask + SQLite\nLocalhost application\nProposed system'),
 'tiles':(50,650,330,120,'Possible basemap provider\nNot selected'),
},[
 ((300,290),(510,440),'Location / filters / radius',(265,330)),
 ((510,550),(190,550),'Map / records / summaries',(160,575)),
 ((190,550),(190,290),'',(90,420)),
 ((1250,290),(1250,650),'Source records',(1270,455)),
 ((1070,710),(950,530),'Approved standardized\nrecords',(900,770)),
 ((610,590),(380,690),'Conditional tile requests',(400,660)),
 ((380,740),(510,580),'Conditional tiles',(295,790)),
],((460,350,1000,630),'System boundary'))
