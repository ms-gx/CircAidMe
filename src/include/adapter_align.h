/*
Copyright 2020 Michael Schmid, Genexa AG (michael.schmid@genexa.ch)
https://github.com/ms-gx/circaidme

This code is a modified version of:
https://github.com/rrwick/Porechop/blob/master/porechop/include/adapter_align.h.
Original author is Ryan Wick (rrwick@gmail.com).

This file is part of CircAidMe. CircAidMe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. CircAidMe is distributed in
the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with CircAidMe. If
not, see <http://www.gnu.org/licenses/>.
*/

#ifndef ADAPTER_ALIGN_H
#define ADAPTER_ALIGN_H


#include "seqan/sequence.h"

#include <string>
#include <vector>


using namespace seqan;


// Functions that are called by the Python script must have C linkage, not C++ linkage.
extern "C" {
    char * adapterAlignment(char * readSeq, char * adapterSeq,
                            int matchScore, int mismatchScore, int gapOpenScore, int gapExtensionScore, int score);
    void freeCString(char * p);
}

char * cppStringToCString(std::string cpp_string);


#endif // ADAPTER_ALIGN_H
