# -*- coding: utf-8 -*-
from reportlab.lib.units import inch

kek = M2Retrieving.get_data('расходы,текущий,null,null,общегосударственные вопросы,null')

import json

json_string = kek.response
par = json.loads(json_string)

if len(par["axes"])>1:

    # mew = par["cells"][0][0]["value"]
    # print(mew)
    
    # mi=par["axes"][1]["positions"][1]["ordinal"]
    # print(mi)
    
    # itog=par["cells"][2][0]["value"]
    # print(itog)
    # kek=[]
    # kek=itog.split('E')
    # print(kek[1],' ',kek[0])
    
    k = len(par["axes"][1]["positions"])
    title = par["axes"][1]["positions"][0]["members"][0]["caption"]
    i = 1
    diagramttl = []
    diagramznach = []
    header = 'null'
    znachenie = 0
    normznach = []
    exponen = []
    pars = []
    while i < k:
        header = par["axes"][1]["positions"][i]["members"][0]["caption"]
        diagramttl.append(header)
        znachenie = par["cells"][i][0]["value"]
        diagramznach.append(znachenie)
        i = i + 1
    i = 0
    min = 1000
    while i < k - 1:
        if diagramznach[i] != None:
            pars = diagramznach[i].split('E')
            normznach.append(float(pars[0]))
            pow = int(pars[1])
            exponen.append(int(pars[1]))
            if pow < min:
                min = pow
    
        else:
            diagramznach[i] = 0
            normznach.append(diagramznach[i])
            exponen.append(diagramznach[i])
        i = i + 1
    i = 0
    # print(10**(exponen[1]-min))
    # print(min)
    itogznach = []
    while i < k - 1:
        if exponen[i] != 0:
            itogznach.append(int(normznach[i] * 10 ** (exponen[i] - min)))
        else:
            itogznach.append(0)
        i = i + 1
    
    # print(itogznach)
    # print(exponen)
    # print(normznach)
    # print(k)
    # print(title)
    # print(diagramttl)
    # print(diagramznach)
    
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Frame
    from reportlab.lib.styles import getSampleStyleSheet
    
    # Set the Arial font
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    
    # Cоздаем pdf
    doc = canvas.Canvas("pattern.pdf")
    
    
    # Функция для фирменной полосы сверху
    def top_line(a):
        a.setFillColorRGB(0.1, 0.47, 0.8)
        a.rect(0 * inch, 11.19 * inch, 8.27 * inch, 0.5 * inch, stroke=0, fill=1)
        a.setFillColorRGB(0, 0.15, 0.28)
        # a.rect(0 * inch, 11.19 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
        a.rect(8.19 * inch, 11.19 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
        a.setFont('Arial', 12)
        a.setFillColorRGB(1, 1, 1)
        a.drawRightString(7.77 * inch, 11.41 * inch, "OpenFinData")
    
    
    # Функция для заголовка
    def title_doc(a):
        a.setFont('Arial', 12)
        a.setFillColorRGB(0, 0, 0)
        a.drawString(0.5 * inch, 10.72 * inch, 'Ваш запрос: ' + title)
    
    #метод для превращения 10^n в 10 тысяч млн млрд и тд 
    def frmt(n):
        mas=[' тыс.',' млн.',' млрд.',' трлн.']
        k=0
        s=''
        p=n
    
        while p>0:
        p=p//10
        k=k+1
    
    
        if (k>12) and (k<16):
            n=n/ (10**12)
            s=str(n)+mas[4]
        if (k>9) and (k<13):
            n = n / (10**9)
            s=str(n)+mas[3]
        if (k>6) and (k<10):
            n = n / (10 ** 6)
            s=str(n)+mas[2]
        if (k>3) and (k<7):
            n = n / (10 ** 3)
            s=str(n)+mas[1]
        if  k<4:
            s=str(n)
        return s
    
    
    
    # Общая цифра
    def info(a):
        sum = 0
        i = 0
        while i < k - 1:
            sum = sum + itogznach[i]
            i = i + 1
    
        a.setFillColorRGB(0.72, 0.85, 0.98)
        a.rect(0 * inch, 9.85 * inch, 8.27 * inch, 0.5 * inch, stroke=0, fill=1)
    
        a.setFillColorRGB(0.1, 0.47, 0.8)
        a.rect(0 * inch, 9.85 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
        # a.rect(8.19 * inch, 9.85 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
    
        a.setFont('Arial', 12)
        a.setFillColorRGB(0, 0, 0)
        a.drawString(0.5 * inch, 10.04 * inch, "Всего: " + frmt(sum) + " * (10^1000)" + " рублей")
    
    
    # Применяем все функции к нашему документу и сохраняем его
    top_line(doc)
    title_doc(doc)
    info(doc)
    doc.showPage()
    doc.save()
    
    import pygal
    from pygal.style import LightStyle
    
    pie_chart = pygal.Pie(inner_radius=.45, plot_background='white', background='white', legend_at_bottom='True',
                          legend_at_bottom_columns=1, margin=15, width=732, height=690)
    pie_chart.title = 'Диаграмма'
    i = 0
    while i < k - 1:
        pie_chart.add(diagramttl[i], itogznach[i])
        i = i + 1
    pie_chart.render_to_file('chart.svg')
    import cairosvg
    
    cairosvg.svg2pdf(file_obj=open("chart.svg", "rb"), write_to="chart.pdf")
    
    # Вставляем диаграмму в pdf
    from PyPDF2 import PdfFileWriter, PdfFileReader
    
    output = PdfFileWriter()
    ipdf = PdfFileReader(open('pattern.pdf', 'rb'))
    wpdf = PdfFileReader(open('chart.pdf', 'rb'))
    watermark = wpdf.getPage(0)
    
    for i in range(ipdf.getNumPages()):
        page = ipdf.getPage(i)
        # Здесь корректируем позиционирование
        page.mergeTranslatedPage(watermark, 0.3 * inch, 2 * inch, expand=False)
        output.addPage(page)
    
    # Сохраняем всю красоту в новый pdf
    with open('page1.pdf', 'wb') as f:
        output.write(f)
    
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, cm
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, Table, TableStyle
    from reportlab.platypus import Paragraph, Table, TableStyle, Image
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    # Set the Arial font
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    
    width, height = A4
    
    # Высчитываем итоговую сумму
    sum = 0
    while i < k - 1:
        sum = sum + itogznach[i]
        i = i + 1
    
    i = 0
    qu = []
    tablemas = [["Параметр", "Значение *"]]  # Тут сразу и заголовки таблицы
    if (sum != 0):
        while i < k - 1:
            # Тут мы высчитываем проценты, чтобы вставить их в табличку
            qu = [str(diagramttl[i]) + "  (" + str(round(itogznach[i] / sum * 100, 2)) + "%)", itogznach[i]]
            tablemas.append(qu)
            i = i + 1
    else:
        while i < k - 1:
            qu = [diagramttl[i], itogznach[i]]
            tablemas.append(qu)
            i = i + 1
    
    data = tablemas  # Данные для таблицы
    
    # Стили для таблицы
    styles = getSampleStyleSheet()
    table = Table(data, colWidths=[16 * cm, 2.5 * cm], rowHeights=1.1 * cm)
    table.setStyle(TableStyle([
        # ('INNERGRID', (0,0), (-1,-1), 1.5, colors.white),
        ('LINEBEFORE', (1, 0), (-1, -1), 0.5, colors.white),
        ('LEFTPADDING', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        # ('LINEABOVE',(0,1),(1,1), 2, colors.white),
        ('BACKGROUND', (0, 0), (1, 0), colors.Color(0.05, 0.27, 0.63)),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.005, colors.Color(0, 0.15, 0.28)),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.82, 0.89, 1)]),
    ]))
    
    # Создаем страницу с таблицей
    c = canvas.Canvas("page2.pdf", pagesize=A4)
    c.setFont('Arial', 14)
    
    
    # Функция для позиционирования таблицы
    def coord(x, y, height, unit=1):
        x, y = x * unit, height - y * unit
        return x, y
    
    
    w, h = table.wrap(width, height)
    table.wrapOn(c, width, height)
    table.drawOn(c, *coord(0.5, 0.8, (height - h), inch))
    
    
    # Замечание внизу страницы
    def notice(a):
        a.setFont('Arial', 10)
        a.setFillColorRGB(0, 0, 0)
        a.drawString(0.5 * inch, 0.5 * inch,
                     "* Для получения реальной суммы в рублях необходимо табличное значение умножить на (10^1000)")
    
    
    notice(c)
    c.save()
    
    from PyPDF2 import PdfFileWriter, PdfFileReader
    
    # Добавляем станичку с таблицей
    file1 = PdfFileReader(open('page1.pdf', "rb"))
    file2 = PdfFileReader(open('page2.pdf', "rb"))
    
    output = PdfFileWriter()
    
    output.addPage(file1.getPage(0))
    output.addPage(file2.getPage(0))
    
    # Сохраняем все в итоговый файл
    with open('result.pdf', 'wb') as f:
        output.write(f)
else:
    mew = par["cells"][0][0]["value"]
    print(mew)
