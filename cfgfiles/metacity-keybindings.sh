#!/bin/sh
if [ -d "$HOME/.gconf/apps/metacity" ] ; then
    rm -r $HOME/.gconf/apps/metacity
fi
setxkbmap hu
