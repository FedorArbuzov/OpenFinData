print(3)
kek=M2Retrieving.get_data('расходы,фактический,null,2013,национальная оборона,null')
import json
#парсим json
json_string=kek.response
par=json.loads(json_string)




#находим количество объектов в axes[1]["positions']
k=len(par["axes"][1]["positions"])
title=par["axes"][1]["positions"][0]["members"][0]["caption"]
i=1 #счетчик
diagramttl=[] #лист для надписей
diagramznach=[]#лист для значений(не парсила пока)
header='null'#заголовок
znachenie=0#переменная, где хранится строка, которую позже буду делить сплитом
normznach=[]#лист значений флоат
exponen=[]#лист хранения степеней десятки 
pars=[]#лист для хранения кусочков распарсенной строки

#собираем надписи, которые позже пойдут в легенду диаграммы, и числа
while i<k:
    header=par["axes"][1]["positions"][i]["members"][0]["caption"]
    diagramttl.append(header)
    znachenie=par["cells"][i][0]["value"]
    diagramznach.append(znachenie)
    i = i + 1
i=0
min=1000 #поиск минимума
#тут мы красиво парсим второе число на флоат и степень десятки 
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
#дальше начинается Светин кусок магии с пдф
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
itogznach=[]#больше массивов богу массивов! Этот - для итоговых числовых значений
while i<k-1:
    if exponen[i]!=0:
        itogznach.append(int(normznach[i]*10**(exponen[i]-min)))
    else:
        itogznach.append(0)
    i=i+1
#строим диаграмму
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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
#Set the Arial font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))


width, height = A4



def coord(x, y, height, unit=1):
    x, y = x * unit, height -  y * unit
    return x, y



i=0
qu=[]
tablemas=[]
while i<k-1:
    qu=[diagramttl[i], itogznach[i]]
    tablemas.append(qu)
    i = i + 1
data=tablemas



styles = getSampleStyleSheet()

table = Table(data, colWidths=[8 * cm, 8 * cm], rowHeights=1*cm)
table.setStyle(TableStyle([
                       ('INNERGRID', (0,0), (-1,-1), 1, colors.grey),
                       ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                       ('LINEABOVE',(0,1),(1,1), 1.5, colors.grey),
                       #('BACKGROUND',(0,0),(1,0), colors.Color(0.31, 0.1, 0.45)),
                       #('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
                       ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                       ('BOX', (0,0), (-1,-1), 0.01, colors.grey),
                       ]))


c = canvas.Canvas("abcdefg.pdf", pagesize=A4)
c.setFont('Arial', 14)

w, h = table.wrap(width, height)
table.wrapOn(c, width, height)
table.drawOn(c, *coord(2.5, 1, height - h, cm))

c.save()
