"""Portable teacher-book renderer. Requires reportlab, pymupdf and font paths.

Input format: @@ page heading, ## subheading, ! answer, ordinary paragraphs.
Use --original for the original paper; original pages are copied without OCR.
"""
import argparse,re,json,hashlib
from pathlib import Path
from xml.sax.saxutils import escape
import fitz
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,PageBreak,Table,TableStyle,Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

def main():
 p=argparse.ArgumentParser()
 for flag in ['original','content','output','font','heading-font','symbol-font']:p.add_argument('--'+flag,required=True)
 p.add_argument('--title',default='高中化学完整解析');a=p.parse_args()
 pdfmetrics.registerFont(TTFont('Body',a.font,subfontIndex=0));pdfmetrics.registerFont(TTFont('Head',a.heading_font,subfontIndex=0));pdfmetrics.registerFont(TTFont('Math',a.symbol_font,subfontIndex=0))
 sub=str.maketrans('₀₁₂₃₄₅₆₇₈₉₊₋','0123456789+-');sup=str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻','0123456789+-')
 def fmt(t):
  t=escape(t.replace('−','-').replace('—','-').replace('–','-'))
  t=re.sub('[₀₁₂₃₄₅₆₇₈₉₊₋]+',lambda m:'<sub>'+m[0].translate(sub)+'</sub>',t)
  t=re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+',lambda m:'<super>'+m[0].translate(sup)+'</super>',t)
  return t.replace('⇌','<font name="Math">⇌</font>').replace('ⁿ','<super>n</super>').replace('N_A','N<sub>A</sub>')
 styles={k:ParagraphStyle(k,fontName=f,fontSize=s,leading=l,textColor=c,wordWrap='CJK',spaceAfter=8,spaceBefore=3,keepWithNext=(k=='h')) for k,f,s,l,c in [('t','Head',18,26,colors.HexColor('#183B59')),('h','Head',12,19,colors.HexColor('#183B59')),('a','Head',11,18,colors.HexColor('#B1252A')),('b','Body',11,18,colors.black)]}
 original=fitz.open(a.original);story=[];titles=[]
 for i,sec in enumerate(Path(a.content).read_text(encoding='utf8').split('@@ ')[1:]):
  if i:story.append(PageBreak())
  lines=sec.strip().splitlines();titles.append(lines[0]);story.append(Paragraph(fmt(lines[0]),styles['t']))
  for line in lines[1:]:
   if not line.strip():continue
   if line.startswith('@choices '):
    key=line.split()[1];assert len(key)==14
    rows=[['题号']+list(map(str,range(1,8))),['答案']+list(key[:7]),['题号']+list(map(str,range(8,15))),['答案']+list(key[7:])]
    table=Table(rows,colWidths=[507/8]*8,rowHeights=[21]*4)
    table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Body'),('FONTSIZE',(0,0),(-1,-1),11),('ALIGN',(0,0),(-1,-1),'CENTER'),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#183B59'))]))
    story.extend([table,Spacer(1,10)]);continue
   if line.startswith('@fig '):
    # The fixture refers the learner to the exact original apparatus drawing.
    story.append(Paragraph('装置图请对照前附原卷；进气长管插入洗液，出气短管在液面上。',styles['b']));continue
   key='h' if line.startswith('## ') else 'a' if line.startswith('! ') else 'b'
   story.append(Paragraph(fmt(line[3:] if key=='h' else line[2:] if key=='a' else line),styles[key]))
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);bodyfile=out.with_name(out.stem+'_body.pdf')
 def footer(c,d):
  c.setFont('Body',8);c.drawString(44,28,a.title);c.drawRightString(551,28,f'{len(original)+d.page}')
 SimpleDocTemplate(str(bodyfile),leftMargin=44,rightMargin=44,topMargin=50,bottomMargin=45,title=a.title).build(story,onFirstPage=footer,onLaterPages=footer)
 body=fitz.open(bodyfile);dest=fitz.open();dest.insert_pdf(original);dest.insert_pdf(body)
 norm=lambda t:re.sub(r'\s+','',t.translate(sub).translate(sup).replace('−','-'))
 toc=[[1,'原始试卷',1]]
 for title in titles:
  for page in body:
   if norm(title) in norm(page.get_text()):toc.append([1,title,len(original)+page.number+1]);break
 dest.set_toc(toc);dest.set_metadata({'title':a.title});dest.save(out,deflate=True,garbage=4);dest.close();dest=fitz.open(out)
 same=all(original[i].get_pixmap().samples==dest[i].get_pixmap().samples for i in range(len(original)))
 assert same,'Original pages changed'
 renders=out.with_name(out.stem+'_rendered');renders.mkdir(exist_ok=True)
 for i,page in enumerate(dest):page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(renders/f'{i+1:03}.png')
 print(json.dumps({'pages':len(dest),'original_pages_preserved':same,'rendered':str(renders)},ensure_ascii=False))
if __name__=='__main__':main()
