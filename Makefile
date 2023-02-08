#                                                                         \
	This file is part of Giftray (python version).                                         \
	Copyright 2020 cadeauthom <cadeauthom@gmail.com>                      \
	                                                                      \
	Giftray is free software: you can redistribute it and/or modify       \
	it under the terms of the GNU General Public License as published by  \
	the Free Software Foundation, either version 3 of the License, or     \
	(at your option) any later version.                                   \
	                                                                      \
	This program is distributed in the hope that it will be useful,       \
	but WITHOUT ANY WARRANTY; without even the implied warranty of        \
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         \
	GNU General Public License for more details.                          \
	                                                                      \
	You should have received a copy of the GNU General Public License     \
	along with this program.  If not, see <https://www.gnu.org/licenses/>.\

PATH_CONVERT	= /usr/bin/convert
#32
FLAGS_CONVERT_ICO= -define icon:auto-resize=16,32,48,256 -background none svg:-
PATH_PYTHON     != wslpath "`where.exe python3`"
#/mnt/c/Users/$(USER)/AppData/Local/Microsoft/WindowsApps/python3.exe
PATH_MSI        = MSIX-Toolkit.x64/MakeAppx.exe
FLAGS_PYTHON    = #--console
PATH_UPX	= V:\git\perso\py.git\upx-3.96-win64

PROJECT 	= giftray
DEFAULT_COLOR 	= blue

PATH_BUILD	= build
PATH_DIST	= dist
PATH_SVG 	= svg
PATH_ICO 	= $(PATH_BUILD)/icons
PATH_CONF 	= $(PATH_BUILD)/conf
# PATH_PNG 	= $(PATH_BUILD)/png

EXEC		= $(PATH_DIST)/$(PROJECT)_setup.msi
ICO		= $(PATH_ICO)/$(PROJECT).ico
SVG		= $(wildcard $(PATH_SVG)/*.svg)
PY		= $(wildcard src/*.py)
CFG		= src/setup.cfg
CONF    = $(PATH_CONF)/giftray.conf
CONFS   = $(wildcard conf/*.conf) $(wildcard conf/*.conf.example)
SVG_PNG = $(wildcard $(PATH_SVG)/$(PROJECT)-*.svg)
ICOS_BLUE   	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/blue/%.ico, $(SVG))
ICOS_BLACK  	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/black/%.ico,$(SVG))
ICOS_RED    	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/red/%.ico,  $(SVG))
ICOS_GREEN  	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/green/%.ico,$(SVG))
#PNG             = $(patsubst $(PATH_SVG)/$(PROJECT)-0.svg, $(PATH_PNG)/$(PROJECT)-%-blue.png, $(SVG_PNG)) \
#                  $(patsubst $(PATH_SVG)/$(PROJECT)-0.svg, $(PATH_PNG)/$(PROJECT)-%-black.png,$(SVG_PNG)) \
#                  $(patsubst $(PATH_SVG)/$(PROJECT)-0.svg, $(PATH_PNG)/$(PROJECT)-%-red.png,  $(SVG_PNG)) \
#                  $(patsubst $(PATH_SVG)/$(PROJECT)-0.svg, $(PATH_PNG)/$(PROJECT)-%-green.png,$(SVG_PNG))
# PNG44=$(PATH_PNG)/$(PROJECT)-44.png
# PNG150=$(PATH_PNG)/$(PROJECT)-150.png
# PNG=$(PNG44) $(PNG150)
# MANIFEST=AppxManifest.xml

all: ico exec

exec: $(EXEC)

ico: $(ICOS_BLUE) $(ICOS_BLACK) $(ICOS_RED) $(ICOS_GREEN) $(ICO)

#png: $(PNG)

# $(ICO): $(PNG)
#	 $(PATH_CONVERT) -define icon:auto-resize=16,32,48,256 -background none $(PNG) $(ICO)
	
$(ICO):
	cp $(PATH_ICO)/blue/$(PROJECT)-0.ico $@
	
$(CONF): $(CONFS)
	mkdir -p $(@D)
	cp conf/* $(@D)/

$(EXEC): $(ICO) $(SRCS) $(PY) $(CFG) $(CONF)
	mkdir -p $(@D)
	cd src; \
	$(PATH_PYTHON) setup.py \
		build_exe --build-exe ../$(PATH_BUILD)/exe \
		bdist_msi --bdist-dir ../$(PATH_BUILD)/exe --dist-dir ../$(PATH_DIST) -k --target-name $(notdir $@)
#	$(PATH_PYTHON) -m PyInstaller $(FLAGS_PYTHON) --noconfirm --upx-dir="$(PATH_UPX)" $(SPEC)
#	$(PATH_MSI) pack /v /o /h SHA256 /d "$(PATH_DIST)" /p "$@"

#$(PNG44): $(PATH_SVG)/$(PROJECT)-0.svg
#	mkdir -p $(@D)
#	cat $< \
#	    | $(PATH_CONVERT) -resize 44x44 -background none svg:- $(PATH_PNG)/$(PROJECT)-44.png
#$(PNG150): $(PATH_SVG)/$(PROJECT)-0.svg
#	mkdir -p $(@D)
#	cat $< \
#	    | $(PATH_CONVERT) -resize 150x150 -background none svg:- $(PATH_PNG)/$(PROJECT)-150.png
#
#$(PATH_PNG)/$(PROJECT)-%-blue.png: $(PATH_SVG)/$(PROJECT)-%.svg
#	mkdir -p $(@D)
#	cat $< \
#	    | $(PATH_CONVERT)  -background none svg:- $@
#
#$(PATH_PNG)/$(PROJECT)-%-black.png: $(PATH_SVG)/$(PROJECT)-%.svg
#	mkdir -p $(@D)
#	sed -e s/1185E0/5a5a5a/g -e s/4DCFE0/aaaaaa/g $< \
#	    | $(PATH_CONVERT) $(FLAGS_CONVERT) $@
#
#$(PATH_PNG)/$(PROJECT)-%-red.png: $(PATH_SVG)/$(PROJECT)-%.svg
#	mkdir -p $(@D)
#	sed -e s/1185E0/ED664C/g -e s/4DCFE0/FDC75B/g $< \
#	    | $(PATH_CONVERT) $(FLAGS_CONVERT) $@
#
#$(PATH_PNG)/$(PROJECT)-%-green.png: $(PATH_SVG)/$(PROJECT)-%.svg
#	mkdir -p $(@D)
#	sed -e s/1185E0/32CD32/g -e s/4DCFE0/7CFC00/g $< \
#	    | $(PATH_CONVERT) $(FLAGS_CONVERT) $@

$(PATH_ICO)/blue/%.ico: $(PATH_SVG)/%.svg
	mkdir -p $(@D)
	cat $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT_ICO)  $@

$(PATH_ICO)/black/%.ico: $(PATH_SVG)/%.svg
	mkdir -p $(@D)
	sed -e s/1185E0/5a5a5a/g -e s/4DCFE0/aaaaaa/g $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT_ICO) $@

$(PATH_ICO)/red/%.ico: $(PATH_SVG)/%.svg
	mkdir -p $(@D)
	sed -e s/1185E0/ED664C/g -e s/4DCFE0/FDC75B/g $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT_ICO) $@

$(PATH_ICO)/green/%.ico: $(PATH_SVG)/%.svg
	mkdir -p $(@D)
	sed -e s/1185E0/32CD32/g -e s/4DCFE0/7CFC00/g $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT_ICO) $@

mrproper: clean
	rm -rf dist
clean:
	rm -rf build
