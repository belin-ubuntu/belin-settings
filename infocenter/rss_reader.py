#!coding: utf-8
import orca.speech
from datetime import datetime
from gi.repository import Gtk as gtk
import sys
def read(url, forras):
    import feedparser
    feed = feedparser.parse(url)
    if len(feed['feed'])==0:
        dialog = gtk.MessageDialog(None, 0, gtk.MessageType.ERROR,
            gtk.ButtonsType.OK, "A kiválasztott funkcióhoz tartozó adatforrás jelenleg nem érhető el. Próbálja meg később.")
        dialog.run()
        sys.exit()
    try:
        if feed['feed']['title']!=feed['feed']['subtitle']:
            if feed['feed']['title'].__contains__(' - '):
                cim=feed['feed']['title']
            elif feed['feed']['subtitle'].__contains__(' - '):
                cim=feed['feed']['subtitle']
            else:
                cim=feed['feed']['title']+' - '+feed['feed']['subtitle']
        else:
            cim=feed['feed']['title']
    except KeyError:
        cim=feed['feed']['title']
    html_tartalom='<html>\n<head>\n<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">\n<title>'+cim+'</title>\n</head>\n<body>'
    html_tartalom=html_tartalom+'<h1>'+cim+'</h1>\n'
    orca.speech.speak('Kis türelmet, az információk letöltése folyamatban.')
    link=feed['feed']['links'][0]['href']
    forras_szoveg='<div><p>Forrás: <a href="'+link+'">'+forras+'</a></p></div>\n'
    html_tartalom=html_tartalom+forras_szoveg
    for i in feed['entries']:
        cim=i['title']
        #datum=xml.getElementsByTagName("pubDate")[i].childNodes[0].data
        link=i['links'][0]['href']
        leiras=i['summary']
        szoveg2=cim
        linktext=link
        html_tartalom=html_tartalom+'<h2> <a href="'+linktext+'">'+szoveg2+'</a></h2>\n'
        html_tartalom=html_tartalom+'<p>\n'
        szoveg2=leiras
        html_tartalom=html_tartalom+szoveg2+"</p>\n"
    orca.speech.speak('Betöltés, kis türelmet.')
    html_tartalom=html_tartalom+'</body></html>'
    return html_tartalom

