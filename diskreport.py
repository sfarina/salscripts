#! /usr/bin/env python2

#from subprocess import call
import subprocess
import glob
import sys
import os
import re
from optparse import OptionParser
#import getopt
usage = "usage: %prog [options] PATH"
parser = OptionParser(usage=usage)

#options
parser.add_option("-t", "--threshold", dest="threshGB", default=5.,
	action="store", type="float",
	help="Threshold (GB): default = 5.\nThreshold (minimum) size of a directory that is to be expanded.")

parser.add_option("-i", "--ignore", dest="ignoreGB", default=1.5,
	action="store", type="float",
	help="Ignore (GB):  Default = 1.5\nMinimum size of files/directories to list.")

parser.add_option("-v", "--verbose", dest="verbose", default=False,
	action="store_true",
	help="Verbose: Display summary of the small files. Useful with --ignore")

parser.add_option("-u", "--inhuman", dest="human", default=True,
	action="store_false",
	help="not hUman readable: display as bytes instead of MB, GB, etc")

parser.add_option("-r", "--reverse", dest="reverse", default=False,
	action="store_true",
	help="Reverse: display list smallest first")

parser.add_option("-p", "--showdepth", dest="showdepth", default=False,
	action="store_true",
help="show Depth: Print the level of recursion")

parser.add_option("-d", "--depth", dest="DEPTH", default=10,
	action="store", type="int",
	help="only dive so far")

parser.add_option("-c", "--csv", dest="csv", default=False,
	action="store_true",
	help="Csv: print to Excel ready .csv rather than space delimited")

parser.add_option("-b", "--tab", dest="printTAB", default=True,
	action="store_true",
	help="use taBs instead of spaces")

parser.add_option("-s", "--space", dest="printTAB", default=True,
	action="store_false",
	help="Space delimited")

(options,args) = parser.parse_args()

#global definitions
#symbols = ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
symbols = ['K', 'M', 'G']
bytethreshold = options.threshGB*1024.*1024.*1024.
bytemin = options.ignoreGB*1024.*1024.*1024.
small_file_summary = " "

if options.printTAB: delimiter = '\t'
elif options.csv: delimiter = ','
else: delimiter = ' '


def bytes2human(n, i=0):
	f = 1024
	try: n = float(n)
	except: return [n, 'G']
#	print "while"
#	print n
	while n > f*1024:
		i += 1
		f = f * 1024
	try:
		s = symbols[i]
	except:
		s = symbols[-1]
		f = 1024**(len(symbols))

	value = float(n) / float(f)
	return [value, s]
#	return '%3.1f %s' % (value, s)

def pnice(nlet):
	try:
		return "%7.1f %c" % (nlet[0], nlet[1])
	except:
		return "%7s %c" % (nlet[0], nlet[1])
#str.format() unavailable in python v < 2.6
#	return "{0:5.1f}".format(nlet[0])+nlet[1]


def getdu(path, level):
#recursive function to print info in a given directory

#initialization
	fsmaller = 0
	smalltotal = 0

#get all files in path
	greturn = glob.glob(path+"/*")

#sys-util du, flags:  print info in bytes (not blocks), short (not recursive)
#	cmd = 'du -bs'

#mac version
	cmd = 'du -ks'

#build the command
	arg = cmd.split()
	arg = arg + greturn

	try:
    #execute the command
		proc = subprocess.Popen(arg,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #get the output
		result, _ = proc.communicate()
    #	print result
	except OSError as e:
		print e
		result, _ = ("", "")

#string save the block to text to an array of strings
	matrix = [s.split() for s in result.splitlines()]
	errors = [re.sub("[`':]","",s.split()[4]) for s in _.splitlines()]

#	print errors

#convert array of strings to array of [int,string] vectors
	b=[]
	for a in matrix:
#	UNIX
#		if a[1] not in errors: b.append([int(a[0]), a[1]])
#	MAC
		if a[1] not in errors: b.append([1024 * int(a[0]), " ".join(a[1:]) ])

#sort based on size, default is descending order
	if options.reverse: matrix2 = sorted(b, key=lambda x: int(x[0]))
	else: matrix2 = sorted(b, reverse=True, key=lambda x: int(x[0]))

	for nam in errors:
		matrix2.append(['?', nam])

#print the results
	for d in matrix2:
#only care about files bigger than ignoreGB
		if d[0] > bytemin:
			j = level
#print depth
			if options.showdepth:
				if options.csv: print '%d%s'% (level,delimiter),
				else: print '%2d%s'% (level,delimiter),
#indent
			while j > 0:
				if not options.csv: print delimiter,
				j = j - 1
#print size, directory / file
			if options.human: 
				print "%s%c%s" % (pnice(bytes2human(d[0])), ' ', d[1])
			else:
				print "%13d%c%s" % (d[0], delimiter, d[1])
#if file is "small"
		else:
			fsmaller = fsmaller + 1
			smalltotal = smalltotal + d[0]
#if directory is big, go deeper
		if d[0] > bytethreshold:
			if os.path.isdir(d[1]):
				if level < options.DEPTH: getdu(d[1],level + 1)

#print info about small files
	if options.verbose:
		if fsmaller > 0:
#trim the filename off the direcetory
			p = d[1].rpartition('/')
			parent = p[0]+p[1]
			j = level

			s = "%s contains %s in %4d \"small\" files" % (parent, pnice(bytes2human(smalltotal)), fsmaller)
			print s
	

#MAIN
if len(args) > 0:
	mypath = args
else:
	mypath = ['.']

for folder in mypath:
	getdu(folder, 0)

#if options.verbose: print small_file_summary
