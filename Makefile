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
FLAGS_CONVERT   = -background none svg:-
FLAGS_CONVERT_ICO= -define icon:auto-resize=16,32,48,256 $(FLAGS_CONVERT)
PATH_PYTHON     != wslpath "`where.exe python3`"
#/mnt/c/Users/$(USER)/AppData/Local/Microsoft/WindowsApps/python3.exe
FLAGS_PYTHON    = #--console
PATH_UPX	= V:\git\perso\py.git\upx-3.96-win64

PROJECT 	= giftray
DEFAULT_COLOR 	= blue

PATH_BUILD	= ./build/$(PROJECT)
PATH_SVG 	= ./svg
PATH_ICO 	= $(PATH_BUILD)/icons
PATH_PNG 	= $(PATH_BUILD)/png

SPEC		= $(PROJECT).spec
EXEC		= $(BUILDDIR)/$(PROJECT).exe
ICO		= $(PATH_ICO)/$(PROJECT).ico
SVG		= $(wildcard $(PATH_SVG)/*.svg)
SVG_PNG = $(wildcard $(PATH_SVG)/$(PROJECT)-*.svg)
ICOS_BLUE   	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/blue/%.ico, $(SVG))
ICOS_BLACK  	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/black/%.ico,$(SVG))
ICOS_RED    	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/red/%.ico,  $(SVG))
ICOS_GREEN  	= $(patsubst $(PATH_SVG)/%.svg, $(PATH_ICO)/green/%.ico,$(SVG))
PNG             = $(patsubst $(PATH_SVG)/$(PROJECT)-%.svg, $(PATH_PNG)/$(PROJECT)-%-blue.png, $(SVG_PNG)) \
                  $(patsubst $(PATH_SVG)/$(PROJECT)-%.svg, $(PATH_PNG)/$(PROJECT)-%-black.png,$(SVG_PNG)) \
                  $(patsubst $(PATH_SVG)/$(PROJECT)-%.svg, $(PATH_PNG)/$(PROJECT)-%-red.png,  $(SVG_PNG)) \
                  $(patsubst $(PATH_SVG)/$(PROJECT)-%.svg, $(PATH_PNG)/$(PROJECT)-%-green.png,$(SVG_PNG))


all: ico exec

exec: $(EXEC)

ico: $(ICOS_BLUE) $(ICOS_BLACK) $(ICOS_RED) $(ICOS_GREEN)

$(ICO): $(PNG)
	$(PATH_CONVERT) $(FLAGS_CONVERT_ICO) $(PNG) $(ICO)

$(EXEC): $(SPEC) $(ICO) $(SRCS)
	$(PATH_PYTHON) -m PyInstaller $(FLAGS_PYTHON) --noconfirm --upx-dir="$(PATH_UPX)" $(SPEC)

$(PATH_PNG)/$(PROJECT)-%-blue.png: $(PATH_SVG)/$(PROJECT)-%.svg
	mkdir -p $(@D)
	cat $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT) $@

$(PATH_PNG)/$(PROJECT)-%-black.png: $(PATH_SVG)/$(PROJECT)-%.svg
	mkdir -p $(@D)
	sed -e s/1185E0/5a5a5a/g -e s/4DCFE0/aaaaaa/g $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT) $@

$(PATH_PNG)/$(PROJECT)-%-red.png: $(PATH_SVG)/$(PROJECT)-%.svg
	mkdir -p $(@D)
	sed -e s/1185E0/ED664C/g -e s/4DCFE0/FDC75B/g $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT) $@

$(PATH_PNG)/$(PROJECT)-%-green.png: $(PATH_SVG)/$(PROJECT)-%.svg
	mkdir -p $(@D)
	sed -e s/1185E0/32CD32/g -e s/4DCFE0/7CFC00/g $< \
	    | $(PATH_CONVERT) $(FLAGS_CONVERT) $@

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
