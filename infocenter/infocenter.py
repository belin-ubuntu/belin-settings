#!coding: utf-8
from gi.repository import Gtk
import locale, json, sys
class InfoCenter:
    def __init__(self):
        self.modulok=None
        self.modul_azonositok=None
        self.comboboxtext=None
        self._gui=None
        f=open('/usr/share/infocenter/modullista.cfg', 'r')
        self.modulok=json.load(f)
        f.close()
        self.modul_azonositok=list(self.modulok.keys())
        self.modul_azonositok.sort(key=locale.strxfrm)
        self._gui=self.parbeszedablak_elokeszites()
        self._gui.set_modal(True)
        self.comboboxtext.set_visible(True)
        self.showGUI()

    def parbeszedablak_elokeszites(self):
        dialog=Gtk.Dialog('Információs Központ')
        dialog.set_default_size(500, 400)
        grid = Gtk.Grid()
        dialog.get_content_area().add(grid)
        label=Gtk.Label('Válassza ki azt az információ forrást, melyet használni szeretne.')
        grid.add(label)
        self.comboboxtext=Gtk.ComboBoxText()
        for i in self.modul_azonositok:
            self.comboboxtext.append(i, self.modulok[i]['nev'])
        self.comboboxtext.set_active(0)
        label=Gtk.Label('_Információ típus:')
        label.set_use_underline(True)
        label.set_mnemonic_widget(self.comboboxtext)
        grid.add(label)
        grid.add(self.comboboxtext)
        btn=dialog.add_button('_Megjelenítés', 0)
        btn.connect('clicked', self.present_selected_source)
        btn=dialog.add_button(Gtk.STOCK_CLOSE, 1)
        btn.connect('clicked', self.close_dialog)
        dialog.connect('destroy', self.close_dialog)
        return dialog

    def showGUI(self):
        self._gui.show_all()
        ts = Gtk.get_current_event_time()
        self._gui.present_with_time(ts)

    def present_selected_source(self, widget):
        modul=self.comboboxtext.get_active_id()
        self._gui.destroy()
        __import__(modul)
        if 'categories' in self.modulok[modul]:
            dialog=Gtk.Dialog('Kategória kiválasztása')
            dialog.set_default_size(500, 400)
            grid = Gtk.Grid()
            dialog.get_content_area().add(grid)
            label=Gtk.Label('Az Ön által kiválasztott funkció több információs kategóriát is támogat. Válassza ki az Önt érdeklő kategóriát.')
            grid.add(label)
            categories=Gtk.ComboBoxText()
            for i in self.modulok[modul]['categories']:
                categories.append(i['id'], i['nev'])
            categories.set_active(0)
            label=Gtk.Label('_Kiválasztott kategória:')
            label.set_use_underline(True)
            label.set_mnemonic_widget(categories)
            grid.add(label)
            grid.add(categories)
            btn=dialog.add_button('_Megjelenítés', 0)
            btn=dialog.add_button(Gtk.STOCK_CLOSE, 1)
            btn.connect('clicked', self.close_dialog)
            dialog.connect('destroy', self.close_dialog)
            dialog.set_modal(True)
            dialog.show_all()
            answer=dialog.run()
            print(answer, categories.get_active_id())
            if answer==0:
                sys.modules[modul].main(self.modulok[modul]['categories'][categories.get_active()]['url'], self.modulok[modul]['forras_szoveg'])

        elif 'url' in self.modulok[modul] and 'forras_szoveg' in self.modulok[modul]:
            sys.modules[modul].main(self.modulok[modul]['url'], self.modulok[modul]['forras_szoveg'])
        else:
           sys.modules[modul].main()
        Gtk.main_quit()
    def close_dialog(self, widget):
        self._gui.destroy()
        Gtk.main_quit()

def showUI():
    gui = InfoCenter()
    gui.showGUI()
showUI()
Gtk.main()
