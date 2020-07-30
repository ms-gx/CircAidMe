"""
Copyright 2020 Michael Schmid, Genexa AG (michael.schmid@genexa.ch)
https://github.com/ms-gx/circaidme

This file is part of CircAidMe. CircAidMe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. CircAidMe is distributed in
the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with CircAidMe. If
not, see <http://www.gnu.org/licenses/>.
"""

# own modules
from circaidme import parameter
from circaidme.version import __version__

# external modules
import datetime


# class "Log" is used to handle all the logging jobs:
class Log:
	def __init__(self, path):
		self.path = path
		self.starttime = None
	
	def add_line(self, log_line):
		with open(self.path, 'a') as out_f:
			out_f.write(log_line + "\n")

	def note_start(self):
		self.starttime = datetime.datetime.now()
		start_msg = "Starting analysis: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		with open(self.path, 'a') as out_f:
			out_f.write("**************************************" + "\n")
			out_f.write("This is CircAidMe v" + __version__ + "\n")
			out_f.write(start_msg + "\n")
			out_f.write("**************************************" + "\n" + "\n")

	def note_done(self):
		done_msg = "Finished analysis: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		duration = datetime.datetime.now() - self.starttime
		days = divmod(duration.total_seconds(), 86400) 
		hours = divmod(days[1], 3600)
		minutes = divmod(hours[1], 60) 
		seconds = divmod(minutes[1], 1) 
		with open(self.path, 'a') as out_f:
			out_f.write("******************************************************" + "\n")
			out_f.write(done_msg + "\n")
			out_f.write("Runtime was: %d days, %d hours, %d minutes and %d seconds \n" % (days[0], hours[0], minutes[0], seconds[0]))
			out_f.write("******************************************************" + "\n" + "\n")

	def note_stop(self):
		stop_msg = "Analysis was interrupted by user before it finished!: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		with open(self.path, 'a') as out_f:
			out_f.write("*************************************************************************" + "\n")
			out_f.write(stop_msg + "\n")
			out_f.write("*************************************************************************" + "\n" + "\n")

	def note_command(self, args):
		with open(self.path, 'a') as out_f:
			out_f.write("*** Executed command ***" + "\n")
			for arg in vars(args):
			    out_f.write(arg + ": " + str(getattr(args, arg)) + "\n")
			out_f.write("\n")

