from pathlib import Path
import re, json, hashlib, shutil
from xml.sax.saxutils import escape
import fitz
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Flowable, KeepTogether, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Song',str(FONT/'simsun.ttc'),subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hei',str(FONT/'simhei.ttf')))
pdfmetrics.registerFont(TTFont('Latin',str(FONT/'times.ttf')))
pdfmetrics.registerFont(TTFont('MathSymbol',str(FONT/'seguisym.ttf')))
NAVY=colors.HexColor('#183B59'); RED=colors.HexColor('#B1252A')
W,H=595.276,841.89
ST={
'title':ParagraphStyle('title',fontName='Hei',fontSize=18,leading=26,textColor=NAVY,spaceAfter=13),
'head':ParagraphStyle('head',fontName='Hei',fontSize=12,leading=18,textColor=NAVY,spaceBefore=10,spaceAfter=6,keepWithNext=True),
'body':ParagraphStyle('body',fontName='Song',fontSize=11,leading=18.2,spaceAfter=7,wordWrap='CJK'),
'answer':ParagraphStyle('answer',fontName='Hei',fontSize=11,leading=18.2,textColor=RED,backColor=colors.HexColor('#FCF3F1'),borderPadding=6,spaceBefore=4,spaceAfter=10,wordWrap='CJK'),
'meta':ParagraphStyle('meta',fontName='Song',fontSize=9,leading=14,textColor=colors.HexColor('#586671'),spaceAfter=10),
}
SUB=str.maketrans('₀₁₂₃₄₅₆₇₈₉₊₋','0123456789+-')
SUP=str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻','0123456789+-')
def fmt(s):
 s=s.replace('−','-').replace('—','-').replace('–','-')
 s=escape(s)
 s=re.sub('[₀₁₂₃₄₅₆₇₈₉₊₋]+',lambda m:'<sub>'+m.group().translate(SUB)+'</sub>',s)
 s=re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+',lambda m:'<super>'+m.group().translate(SUP)+'</super>',s)
 s=s.replace('N_A','N<sub>A</sub>').replace('V_cell','V<sub>cell</sub>')
 s=s.replace('⇌','<font name="MathSymbol">⇌</font>').replace('ⁿ','<super>n</super>')
 return s
