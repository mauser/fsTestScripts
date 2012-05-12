from datetime import datetime

class logger:
	def __init__(self, log_file):
		self.log_file = log_file

	def log(self, string ):
		#prints a message to stdout and writes it into a file
		print string

		today = datetime.today()

		logfile = open( self.log_file , "a")
		logfile.write(today.isoformat() + "\t" + string + "\n"  )
		logfile.close()


class CliArguments:
	def __init__( self ):
		self.directory = "/media/nfs/fs"
		self.quick = False
		self.combined = False
		self.combined_n = 100
		self.profiling = False
		self.verbose = False
		self.basename = "testfile-"
		self.loop_n = 1
		self.type = "CRD"
