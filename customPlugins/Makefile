#MayaPlugin Makefile

##################################
## MAYA VERSION AND LOCATION
##################################
MAYA_MAJOR_VERSION=2017
MAYA_MINOR_VERSION=0.5
MAYA_LOCATION=/pipeline/el7/software/maya/$(MAYA_MAJOR_VERSION).$(MAYA_MINOR_VERSION)/usr/autodesk/maya$(MAYA_MAJOR_VERSION)

MAYA_SDK=$(DEVKIT_LOCATION)

MAYA_INCLUDE=-I$(MAYA_SDK)/include
MAYA_LIB=-L$(MAYA_LOCATION)/lib -lOpenMaya -lOpenMayaAnim

##################################
## PLUGIN OUTPUT
##################################
LIBRARY=oouCfx.so


##################################
## PLUGIN SOURCES
##################################
SOURCES=$(shell find src/ -name '*.cpp')
HEADERS=${shell find include/ -name '*.h'}
OBJECTS=$(SOURCES:.cpp=.o)

##################################
## COMPILER OPTIONS
##################################
CPP = g++
LD = $(CPP)

INCLUDE_FLAGS= $(MAYA_INCLUDE) -Iinclude/
LIB_FLAGS= $(MAYA_LIB)

CFLAGS = -DBits64_ -m64 -DUNIX -D_BOOL -DLINUX -DFUNCPROTO -D_GNU_SOURCE \
		 -DLINUX_64 -fPIC \
		 -fno-strict-aliasing -DREQUIRE_IOSTREAM -Wall \
		 -Wno-multichar -Wno-comment -Wno-sign-compare -funsigned-char \
		 -pthread

debug: CFLAGS += -DDEBUG -g -O0
install: CFLAGS += -O3

CPPFLAGS = $(CFLAGS) -std=c++11 -Wno-deprecated -Wno-reorder -fno-gnu-keywords

LFLAGS = $(CPPFLAGS) -Wl,-Bsymbolic -shared


##################################
## COMPILE TARGETS
##################################
.cpp.o: $(SOURCES) $(HEADERS)
	$(CPP) -c $< $(CPPFLAGS) $(INCLUDE_FLAGS) -o $@

$(LIBRARY): $(OBJECTS)
	 $(CPP) $(OBJECTS) $(LFLAGS) $(LIB_FLAGS) -o $@

install: $(LIBRARY)
	cp -f $(LIBRARY) ../../../build/ooutdmaya2017_plugins/plug-ins

debug: $(LIBRARY)
	cp -f $(LIBRARY) ../../../build/ooutdmaya2017_plugins/plug-ins

clean:
	rm -f src/*.o
	rm -f *.so
