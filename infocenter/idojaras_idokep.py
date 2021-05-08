#!coding: utf-8
from lxml import html
from gi.repository import Gtk as gtk
import subprocess
cimek={}
cimek['terkep0']='Mai időjárás'
cimek['terkep1']='hosszútávú előrejelzés'
cimek['terkep2']=''
cimek['szolg_36ora']='36 órás előrejelzés'
cimek['szolg_balaton']='Balatoni időjárás'
cimek['szolg_pollen']='Pollenjelentés'
cimek['szolg_kozlekedes']='Közlekedésmeteorológiai információk'
cimek['szolg_orvos']='Orvosmeteorológia'
cimek['szolg_hojelentes']='Hójelentés'
def main():
    try:
        h=html.parse('http://adat.idokep.hu/rss/subscribe/infoalap_forecast_5396e3.xml')
        x=h.xpath('//title|//description')
        html_tartalom='<html>\n<head>\n<meta charset="utf-8">\n<title>'+x[0].text_content()+' '+x[1].text_content()+'</title>\n</head>\n<body>\n<h1>'+x[0].text_content()+' '+x[1].text_content()+'</h1>\n<div>Forrás: <a href="http://www.idokep.hu">Időkép.hu</a>\n</div>\n<div></div>\n'
        for i in range(2, len(x), 2):
            if len(x[i+1].text_content())!=0:
                if x[i].text_content() in cimek:
                    if cimek[x[i].text_content()]!='':
                        html_tartalom=html_tartalom+'<h2>'+cimek[x[i].text_content()]+'</h2>\n<p>'+x[i+1].text_content().replace('\n', '</p>\n<p>')+'</p>\n'
                    else:
                        html_tartalom=html_tartalom+'<p>'+x[i+1].text_content().replace('\n', '</p>\n<p>')+'</p>\n'
                else:
                    html_tartalom=html_tartalom+'<h2>'+x[i].text_content()+'</h2>\n<p>'+x[i+1].text_content().replace('\n', '</p>\n<p>')+'</p>\n'
        html_tartalom=html_tartalom+'</body>\n</html>'
        html.open_in_browser(html.document_fromstring(html_tartalom), encoding='utf-8')
    except:
        dialog = gtk.MessageDialog(None, 0, gtk.MessageType.ERROR,
            gtk.ButtonsType.OK, "A kiválasztott funkcióhoz tartozó adatforrás jelenleg nem érhető el. Próbálja meg később.")
        dialog.run()
        sys.exit()

