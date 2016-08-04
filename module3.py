print(3)
kek=M2Retrieving.get_data('расходы,фактический,null,2013,национальная оборона,null')
import json
#парсим json
json_string=kek.response
par=json.loads(json_string)




#находим количество объектов во 
k=len(par["axes"][1]["positions"])
title=par["axes"][1]["positions"][0]["members"][0]["caption"]
i=1
diagramttl=[]
diagramznach=[]
header='null'
znachenie=0
normznach=[]
exponen=[]
pars=[]

while i<k:
    header=par["axes"][1]["positions"][i]["members"][0]["caption"]
    diagramttl.append(header)
    znachenie=par["cells"][i][0]["value"]
    diagramznach.append(znachenie)
    i = i + 1
i=0
min=1000
while i<k-1:
    if diagramznach[i]!=None:
        pars=diagramznach[i].split('E')
        normznach.append(float(pars[0]))
        pow=int(pars[1])
        exponen.append(int(pars[1]))
        if pow<min:
            min=pow

    else:
        diagramznach[i]=0
        normznach.append(diagramznach[i])
        exponen.append(diagramznach[i])
    i=i+1

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet

#Set the Arial font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

#Cоздаем pdf
doc = canvas.Canvas("test15.pdf")

#Функция для фирменной полосы сверху
def top_line(a):
    a.setFillColorRGB(0.1, 0.47, 0.8)
    a.rect(0 * inch, 11.19 * inch, 8.27 * inch, 0.5 * inch, stroke=0, fill=1)
    a.setFillColorRGB(0, 0.15, 0.28)
    #a.rect(0 * inch, 11.19 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
    a.rect(8.19 * inch, 11.19 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
    a.setFont('Arial', 12)
    a.setFillColorRGB(0, 0.15, 0.28)
    a.drawRightString(7.77 * inch, 11.41 * inch, "OpenFinData")

#Функция для заголовка
def title(a):
    a.setFont('Arial', 12)
    a.setFillColorRGB(0, 0, 0)
    a.drawString(0.5 * inch, 10.72 * inch, "Текущие расходы на печеньки в Москве".encode("utf-8"))# сюда будем вбивать

#Общая цифра
def info(a):

    a.setFillColorRGB(0.72, 0.85, 0.98)
    a.rect(0 * inch, 9.85 * inch, 8.27 * inch, 0.5 * inch, stroke=0, fill=1)

    a.setFillColorRGB(0.1, 0.47, 0.8)
    a.rect(0 * inch, 9.85 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
    #a.rect(8.19 * inch, 9.85 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)

    a.setFont('Arial', 12)
    a.setFillColorRGB(0, 0, 0)
    a.drawString(0.5 * inch, 10.04 * inch, "Всего: 1 000 000 рублей".encode("utf-8"))

#Применяем все функции к нашему документу и сохраняем его
top_line(doc)
title(doc)
info(doc)
doc.showPage()
doc.save()


i=0
itogznach=[]
while i<k-1:
    if exponen[i]!=0:
        itogznach.append(int(normznach[i]*10**(exponen[i]-min)))
    else:
        itogznach.append(0)
    i=i+1

import pygal
from pygal.style import LightStyle
pie_chart = pygal.Pie(inner_radius=.6, plot_background='white', background='white', legend_at_bottom = 'True', legend_at_bottom_columns=1, margin = 15, width = 550)
pie_chart.title = title
i=0
while i<k-1:
    pie_chart.add(diagramttl[i], itogznach[i])
    i=i+1

pie_chart.render_to_file('im.svg')
cairosvg.svg2pdf(
    file_obj=open("im.svg", "rb"), write_to="chart.pdf")

#Вставляем диаграмму в pdf
from PyPDF2 import PdfFileWriter, PdfFileReader
output = PdfFileWriter()
ipdf = PdfFileReader(open('test15.pdf', 'rb'))
wpdf = PdfFileReader(open('chart.pdf', 'rb'))
watermark = wpdf.getPage(0)

for i in range(ipdf.getNumPages()):
    page = ipdf.getPage(i)
    #Здесь корректируем позиционирование
    page.mergeTranslatedPage(watermark, 1.2*inch, 3.2*inch, expand=False)
    output.addPage(page)

#Сохраняем всю красоту в новый pdf
with open('result.pdf', 'wb') as f:
   output.write(f)
