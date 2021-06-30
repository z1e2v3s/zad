#!/bin/bash

ddir="zad/Designer"
udir="zad/pyuic"

pyuic5 -o "$udir/mainwindow.py" "$ddir/mainwindow.ui"
pyuic5 -o "$udir/settings.py" "$ddir/settings.ui"

