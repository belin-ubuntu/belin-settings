import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkX11', '3.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Wnck, GdkX11, Gdk
try:
    import orca.speech
except IndexError:
    pass
class windowcontextmenu(Gtk.Menu):
    def switch_window(self, widget, window_list, active_window):
        self.popdown()
        while Gtk.events_pending():
            Gtk.main_iteration()
        if active_window!=widget.get_label()[1:len(widget.get_label())]:
            orca.speech.stop()
        try:
            workspace=window_list.get_workspace()
            workspace.activate(GdkX11.x11_get_server_time(GdkX11.X11Window.lookup_for_display(Gdk.Display.get_default(), GdkX11.x11_get_default_root_xwindow())))
        except AttributeError:
            pass
        window_list.activate(GdkX11.x11_get_server_time(GdkX11.X11Window.lookup_for_display(Gdk.Display.get_default(), GdkX11.x11_get_default_root_xwindow())))
        while Gtk.events_pending():
            Gtk.main_iteration()
        return True

    def displaymenue(self):
        default = Wnck.Screen.get_default()
        default.force_update()
        workspace=default.get_active_workspace()
        active_window=default.get_active_window().get_name()
        if default.get_active_window().has_icon_name():
            menu_item=Gtk.ImageMenuItem('_'+default.get_active_window().get_name().replace('x-caja-desktop', 'Asztal'))
            menu_icon=Gtk.Image.new_from_pixbuf(default.get_active_window().get_icon())
            menu_item.set_image(menu_icon)
            menu_item.set_property("always-show-image", True)
            menu_item.set_use_underline(True)
        else:
            menu_item=Gtk.MenuItem('_'+active_window.replace('x-caja-desktop', 'Asztal'))
            menu_item.set_use_underline(True)
        menu_item.connect("activate", self.switch_window, default.get_active_window(), active_window)
        self.append(menu_item)
        for window_list in default.get_windows():
            window_name=window_list.get_name()
            if window_name!=active_window:
                if window_list.has_icon_name():
                    menu_item=Gtk.ImageMenuItem('_'+window_name.replace('x-caja-desktop', 'Asztal'))
                    menu_icon=Gtk.Image.new_from_pixbuf(window_list.get_icon())
                    menu_item.set_image(menu_icon)
                    menu_item.set_property("always-show-image", True)
                    menu_item.set_use_underline(True)
                else:
                    menu_item=Gtk.MenuItem('_'+window_name.replace('x-caja-desktop', 'Asztal'))
                    menu_item.set_use_underline(True)
                menu_item.connect("activate", self.switch_window, window_list, active_window)
                self.append(menu_item)
        self.show_all()
        self.select_first(True)
        self.popup(None, None, None, None, 0, Gtk.get_current_event_time())

