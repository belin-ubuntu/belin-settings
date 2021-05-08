#!/usr/bin/env python3
#!coding: utf-8
import os
import time
import lxml.html
import lxml.etree
import sys
from gi.repository import Gtk as gtk
import json
import locale
import orca.speech
from urllib.request import urlopen
from datetime import date, timedelta
maganhangzok=['a', 'á', 'e', 'é', 'i', 'í', 'o', 'ó', 'u', 'ú', 'ö', 'ő', 'ü', 'ű', 'A', 'Á', 'E', 'É', 'I', 'Í', 'U', 'Ú', 'O', 'Ó', 'Ö', 'Ő', 'Ü', 'Ű', '[', 'm', 'M', 'r', 'R']
specialis_adok=['Megamax', 'Meteo TV', 'Mezzo', 'Minimax', 'Miskolc TV', 'Motors', 'Music channel', 'Musicmix', 'Muzsika TV', 'RAI UNO']
class TvMusor:
    try:
        h=urlopen('http://belin.hu/csatornak.txt')
        csatornak=json.loads(h.read().decode('utf-8'))
    except:
        dialog = gtk.MessageDialog(None, 0, gtk.MessageType.ERROR,
            gtk.ButtonsType.OK, "A TV csatornákat tartalmazó adatbázis jelenleg nem érhető el. Próbálja meg később.")
        dialog.run()
        sys.exit()

    def __init__(self):
        self.csatornavalaszto=None
        self.model = None
        self.treeiter =None
        self._gui=None
        self._gui=self.parbeszedablak_elokeszitese()
        self._gui.set_modal(True)
        self.showGUI()

    def parbeszedablak_elokeszitese(self):
        dialog=gtk.Dialog()
        dialog.set_title('TV csatorna kiválasztása')
        dialog.set_default_size(800, 400)
        vbox=gtk.VBox(False, 1)
        label=gtk.Label('Válasszon egy csatornát a listából, majd aktiválja a megjelenítés gombot.')
        label.set_line_wrap(True)
        vbox.add(label)
        label=gtk.Label('_Csatornák listája:')
        label.set_use_underline(True)
        adolista=list(set(self.csatornak.keys()))
        adolista.sort(key=locale.strxfrm)
        csatornalista=gtk.ListStore(str)
        for i in adolista:
            csatornalista.append([i])
        self.csatornavalaszto=gtk.TreeView(model=csatornalista)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('', renderer, text=0)
        self.csatornavalaszto.append_column(column)
        self.csatornavalaszto.set_headers_visible(False)
        label.set_mnemonic_widget(self.csatornavalaszto)
        vadjust = self.csatornavalaszto.get_vadjustment()
        scrolledwindow = gtk.ScrolledWindow(None, None)
        scrolledwindow.add(self.csatornavalaszto)
        vbox.add(label)
        vbox.add(scrolledwindow)
        dialog.get_content_area().add(vbox)
        self.csatornavalaszto.set_search_column(0)
        selection = self.csatornavalaszto.get_selection()
        selection.select_path(0)
        btn=dialog.add_button('_Megjelenítés', 0)
        btn.grab_default()
        btn.connect('clicked', self.musorinformacio_lekerese)
        btn=dialog.add_button(gtk.STOCK_CANCEL, 1)
        btn.connect('clicked', self.tvmusor_dialog_destroy)
        dialog.connect('destroy', self.tvmusor_dialog_destroy)
        return dialog

    def showGUI(self):
        self._gui.show_all()
        ts = gtk.get_current_event_time()
        self._gui.present_with_time(ts)

    def musorinformacio_lekerese(self, widget):
        self._gui.hide()
        self.model, self.treeiter = self.csatornavalaszto.get_selection().get_selected()
        kivalasztottado=self.model[self.treeiter][0]
        self._gui.destroy()
        ora=time.strftime('%H')
        perc=time.strftime('%M')
        urllista=[]
        datum=[]
        datum.append(date.today())
        datum.append(date.today()+timedelta(days=1))
        datum.append(date.today()+timedelta(days=2))
        for i in datum:
            urllista.append(self.csatornak[kivalasztottado]['url']+'/'+i.strftime("%Y-%m-%d"))
        orca.speech.speak('Kis türelmet, műsorinformációk letöltése folyamatban.')
        par=lxml.html.HTMLParser(encoding='utf-8')
        print(urllista[0])
        u=urlopen(urllista[0])
        html=lxml.html.parse(u, parser=par)
        adocim=kivalasztottado
        if adocim[0] in maganhangzok and adocim not in specialis_adok:
            musor_html='<html><head>\n<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">\n<title>Az '+adocim+' csatorna műsora</title></head><body><h1>Az '+adocim+' csatorna mai műsora</h1>'
        else:
            musor_html='<html>\n<head>\n<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8"><title>A '+adocim+' csatorna műsora</title></head><body><h1>A '+adocim+' csatorna mai műsora</h1>'
        szam=0
        for url in urllista:
            szam=szam+1
            u=urlopen(url)
            html=lxml.html.parse(u, parser=par)
            if szam==2:
                if adocim[0] in maganhangzok and adocim not in specialis_adok :
                    musor_html=musor_html+'<h1>Az '+adocim+' csatorna holnapi műsora</h1>'
                else:
                    musor_html=musor_html+'<h1>A '+adocim+' csatorna holnapi műsora</h1>'
            if szam==3:
                if adocim[0] in maganhangzok and adocim not in specialis_adok :
                    musor_html=musor_html+'<h1>Az '+adocim+' csatorna holnaputáni műsora</h1>'
                else:
                    musor_html=musor_html+'<h1>A '+adocim+' csatorna holnaputáni műsora</h1>'
            adat=html.xpath('//div/div/div[@class="musor_lista_idopont2"]|//div/div/div[@class="musor_lista_cim2"]')
            adatok=html.xpath('//div[@class="musor_lista_idopont"]|//div[@class="musor_lista_cim"]')
            musor={}
            musor['musor']=[]
            musorinformacio={}
            musorinformacio['idopont']=adat[0].text_content().strip()
            musorinformacio['cim']=adat[1].text_content().strip()
            musor['musor'].append(musorinformacio)
            for k in range(0, len(adatok)-1, 2):
                musorinformacio={}
                musorinformacio['idopont']=adatok[k].text_content().strip()
                musorinformacio['cim']=adatok[k+1].text_content().strip()
                musor['musor'].append(musorinformacio)
            for i in musor['musor']:
                if 'link' in i:
                    musor_html=musor_html+str('<h2><a href="'+i['link']+'">'+i['idopont']+': '+i['cim']+'</a></h2>')
                else:
                    musor_html=musor_html+'<h2>'+i['idopont']+': '+i['cim']+'</h2>'
                if 'informacio' in i:
                    musor_html=musor_html+i['informacio']
        musor_html=musor_html.replace('õ', 'ő')
        musor_html=musor_html.replace('Õ', 'Ő')
        musor_html=musor_html.replace('û', 'ű')
        html2=lxml.html.document_fromstring(musor_html)
        orca.speech.speak('Betöltés, kis türelmet.')
        k=lxml.html.open_in_browser(html2, encoding='utf-8')
        gtk.main_quit()

    def tvmusor_dialog_destroy(self, widget):
        self._gui.destroy()
        gtk.main_quit()

def main():
    gui=TvMusor()
    gui.showGUI()
main()
gtk.main()
