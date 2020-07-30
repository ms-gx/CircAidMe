/*
Copyright 2020 Michael Schmid, Genexa AG (michael.schmid@genexa.ch)
https://github.com/ms-gx/circaidme

This code is a modified version of:
https://github.com/rrwick/Porechop/blob/master/porechop/src/adapter_align.cpp.
Original author is Ryan Wick (rrwick@gmail.com).

This file is part of CircAidMe. CircAidMe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. CircAidMe is distributed in
the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with CircAidMe. If
not, see <http://www.gnu.org/licenses/>.
*/

#include "adapter_align.h"
#include "seqan/align.h"

#include <iostream>
#include <vector>
#include <limits>
#include <algorithm>
#include <utility>

char * adapterAlignment(char * readSeq, char * adapterSeq, // Called by Python script
                        int matchScore, int mismatchScore, int gapOpenScore, int gapExtensionScore, int score) {

    typedef ModifiedString<String<Dna5>, ModComplementDna>   TMyComplement;
    typedef ModifiedString<TMyComplement, ModReverse> TMyReverseComplement;

    std::stringstream output;

    Dna5String sequenceH = readSeq;
    Dna5String sequenceV = adapterSeq;

    Align<Dna5String, ArrayGaps> alignment;
    resize(rows(alignment), 2);
    assignSource(row(alignment, 0), sequenceH);
    assignSource(row(alignment, 1), sequenceV);
    Score<int, Simple> scoringScheme(matchScore, mismatchScore, gapExtensionScore, gapOpenScore);

    LocalAlignmentEnumerator<Score<int>, Unbanded> enumerator(scoringScheme, score);
    while (nextLocalAlignment(alignment, enumerator))
    {
        output << getScore(enumerator) << ";";
	output << "+;";
        output << clippedBeginPosition(row(alignment, 0)) << ";" << (clippedEndPosition(row(alignment, 0)) - 1) << ";";
        output << clippedBeginPosition(row(alignment, 1)) << ";" <<  (clippedEndPosition(row(alignment, 1)) - 1) << std::endl;
    }

    Align<Dna5String, ArrayGaps> alignment2;
    resize(rows(alignment2), 2);
    TMyReverseComplement rCsequenceV(sequenceV);
    assignSource(row(alignment2, 0), sequenceH);
    assignSource(row(alignment2, 1), rCsequenceV);

    LocalAlignmentEnumerator<Score<int>, Unbanded> enumerator2(scoringScheme, score);
    while (nextLocalAlignment(alignment2, enumerator2))
    {
        output << getScore(enumerator2) << ";";
	output << "-;";
        output << clippedBeginPosition(row(alignment2, 0)) << ";" << (clippedEndPosition(row(alignment2, 0)) - 1) << ";";
        output << clippedBeginPosition(row(alignment2, 1)) << ";" <<  (clippedEndPosition(row(alignment2, 1)) - 1) << std::endl;
    }

    return cppStringToCString(output.str());
}


void freeCString(char * p) { // Called by Python script
    free(p);
}


char * cppStringToCString(std::string cpp_string) { // Only called internally
    char * c_string = (char*)malloc(sizeof(char) * (cpp_string.size() + 1));
    std::copy(cpp_string.begin(), cpp_string.end(), c_string);
    c_string[cpp_string.size()] = '\0';
    return c_string;
}
