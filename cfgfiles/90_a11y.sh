#!/bin/sh
export ACCESSIBILITY_ENABLED=1
export DERIVATIVE_NAME=BeLin
export GNOME_ACCESSIBILITY=1
export GTK_MODULES=gail:atk-bridge:libcanberra-gtk-module
export QT_ACCESSIBILITY=1
export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
export GTK_OVERLAY_SCROLLING=0
if [ -d "$HOME/.gconf/apps/metacity" ] ; then
    rm -r $HOME/.gconf/apps/metacity
fi
setxkbmap hu
export DCONF_PROFILE=keybinding
for i in Desktop/*
do
if [[ -f $i ]]; then
chmod +x "$i"
gio set "$i" "metadata::trusted" yes
fi
done
