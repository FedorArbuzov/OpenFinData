print(3)
kek=M2Retrieving.get_data('расходы,фактический,null,2013,национальная оборона,null')
import json

json_string=kek.response
par=json.loads(json_string)


itog=par["cells"][2][0]["value"]
print(itog)


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

pie_chart.render_to_file('imany.html')
