# Copyright 2020 Michael Schmid, Genexa AG (michael.schmid@genexa.ch)
# https://github.com/ms-gx/circaidme
#
# This file is part of CircAidMe. CircAidMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version. CircAidMe is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public License along with CircAidMe. If
# not, see <http://www.gnu.org/licenses/>.


# This makefile will build the C++ parts of CircAidMe.
# This makefile works only for Linux systems and NOT on Mac

CXX          = g++
CXXFLAGS     = -Wall -Wextra -pedantic -mtune=native

# These flags are required for the build to work.
FLAGS        = -std=c++14 -Isrc/include -fPIC -O3 -D NDEBUG
LDFLAGS      = -shared

TARGET       = circaidme/lib/seqan2_functions.so
SHELL        = /bin/sh
SOURCES      = $(shell find src -name "*.cpp")
HEADERS      = $(shell find src -name "*.h")
OBJECTS      = $(SOURCES:.cpp=.o)

$(TARGET): $(OBJECTS)
	$(CXX) $(FLAGS) $(CXXFLAGS) $(LDFLAGS) -Wl,-soname,$(TARGET) -o $(TARGET) $(OBJECTS)

# Only removes objects (not needed to run CircAidMe)
clean:
	$(RM) $(OBJECTS)

# Also removes the .so-file
clean_full: clean
	$(RM) $(TARGET)

%.o: %.cpp $(HEADERS)
	$(CXX) $(FLAGS) $(CXXFLAGS) -c -o $@ $<
