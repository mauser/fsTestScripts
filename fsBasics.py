#!/usr/bin/python

#
# Author: Sebastian Moors <mauser@smoors.de> 12.08.2011
# 
# This script can be used to test the basic features
# of a filesystem. We're using it to detect regressions
# in our filesystem. Even though it has the ability 
# to measure the runtime of the atomic tests, it is 
# not meant for performance measurements.

# See fsBasics -h for an overview of available options and arguments.


import os
import sys
import time
import getopt
import stat
from common import CliArguments
from progress_bar import ProgressBar

class basic_tests:

	profiling = False

	def profiling_printer(self, what, how_long):
		if self.profiling:
			print "[profiling]\t " + what + " took " + str(how_long) + " seconds"  

	def __init__(self, args):
		self.working_dir = args.directory
		self.profiling = args.profiling
		self.verbose = args.verbose
		self.basename = args.basename
		self.type = args.type

		if self.working_dir[-1] == "/":
			self.working_dir = self.working_dir[:-1]
		
	
		self.fname = self.working_dir + "/" + self.basename

	def combined_test_run(self, num):
 
	
		fnames = []
		for i in range(1,num): 
			fnames.append( self.working_dir + "/" + self.basename + str(i))


		if self.type.find("C") > -1 or self.type.find("c") > -1:
			a = self.run_test("create_files", self.create_files, fnames)
		else:
			a = True

		if self.type.find("R") > -1 or self.type.find("r") > -1:
			b = self.run_test("compare_with_dir_contents", self.compare_with_dir_contents, fnames)
		else:
			b = True

		if self.type.find("D") > -1 or self.type.find("d") > -1:
			c = self.run_test("delete_files", self.delete_files, fnames) 
		else:
			c = True

		return (a and b and c)


	def run_basic_tests(self):
		#basic file tests
		self.run_test("create_empty_file", self.create_empty_file, self.fname)
		self.run_test("move_file", self.move_file, self.fname)
		self.run_test("change_times", self.change_times, self.fname)
		self.run_test("change_owner", self.change_owner, self.fname)
		self.run_test("change_group", self.change_group, self.fname)
		self.run_test("change_permissions", self.change_permissions, self.fname)
		self.run_test("delete_file", self.delete_file, self.fname)

		#basic dir tests
		self.run_test("create_empty_dir", self.create_empty_dir, self.fname)
		self.run_test("move_file", self.move_file, self.fname)
		self.run_test("change_times", self.change_times, self.fname)
		self.run_test("change_owner", self.change_owner, self.fname)
		self.run_test("change_group", self.change_group, self.fname)
		self.run_test("change_permissions", self.change_permissions, self.fname)
		self.run_test("delete_dir", self.delete_dir, self.fname)


	def run_quick_tests(self):
		'''only run basic tests'''
		self.run_basic_tests()

	def run_combined_tests(self, n):
		''' run a combination of different test'''
		self.run_test("combined_test_run(" + str(n) +")", self.combined_test_run, n )



	def run_test(self,name, function, argument):
		'''run a function and print its return value'''
		if function( argument ):
			print "\033[32m" + "[passed]\t" + "\033[0m" + name
			return True
		else:
			print "\033[31m" + "[failed]\t" + "\033[0m" + name
			return False

	def compare_with_dir_contents(self, fnames):
		'''compare the contents of a dir with the given list'''
		
		r = True
		then = time.time()
		l = os.listdir( self.working_dir )
		now = time.time()
		self.profiling_printer("Reading dir contents", now - then)
		for f in fnames:
			fname = f[f.rfind("/")+1:]
			if fname not in l:
				print str(f) + " was not found in the directory listing"
				r = False
		return r



	#
	# Atomic test cases follow...
	#

	def create_empty_dir(self, fname ):
		'''create an empty directory'''
		try:
			os.mkdir( fname )
		except Exception as (errno, strerror):
			print "Create empty dir: Caught exception " + str(errno) + ":" + strerror
		

		#check if file is existing
		if os.path.isdir( fname ):
			return True
		else:
			return False


	def change_owner(self, fname):
		'''change the owner (uid and gid) of a file'''
		
		#remember the old uid/gid values
		old_uid = os.stat(fname).st_uid
		old_gid = os.stat(fname).st_gid

		#choose a new one (the numbers are meaningless)
		new_uid, new_gid = 20, 20
		
		try:
			os.chown(fname, new_uid, new_gid)
			uid = os.stat(fname).st_uid
			gid = os.stat(fname).st_gid
			
			if uid != 20 or gid != 20:
				return False


		except Exception as (errno, strerror):
			print "Change owner: Caught exception " + str(errno) + ":" + strerror
			return False
		
		#restore the old uid/gid values after test was done
		os.chown(fname, old_uid, old_gid); 

		return True

	def change_group(self, fname):
		'''change the owner (uid and gid) of a file'''
		
		#remember the old uid/gid values
		old_uid = os.stat(fname).st_uid
		old_gid = os.stat(fname).st_gid

		#choose a new one (the numbers are meaningless)
		new_gid = 20
		
		try:
			os.chown(fname, old_uid, new_gid)
			uid = os.stat(fname).st_uid
			gid = os.stat(fname).st_gid
			
			if uid != old_gid or gid != 20:
				return False


		except Exception as (strerror):
			print "Change group: Caught exception :" + str(strerror)
			return False
		
		#restore the old uid/gid values after test was done
		os.chown(fname, old_uid, old_gid); 

		return True




	def change_permissions(self, fname):
		'''change the permission of a file'''

		old_mode = os.stat(fname).st_mode
		try:
			os.chmod(fname, 0000)
			st_old_mode = os.stat(fname).st_mode
			
			
			os.chmod(fname, stat.S_IXOTH)
			st_new_mode = os.stat(fname).st_mode

			if st_new_mode - st_old_mode == 1:
				return True
			else:
				return False

					


		except Exception as (strerror):
			print "Change permission: Caught exception:" + str(strerror)
			return False
		
		#restore the old mode values after test was done
		os.chmod(fname, old_mode)

		return True


		

	def change_times(self, fname):
		'''change the atime and mtime of a file'''

		stat_obj = os.stat(fname)
		mtime = stat_obj.st_mtime
		atime = stat_obj.st_atime


		try:
			os.utime(fname, (0,0) )
			stat_obj = os.stat(fname)
		
		
			if stat_obj.st_mtime != 0 or stat_obj.st_atime != 0:
				return False

		except Exception as (strerror):
			print "Change timestamps: Caught exception:" + str(strerror)
			return False
		
		#restore the old atime/mtime values after test was done
		os.utime(fname, (atime,mtime) )

		return True



	def move_file(self, fname):
		'''moves the file from fname to fname-moved and back'''
		

		was_dir = os.path.isdir(fname)
		was_file = os.path.isfile(fname)

		new_name = fname + "-moved"

		try:
			os.rename(fname, new_name)
		
			if was_dir and not os.path.isdir(new_name):
				return False
		
			if was_file and not os.path.isfile(new_name):
				return False

		except Exception as (strerror):
			print "Move file: Caught exception:" + str(strerror)
			return False
		
		#restore the old uid/gid values after test was done
		os.rename(new_name, fname)

		return True




	def create_empty_file(self, fname ):
		'''create an empty file'''
		try:
			f = open( fname, "w" );
			f.close()
		except Exception as (errno, strerror):
			print "Create file: Caught exception " + str(errno) + ":" + strerror
			return False	

		#check if file is existing
		if os.path.isfile( fname ):
			return True
		else:
			print "File " + fname + " is not existing"
			return False




	def delete_file(self, fname ):
		'''delete a file'''
		
		try:
			os.unlink( fname )
		except Exception as (errno, strerror):
			print "Delete file: Caught exception " + str(errno) + ":" + strerror


		#check if file is existing
		if os.path.isfile( fname ):
			return False
		else:
			return True

	def delete_dir(self, fname ):
		'''delete a directory'''
		
		try:
			os.rmdir( fname )
		except Exception as (errno, strerror):
			print "Delete dir: Caught exception " + str(errno) + ":" + strerror
			return False

		#check if file is existing
		if os.path.isdir( fname ):
			return False
		else:
			return True

	def create_files(self, file_list ):
		'''create files. The filenames are supplied as a list'''
		count = 0
		total = len(file_list)
		
		if self.verbose: print "\nTrying to create " + str(total) + " files"
		
		prog = ProgressBar(count, total, 77, mode='fixed', char='#')
	
		counter = 0
		last_time =time.time()

		before = time.time()
		for file_name in file_list:
			ret = self.create_empty_file( file_name )
		    	
			if self.verbose:
				count += 1
				prog.increment_amount()
				print prog, '\r',
				sys.stdout.flush()

			if ret == False:
				print "Failed to create file " + str( file_name )
				return False
			else:
				counter+=1

			if counter % 1000 == 0 and self.profiling:
				diff = time.time() - last_time
				last_time = time.time()	
				f = open("/tmp/basicStat.csv","a")
				f.write(str(counter) + "," + str(diff) + "\n")
				f.flush()
				f.close()
		print

		after = time.time()
		files_per_second = str( len(file_list) / (after-before) )
		self.profiling_printer("Creating " + str(len(file_list)) + " files (" + files_per_second +  " per second)", after - before)

		return True

	def delete_files(self, file_list ):
		'''create files. The filenames are supplied as a list'''
		
		
		count = 0
		total = len(file_list)
		if self.verbose: print "\nTrying to delete " + str(total) + " files"
		prog = ProgressBar(count, total, 77, mode='fixed', char='#')
		
		before = time.time()
		for file_name in file_list:
			ret = self.delete_file( file_name )
			
			if self.verbose:
				count += 1
				prog.increment_amount()
				print prog, '\r',
				sys.stdout.flush()

			
			if ret == False:
				print "Failed to delete file " + str( file_name )
				return False
		print

		after = time.time()
		self.profiling_printer("Deleting " + str(len(file_list)) + " files", after - before)
		return True