class Apparatus(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=470;self.height=112
 def draw(self):
  c=self.canv;c.setStrokeColor(NAVY);c.setLineWidth(1)
  for x,label in [(12,'A  产生SO2'),(132,'B  洗气'),(252,'C  反应'),(372,'D  尾气吸收')]:
   c.roundRect(x,20,85,64,4);c.setFont('Song',9);c.drawCentredString(x+42.5,4,label)
  for x in [97,217,337]:
   c.line(x,55,x+35,55);c.line(x+35,55,x+30,58);c.line(x+35,55,x+30,52)
  c.setFont('Song',8);c.drawCentredString(54,53,'Cu / 浓硫酸')
  c.drawCentredString(294,53,'MnO2 / 水')
  c.drawCentredString(414,53,'NaOH')
  c.setFillColor(colors.HexColor('#E9F1F5'));c.rect(136,24,77,28,fill=1,stroke=0);c.setFillColor(NAVY)
  c.line(150,90,150,34);c.line(194,90,194,65)
  c.setFont('Song',8);c.drawCentredString(174,35,'饱和NaHSO3')
  c.drawString(136,96,'长进');c.drawString(184,96,'短出')
  c.setFillColor(colors.black)
def furniture(c,d):
 c.saveState();c.setStrokeColor(NAVY);c.setLineWidth(.7);c.line(44,H-43,W-44,H-43)
 c.setFont('Hei',8);c.setFillColor(NAVY);c.drawString(44,H-34,'海淀高三化学期中  |  原卷 · 完整解析 · 知识精讲')
 c.setFont('Song',8);c.setFillColor(colors.HexColor('#6D7780'))
 c.drawString(44,29,'独立解答与科学复核  /  教学解析')
 c.drawRightString(W-44,29,f'解析 {d.page}  ·  全书 {d.page+8}')
 c.restoreState()
def make_body(text,path):
 story=[];titles=[]
 for i,section in enumerate(text.split('@@ ')[1:]):
  if i:story.append(PageBreak())
  lines=section.strip().splitlines();titles.append(lines[0]);story.append(Paragraph(fmt(lines[0]),ST['title']))
  for j,line in enumerate(lines[1:]):
   line=line.strip()
   if not line:continue
   if line=='@fig apparatus':story.extend([Apparatus(),Spacer(1,5)]);continue
   if line.startswith('@choices '):
    key=line.split()[1]
    assert len(key)==14
    rows=[['题号']+list(map(str,range(1,8))),['答案']+list(key[:7]),['题号']+list(map(str,range(8,15))),['答案']+list(key[7:])]
    table=Table(rows,colWidths=[(W-88)/8]*8,rowHeights=[21]*4)
    table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Song'),('FONTSIZE',(0,0),(-1,-1),11),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.5,NAVY),('TEXTCOLOR',(1,1),(-1,1),RED),('TEXTCOLOR',(1,3),(-1,3),RED),('BACKGROUND',(0,0),(0,-1),colors.HexColor('#EDF2F6'))]))
    story.extend([table,Spacer(1,10)]);continue
   if line.startswith('## '):style='head';line=line[3:]
   elif line.startswith('! '):style='answer';line=line[2:]
   elif j==0 and (line.startswith('原卷') or line.startswith('题目')):style='meta'
   else:style='body'
   story.append(Paragraph(fmt(line),ST[style]))
 doc=SimpleDocTemplate(str(path),pagesize=(W,H),rightMargin=44,leftMargin=44,topMargin=59,bottomMargin=48,title='海淀高三化学期中：完整解析与知识精讲',author='HighSchool Chemistry Forge')
 doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
 return titles
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--exam',required=True);args=parser.parse_args()
 txt=(ROOT/'assets/haidian_lessons.txt').read_text(encoding='utf8')
 titles=make_body(txt,OUT/'analysis_body.pdf')
 exam=Path(args.exam)
 orig=fitz.open(exam);body=fitz.open(OUT/'analysis_body.pdf');combined=fitz.open();combined.insert_pdf(orig);combined.insert_pdf(body)
 toc=[[1,'原始试卷（完整8页）',1]]
 section_pages=[]
 for title in titles:
  for p in body:
   # Find actual rendered heading, preserving split lines and chemical subscripts.
   norm=lambda x:re.sub(r'\s+','',x.translate(SUB).translate(SUP).replace('−','-').replace('—','-').replace('–','-'))
   if norm(title) in norm(p.get_text()):
    toc.append([1,title,p.number+9]);section_pages.append((title,p.number+9));break
 combined.set_toc(toc);combined.set_metadata({'title':'海淀高三化学期中：原卷与完整解析','author':'HighSchool Chemistry Forge','subject':'19题独立解答、基础知识、推导、变式与科学复核','keywords':'海淀 高三 化学 解析'})
 final=OUT/'Haidian_Chemistry_Complete.pdf';combined.save(final,garbage=4,deflate=True)
 render=ROOT/'work/rendered';render.mkdir(exist_ok=True)
 for i,p in enumerate(combined):p.get_pixmap(matrix=fitz.Matrix(1.35,1.35)).save(render/f'page_{i+1:02}.png')
 # Visual identity test of retained source, independently of PDF object rewriting.
 combined.close();combined=fitz.open(final)
 source_equal=[]
 for i,p in enumerate(orig):
  a=p.get_pixmap(matrix=fitz.Matrix(1,1));b=combined[i].get_pixmap(matrix=fitz.Matrix(1,1));source_equal.append(a.samples==b.samples)
 stats=[]
 for p in combined:
  blocks=p.get_text('dict')['blocks'];bad=[]
  for block in blocks:
   if block['type']!=0:continue
   for ln in block['lines']:
    for sp in ln['spans']:
     if sp['bbox'][0]<30 or sp['bbox'][2]>W-30 or sp['bbox'][3]>H-20:bad.append(sp['text'])
  stats.append({'page':p.number+1,'text_chars':len(p.get_text()),'out_of_margin':bad})
 meta={'pages':len(combined),'body_pages':len(body),'sections':len(titles),'toc_count':len(toc),'section_pages':section_pages,'original_sha256':hashlib.sha256(exam.read_bytes()).hexdigest(),'source_pages_pixel_equal':source_equal,'page_checks':stats}
 (ROOT/'work/pdf_checks.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in meta.items() if k!='page_checks'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
