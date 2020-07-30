"""
Copyright 2020 Michael Schmid, Genexa AG (michael.schmid@genexa.ch)
https://github.com/ms-gx/circaidme

This code is a modified version of:
https://github.com/rrwick/Porechop/blob/master/porechop/cpp_function_wrappers.py.
Original author is Ryan Wick (rrwick@gmail.com).

CircAidMe makes use of C++ functions which are compiled in seqan2_functions.so. This module uses ctypes
to wrap them in Python functions.

This file is part of CircAidMe. CircAidMe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. CircAidMe is distributed in
the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with CircAidMe. If
not, see <http://www.gnu.org/licenses/>.
"""

# external modules
import os
import sys
from ctypes import CDLL, cast, c_char_p, c_int, c_void_p


SHARED_LIB_SEQAN2 = 'lib/seqan2_functions.so'
SHARED_LIB_SEQAN2_FULL = os.path.join(os.path.dirname(os.path.realpath(__file__)), SHARED_LIB_SEQAN2)
if not os.path.isfile(SHARED_LIB_SEQAN2_FULL):
	sys.exit('could not find ' + SHARED_LIB_SEQAN2)
C_LIB = CDLL(SHARED_LIB_SEQAN2_FULL)


# "adapterAlignment" is the C++ function utilizing SeqAn2 to align adapter to read sequence.
C_LIB.adapterAlignment.argtypes = [c_char_p,  # Read sequence
                                   c_char_p,  # Adapter sequence
                                   c_int,     # Match score
                                   c_int,     # Mismatch score
                                   c_int,     # Gap open score
                                   c_int,     # Gap extension score
                                   c_int]     # Score threshold
C_LIB.adapterAlignment.restype = c_void_p     # Pointer to string describing alignment (returned from SeqAn2)


# "freeCString" cleans up the heap memory for the C string returned by "adapterAlignment". It must be called after "adapterAlignment".
C_LIB.freeCString.argtypes = [c_void_p] # Pointer to C string
C_LIB.freeCString.restype = None        # Returns nothing


def adapter_alignment(read_sequence, adapter_sequence, scoring_scheme_vals, score):
	"""
	Python wrapper for "adapterAlignment" C++ function.
	"""
	match_score = scoring_scheme_vals[0]
	mismatch_score = scoring_scheme_vals[1]
	gap_open_score = scoring_scheme_vals[2]
	gap_extend_score = scoring_scheme_vals[3]
	ptr = C_LIB.adapterAlignment(read_sequence.encode('utf-8'), adapter_sequence.encode('utf-8'),
                                     match_score, mismatch_score, gap_open_score, gap_extend_score, score)
	result_string = c_string_to_python_string(ptr)
	return result_string


def c_string_to_python_string(c_string):
	"""
	This function casts a C string to a Python string and then calls C++ function "freeCString" to delete the C
	string from the heap.
	"""
	python_string = cast(c_string, c_char_p).value.decode() # Cast C string to Python string
	C_LIB.freeCString(c_string)                             # Remove C string from heap
	return python_string                                    # Return the Python string

