# -*- coding: utf-8 -*-
import json

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
# Set the Arial font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import pygal
from pygal.style import LightStyle

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
# import cairosvg
import os
import datetime
import random
import string
from PyPDF2 import PdfFileWriter, PdfFileReader


class M3Visualizing:
    @staticmethod
    def create_response(user_id, json_string, filename_svg=None, filename_pdf=None, visualization=True):
        result = Result()
        par = json.loads(json_string)
        # проверка на то, детализировать или нет
        # parameter visualization for not creating pdf and svg files if request was given from inline
        if len(par["axes"]) > 1 and visualization is True:

            # парсим парсим
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
            # парсим
            while i < k:
                header = par["axes"][1]["positions"][i]["members"][0]["caption"]
                if header.isupper() is True:
                    header = header.lower()
                    header = header.capitalize()

                diagramttl.append(header)
                znachenie = par["cells"][i][0]["value"]
                diagramznach.append(znachenie)
                i += 1
            i = 0

            # парсим число
            while i < k - 1:

                if diagramznach[i] is not None:
                    if 'Е' in diagramznach[i]:
                        pars = diagramznach[i].split('E')
                        normznach.append(float(pars[0]))
                        exponen.append(pars[1])

                    else:
                        normznach.append(float(diagramznach[i]))
                        exponen.append(0)

                else:
                    diagramznach[i] = 0
                    normznach.append(diagramznach[i])
                    exponen.append(diagramznach[i])

                i += 1
            i = 0
            print(normznach)
            itogznach = []

            # считаем итоговое значение(на самом деле нет)
            while i < k - 1:
                if exponen[i] != 0:

                    itogznach.append(int(normznach[i] * 10 ** (exponen[i])))
                else:
                    itogznach.append(int(normznach[i]))
                i += 1
            i = 0
            minznach = []
            while i < k - 1:
                if itogznach[i] != 0:
                    minznach.append(len(str(itogznach[i])))
                else:
                    minznach.append(1000)
                i += 1

            i = 0
            # находим количество цифр в числе
            # dopoln_chis - число с минимальным количеством цифр
            dopoln_chis = minznach[0]
            while i < k - 1:
                if minznach[i] < dopoln_chis:
                    dopoln_chis = minznach[i]
                i += 1

            # создание папки и возвращение пути к ней
            path = M3Visualizing.__create_folder(str(user_id))
            # записывание пути в возвращаемый объект
            result.path = path

            # setting the Arial font
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

            # Cоздаем pdf
            doc = canvas.Canvas(path + "\\" + "pattern.pdf")

            # Функция для фирменной полосы сверху
            def __top_line(a):
                a.setFillColorRGB(0.1, 0.47, 0.8)
                a.rect(0 * inch, 11.19 * inch, 8.27 * inch, 0.5 * inch, stroke=0, fill=1)
                a.setFillColorRGB(0, 0.15, 0.28)
                # a.rect(0 * inch, 11.19 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
                a.rect(8.19 * inch, 11.19 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
                a.setFont('Arial', 12)
                a.setFillColorRGB(1, 1, 1)
                a.drawRightString(7.77 * inch, 11.41 * inch, "OpenFinData")

            # Функция для заголовка
            def __title_doc(a):
                a.setFont('Arial', 12)
                a.setFillColorRGB(0, 0, 0)
                a.drawString(0.5 * inch, 10.72 * inch, 'Ваш запрос: ' + title)

            # метод для превращения 10^n в 10 тысяч млн млрд и тд
            # метод неочень, я попозже его переправлю

            # вот это хороший метод
            def __formation(dopoln_chis):
                mas = [' тыс.', ' млн', ' млрд', ' трлн']
                k = dopoln_chis
                s = ''
                if (k > 12) and (k < 16):
                    s = mas[3]
                if (k > 9) and (k < 13):
                    s = mas[2]
                if (k > 6) and (k < 10):
                    s = mas[1]
                if (k > 3) and (k < 7):
                    s = mas[0]
                return s

            dop_chis = __formation(dopoln_chis)

            # метод преобразования чисел, который нормально работает и мне лень его переписывать
            def __vyvod_chisla(chislo):
                chislo_str = str(chislo)
                length1 = len(chislo_str)
                mas = [' тыс.', ' млн', ' млрд', ' трлн']
                k = length1
                smallestpower = 0
                stri = ''
                s = ''
                if (k > 12) and (k < 15):
                    smallestpower = 12
                    s = mas[3]

                if (k > 9) and (k < 13):
                    smallestpower = 9
                    s = mas[2]

                if (k > 6) and (k < 10):
                    smallestpower = 6
                    s = mas[1]

                if (k > 3) and (k < 7):
                    smallestpower = 3
                    s = mas[0]

                if length1 > 3:
                    chislo /= 10 ** smallestpower
                    chi = str(round(chislo, 2))
                    chi = chi.replace(".", ",")
                    stri = chi + s + " рублей"

                else:
                    chi = str(round(chislo, 2))
                    chi = chi.replace(".", ",")
                    stri = chi + s + " рублей"

                return stri

            # Общая цифра
            def __info(a):
                # Высчитываем итоговую сумму
                # переделываем итоговое значение
                i = 0
                while i < k - 1:
                    if dopoln_chis > 3:
                        itogznach[i] = round(itogznach[i] / (10 ** (dopoln_chis - 1)))
                    i += 1

                i = 0
                sum = 0
                while i < k - 1:
                    sum = sum + itogznach[i]
                    i += 1

                sum = sum * (10 ** (dopoln_chis - 1))

                stre = __vyvod_chisla(sum)

                a.setFillColorRGB(0.72, 0.85, 0.98)
                a.rect(0 * inch, 9.85 * inch, 8.27 * inch, 0.5 * inch, stroke=0, fill=1)

                a.setFillColorRGB(0.1, 0.47, 0.8)
                a.rect(0 * inch, 9.85 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)
                # a.rect(8.19 * inch, 9.85 * inch, 0.08 * inch, 0.5 * inch, stroke=0, fill=1)

                a.setFont('Arial', 12)
                a.setFillColorRGB(0, 0, 0)
                a.drawString(0.5 * inch, 10.04 * inch, "Всего: " + stre)

            # Применяем все функции к нашему документу и сохраняем его
            __top_line(doc)
            __title_doc(doc)
            __info(doc)
            doc.showPage()
            doc.save()

            pie_chart = pygal.Pie(inner_radius=.45, plot_background='white', background='white',
                                  legend_at_bottom='True',
                                  legend_at_bottom_columns=1, margin=15, width=732, height=690)
            pie_chart.title = 'Диаграмма'
            i = 0
            while i < k - 1:
                pie_chart.add(diagramttl[i], itogznach[i])
                i += 1

            pie_chart.render_to_file(path + "\\" + filename_svg)

            # Пока тестовый вариант без библиотеки cairosvg (!!!ПОТОМ ИСПРАВИТЬ)
            # cairosvg.svg2pdf(file_obj=open("chart.svg", "rb"), write_to="chart.pdf")

            # Вставляем диаграмму в pdf

            # Пока тестовый вариант без библиотеки cairosvg (!!!ПОТОМ ИСПРАВИТЬ)
            '''
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
            '''
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

            width, height = A4

            '''
            # Высчитываем итоговую сумму
            #переделываем итоговое значение
            i=0
            while i<k-1:
            if dopoln_chis>3:
            itogznach[i]=round(itogznach[i]/(10**(dopoln_chis-1)))
            i=i+1
            '''

            # Общая сумма (для вычисления процентов нужна)
            i = 0
            sum = 0
            while i < k - 1:
                sum = sum + itogznach[i]
                i += 1

            # стили для текста в левой ячейке
            styles = getSampleStyleSheet()
            styleN = styles['BodyText']
            styleN.wordWrap = 'True'
            styleN.fontName = 'Arial'
            styleN.leading = 14

            # пихаем значения красиво в табличку
            i = 0
            qu = []
            tablemas = [["Параметр", "Значение"]]  # Тут сразу и заголовки таблицы
            if sum != 0:
                while i < k - 1:
                    # Тут мы высчитываем проценты, чтобы вставить их в табличку
                    qu = [Paragraph((diagramttl[i]) + "    (" + str(round(itogznach[i] / sum * 100, 2)) + "%)", styleN),
                          str(itogznach[i]) + dop_chis]
                    tablemas.append(qu)
                    i += 1
            else:
                while i < k - 1:
                    qu = [diagramttl[i], itogznach[i]]
                    tablemas.append(qu)
                    i += 1

            data = tablemas  # Данные для таблицы

            # Стили для таблицы
            styles = getSampleStyleSheet()
            table = Table(data, colWidths=[15 * cm, 3.5 * cm])
            table.setStyle(TableStyle([
                # ('INNERGRID', (0,0), (-1,-1), 1.5, colors.white),
                ('LINEBEFORE', (1, 0), (-1, -1), 0.5, colors.white),
                ('LEFTPADDING', (0, 0), (-1, -1), 11),
                ('RIGHTPADDING', (0, 0), (-1, -1), 14),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                # ('LEADING', (0, 0), (-1, -1), 5),
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                # ('LINEABOVE',(0,1),(1,1), 2, colors.white),
                ('BACKGROUND', (0, 0), (1, 0), colors.Color(0.05, 0.27, 0.63)),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 0.005, colors.Color(0, 0.15, 0.28)),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.82, 0.89, 1)]),
            ]))

            # Создаем страницу с таблицей
            c = canvas.Canvas(path + "\\" + "table_" + filename_pdf, pagesize=A4)
            c.setFont('Arial', 14)

            # Функция для позиционирования таблицы
            def __coord(x, y, height, unit=1):
                x, y = x * unit, height - y * unit
                return x, y

            w, h = table.wrap(width, height)
            table.wrapOn(c, width, height)
            table.drawOn(c, *__coord(0.5, 1.4, (height - h), inch))

            """
            # Замечание внизу страницы
            def __notice(a):
                a.setFont('Arial', 10)
                a.setFillColorRGB(0, 0, 0)
                a.drawString(0.5 * inch, 0.5 * inch,
                             "*Значения приведены в " + dop_chis + " рублей")

            __notice(c)
            """
            c.save()

            # фирменный шаблон
            input1 = PdfFileReader(open("my_pattern.pdf", "rb"))
            page1 = input1.getPage(0)

            # страница с таблицей
            input2 = PdfFileReader(open(path + "\\" + "table_" + filename_pdf, "rb"))
            page2 = input2.getPage(0)

            # накладываем страницу с таблицей на шаблон
            page1.mergePage(page2)

            # формируем итоговый файл
            output = PdfFileWriter()
            output.addPage(page1)
            outputStream = open(path + "\\" + filename_pdf, "wb")
            output.write(outputStream)
            outputStream.close()

            # Пока тестовый вариант без библиотеки cairosvg (!!!ПОТОМ ИСПРАВИТЬ)
            '''
            # Добавляем станичку с таблицей
            file1 = PdfFileReader(open('page1.pdf', "rb"))
            file2 = PdfFileReader(open('page2.pdf', "rb"))
            output = PdfFileWriter()
            output.addPage(file1.getPage(0))
            output.addPage(file2.getPage(0))
            # Сохраняем все в итоговый файл
            with open('result.pdf', 'wb') as f:
                output.write(f)
            '''

            # os.rename("chart.svg",filename1)
            # os.rename("page2.pdf",filename2)
            sum = sum * (10 ** (dopoln_chis - 1))

            stre = __vyvod_chisla(sum)

            # Shows for 1st module, that there is no data for such request
            if stre[0] == '0':
                result.data = False

            result.number = stre
            result.is_file = True
        else:

            # использовать метод уже после проверки на то, есть 0 или нет
            # метод по анализу числа на миллионы миллиарды (РАБОЧИЙ ФИНАЛЬНАЯ ВЕРСИЯ)
            def __vyvod_chisla(chislo):
                chislo_str = str(chislo)
                length1 = len(chislo_str)
                mas = [' тыс.', ' млн', ' млрд', ' трлн']
                k = length1
                smallestpower = 0
                stri = ''
                s = ''
                if (k > 12) and (k < 15):
                    smallestpower = 12
                    s = mas[3]

                if (k > 9) and (k < 13):
                    smallestpower = 9
                    s = mas[2]

                if (k > 6) and (k < 10):
                    smallestpower = 6
                    s = mas[1]

                if (k > 3) and (k < 7):
                    smallestpower = 3
                    s = mas[0]

                if length1 > 3:
                    chislo /= 10 ** smallestpower
                    chi = str(round(chislo, 2))
                    chi = chi.replace(".", ",")
                    stri = chi + s + " рублей"
                else:
                    chi = str(round(chislo, 2))
                    chi = chi.replace(".", ",")
                    stri = chi + s + " рублей"
                return stri

            some_number = par["cells"][0][0]["value"]
            if some_number is None:
                some_number = 0

                # Shows for 1st module, that there is no data for such request
                result.data = False

            some_number = round(float(some_number))

            if some_number > 0:
                result.number = __vyvod_chisla(some_number)
            else:
                result.number = __vyvod_chisla(some_number)

        return result

    # метод по созданию папочки
    @staticmethod
    def __create_folder(user_id):
        """Method which creates folder for request"""
        # Defining current hour
        now_time = datetime.datetime.now()
        cur_hour = now_time.hour

        # Forming random string
        random_str = ''.join(random.sample(string.ascii_lowercase, 5))

        # Forming path
        path = 'tmp' + str(cur_hour) + '_' + user_id + random_str

        # Creating folder
        os.mkdir(path)

        return path


class Result:
    def __init__(self, is_file=False, number='', path='', data=True):
        self.is_file = is_file
        self.number = number
        self.path = path
        self.data = data

        # Хочется серфить по морям