def usage():
	print "Welcome to fsBasics.py, a testing tool for filesystems."
	print "Options:"
	print "\t -h, --help:\t\tPrint this help message"
	print "\t -d, --directory dir:\t\tSpecify the working directory for this script"
	print "\t -q, --quick:\t\tCheck basic functions"
	print "\t -c, --combined n:\t\t Create, list and delete n (empty) files"
	print "\t -p, --profiling:\t\t Show how long each operation took"
	print "\t -l, --loop n:\t\t Repeat the whole process n times"
	print "\t -t, --type [CDR]:\t\t Specify which operations should be done in a combined test run (Create, Delete, Readdir)."


if __name__ == "__main__":

	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hd:qc:pvb:l:t:", ["help", "directory", "quick","combined","profiling","verbose","basename","loop","type"])
	except getopt.GetoptError, err:
		print str(err) 
		usage()
		sys.exit(2)

	cliArguments = CliArguments()

	for o, a in opts:
		if o in ("-q", "--quick" ):
		    cliArguments.quick = True

		if o in ("-p", "--profiling" ):
		    cliArguments.profiling = True

		if o in ("-d", "--directory"):
		    cliArguments.directory = a
		
		if o in ("-b", "--basename"):
		    cliArguments.basename = a
		
		if o in ("-v", "--verbose"):
		    cliArguments.verbose = True
		
		if o in ("-c", "--combined"):
		    cliArguments.combined = True
		    cliArguments.combined_n = int(a) 

		if o in ("-l", "--loop"):
		    cliArguments.loop_n = int(a) 

		if o in ("-t", "--type"):
		    cliArguments.type = a 

		if o in ("-h", "--help"):
		    usage()
		    sys.exit()

	
			
			
	if cliArguments.quick or not cliArguments.combined:
		print "Performing quick run on: " + cliArguments.directory + "\n"
		for i in range(0, cliArguments.loop_n):
			b = basic_tests( cliArguments )
			b.run_quick_tests()
		sys.exit(0)

	if cliArguments.combined:
		print "Performing combined test run on: " + cliArguments.directory + "\n"
		for i in range(0, cliArguments.loop_n):
			b = basic_tests( cliArguments )
			b.run_combined_tests( cliArguments.combined_n )
		sys.exit(0)

	#you will never end up here if you read the nice manual :)
	usage()
