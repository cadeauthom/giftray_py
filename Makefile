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

############### Project setting
PROJECT 	= GifTray
#can be 0, 1 or 2
ICONB		= 0
#can be blue, black, red or green
COLOR 		= blue

############### Commands setting
PATH_CONVERT	= /usr/bin/convert
#32
FLAGS_CONVERT_ICO= -define icon:auto-resize=16,32,48,256 -background none svg:-
PATH_PYTHON     != wslpath "`where.exe python3`"
#/mnt/c/Users/$(USER)/AppData/Local/Microsoft/WindowsApps/python3.exe
#FLAGS_PYTHON    = --console
FLAGS_PYTHON    = 

############### Path setting
BUILD	        = build
DIST	        = dist
SRC		= src
SRC_SVG		= svg
SRC_CONF	= conf
BUILD_SVG	= $(BUILD)/svg
BUILD_CONF	= $(BUILD)/conf
BUILD_EXE	= $(BUILD)/exe
BUILD_SRC	= $(BUILD)/src

#VERSION_MAIN	= $(shell git describe --tags)
VERSION_TAG_COM = $(shell git rev-list --tags --max-count=1)
VERSION_MAIN	= $(shell git describe --tags $(VERSION_TAG_COM))
VERSION_COMMITS	= $(shell git rev-list $(VERSION_MAIN)..HEAD --count)
VERSION_STAGES	= $(shell git status -s | egrep -c "^\w")
VERSION_DIFFS	= $(shell git status -s | egrep -c "^.\w")
VERSION_DATE	= $(shell date +%s)
$(eval VERSION=$(VERSION_MAIN).$(VERSION_COMMITS).$(VERSION_STAGES).$(VERSION_DIFFS).$(VERSION_DATE))

############### Variable Definition
LOWPROJECT 	= $(shell echo $(PROJECT) | tr '[:upper:]' '[:lower:]')

SVGS		= $(wildcard $(SRC_SVG)/*/*.svg)
SVG			= $(SRC_SVG)/$(LOWPROJECT)-$(ICONB).svg
CONF		= $(wildcard $(SRC_CONF)/*.example) $(SRC_CONF)/list_key.txt

HTML_PY		= $(SRC)/svg2html.py
PY		= $(SRC)/$(PROJECT).py
PY_LIBS		= $(wildcard $(SRC)/$(LOWPROJECT)/*.py)
SETUP		= $(SRC)/setup.py
#CFG		= $(SRC)/setup.cfg

IN_PY		= $(SETUP) $(PY) $(PY_LIBS)
OUT_HTML_PY	= $(patsubst $(SRC)/%, $(BUILD_SRC)/%, $(HTML_PY))
OUT_PY		= $(patsubst $(SRC)/%, $(BUILD_SRC)/%, $(IN_PY))
OUT_SVGS	= $(patsubst $(SRC_SVG)/%, $(BUILD_SVG)/%, $(SVGS))
OUT_CONF	= $(patsubst $(SRC_CONF)/%, $(BUILD_CONF)/%, $(CONF))
OUT_ICO 	= $(BUILD)/$(LOWPROJECT).ico
OUT_HTML_SVGS	= $(BUILD)/list_SVGs.html
OUT_EXEC	= $(DIST)/$(PROJECT).$(VERSION).msi

############### Commands from variables
ifndef COLOR
	COLOR = blue
endif
CMD_START = cat
ifeq ($(COLOR),red)
	CMD_START = sed -e s/1185E0/ED664C/g -e s/4DCFE0/FDC75B/g
endif
ifeq ($(COLOR),black)
	CMD_START = sed -e s/1185E0/5a5a5a/g -e s/4DCFE0/aaaaaa/g
endif
ifeq ($(COLOR),green)
	CMD_START = sed -e s/1185E0/32CD32/g -e s/4DCFE0/7CFC00/g
endif

#$(info $$OUT_EXEC is [${OUT_EXEC}])

############### Actions of makefile
all: svg conf ico exec

exec: $(OUT_EXEC)

svg: $(OUT_SVGS) $(OUT_HTML_SVGS)

conf: $(OUT_CONF)

ico: $(OUT_ICO)

# use this one to force the rebuild of colored icon
color:
	$(MAKE) -B ico

############### Actual actions
$(BUILD_SVG)/%: $(SRC_SVG)/%
	@mkdir -p $(@D)
	cp $< $@

$(OUT_HTML_SVGS): $(HTML_PY) $(OUT_SVGS) $(OUT_HTML_PY)
	@mkdir -p $(@D)
	cd $(@D); \
	$(PATH_PYTHON) $< -d $(BUILD_SVG:$(BUILD)/%=%) -o $(@F)

$(BUILD_CONF)/%: $(SRC_CONF)/%
	@mkdir -p $(@D)
	cp $< $@

$(OUT_ICO): $(SVG)
	@mkdir -p $(@D)
	$(CMD_START) $< | $(PATH_CONVERT) $(FLAGS_CONVERT_ICO) $@

$(BUILD_SRC)/%: $(SRC)/%
	@mkdir -p $(@D)
	cp $< $@

$(OUT_EXEC): $(OUT_PY) $(SVG) $(SVGS) $(CONF)
	@mkdir -p $(@D)
	cd $(BUILD_SRC); \
	$(PATH_PYTHON) $(<F) 				\
		--setup-project=$(PROJECT)		\
		--setup-script=$(notdir $(PY))		\
		--setup-icon=../$(OUT_ICO:$(BUILD)/%=%)	\
		--setup-version=$(VERSION)		\
		--setup-include=$(LOWPROJECT)		\
		--setup-include-files=../$(BUILD_SVG:$(BUILD)/%=%)	\
		--setup-include-files=../$(BUILD_CONF:$(BUILD)/%=%)	\
		--setup-include-files=../$(OUT_ICO:$(BUILD)/%=%)	\
		--setup-include-files=../$(OUT_HTML_SVGS:$(BUILD)/%=%)	\
		bdist_msi			\
		  --dist-dir ../../$(@D)\
		  -k			\
		  --target-name $(@F)
		#build_exe --build-exe ../$(BUILD_EXE) \
		#bdist_msi --bdist-dir ../$(BUILD_EXE) \
		#          --dist-dir ../$(@D)       \
		#	  -k                          \
		#	  --target-name $(@F)

############### Usual builin actions
.PHONY: clean mrproper
mrproper: clean
	rm -rf $(DIST)
clean:
	rm -rf $(BUILD)
