deschead="""
Cache HAPI data with input from stdin, file, or URL.
Input is passed through to stdout unmodified.

Version: 0.0.1
"""

desctail="""
Examples:

-----------------------------------------
HAPI info response is or is not included as a part of input

Included:
  URLbase='http://hapi-server.org/servers/TestData/hapi
  URLargs='/data?id=dataset1&parameters=scalar,vector&time.min=1970-01-01Z&time.max=1970-01-02'
  curl $URLbase$URLargs'&include=header' | python hapi-cache-write.py

Not included:
  URLinfo=$URLbase'/info?id=dataset1&parameters=scalar,vector'
  curl $URLbase$URLargs | python hapi-cache-write.py --info $URLinfo
-----------------------------------------

-----------------------------------------
HAPI_DATA can be set on command line or set as shell environment variable

Set on command line:
  curl $URLbase$URLargs'&include=header' | python hapi-cache-write.py --HAPI_DATA /tmp

Set as shell environment variable:
  HAPI_DATA=/tmp
  curl $URLbase$URLargs'&include=header' | python hapi-cache-write.py    

-----------------------------------------
"""

import os
import re
import sys
import gzip
import optparse
import tempfile
from json import loads as jsonparse

if sys.version_info[0] > 2:
	from urllib.request import urlopen
else:
	from urllib2 import urlopen

# Read before implementing binary:
# https://stackoverflow.com/questions/2872381/how-to-read-a-file-byte-by-byte-in-python-and-how-to-print-a-bytelist-as-a-binar
# https://stackoverflow.com/questions/48725405/how-to-read-binary-data-over-a-pipe-from-another-process-in-python
# https://stackoverflow.com/questions/2850893/reading-binary-data-from-stdin

parser = optparse.OptionParser(usage='python hapi-cache-write.py [options]', add_help_option=False)

parser.add_option('-h', '--help', dest='help', action='store_true', help='Show this help message and exit')
parser.add_option('--dir', default=os.path.join(tempfile.gettempdir(),'hapi-data'), help='Cache directory will be DIR/hapi-data')
parser.add_option('--info', help='URL or file for info response associated with input. Required if input does not contain HAPI info header.')
parser.add_option('--file', default=None, help='File containing HAPI data')
parser.add_option('--url', default=None, help='URL with response of HAPI data')
parser.add_option('--format', default='csv', help='Format of input')
parser.add_option('--gzip', dest='gzip', action='store_true', help='Gzip output files')
parser.add_option('--log', default='hapi-cache-write.log', help='Format of input')
parser.add_option('--nostdout', dest='nostdout', action='store_true', help='Do not pass stdin to stdout')

(options, args) = parser.parse_args()

if options.help:
    print(deschead)
    parser.print_help()
    print(desctail)
    sys.exit(0)

if os.environ.get('HAPI_DATA'):
	options.dir = os.environ.get('HAPI_DATA')

if not os.path.exists(options.dir):
	os.makedirs(options.dir)

if options.file is not None:
	if options.format != 'csv':
		raise Error('Only --format=csv is implemented')		

flog = open(options.log,'w')

stdout = True
if options.nostdout:
	stdout = False

def prod(arr):
	p = 1
	for i in arr:
		p = p*arr[i]
	return p

def dump(linea, date, columns):

	# TODO: If number of input columns = number of parameter columns,
	# also create a file with all parameters.		

	subdir = os.path.join(options.dir, date[0:4], date[4:6])
	if not os.path.exists(subdir): os.makedirs(subdir)

	date = date.replace("-","")
	for parameter in columns:
		fname = date[0:8] + "." + parameter + "." + options.format
		fname = os.path.join(subdir, fname)
		if options.gzip:
			fname = fname + ".gz"
			fout = gzip.GzipFile(fname, 'wb', compresslevel=0)
		else:
			fout = open(fname, 'wb')

		for i in range(len(linea)):
			cols = list(columns[parameter])
			fout.write(bytes(",".join([ linea[i][j] for j in cols ]).rstrip() + "\n", encoding='utf8'))
		
		flog.write("Wrote %d lines to %s\n" % (len(linea),fname))
		fout.close()

def firstline(linea):

	if re.match(r'[0-9]{4}-[0-9]{3}',linea[0]):
		flog.write("Not implemented.")
		sys.exit(1) # TODO: Handle this case.

	if len(linea[0]) < 10:
		flog.write("Not implemented.")
		sys.exit(1) # TODO: Handle this case.

	daylast = linea[0].replace("-", "")
	flog.write("First line time: " + linea[0] + "\n")
	# If first line has time of 00:00:00:000000000Z or equivalent,
	# start collecting lines by setting daylast to string with day
	# of "00".
	tmp = linea[0]
	for r in ["-", "T", ":", "Z", "."]:
		tmp = tmp.replace(r, "")
	if len(tmp[8:].replace("0","")) == 0:
		flog.write("First line is at time 00:00:00:000000000 or equivalent.\n")
		daylast = "00000000"

	return daylast

if options.file is not None:
	if len(options.file) > 3 and options.file[-3:] == '.gz':
		f = gzip.GzipFile(options.file, 'rb')
	else:
		f = open(options.file, 'rb')
elif options.url is not None:
	f = urlopen(options.url)
else:
	f = sys.stdin.buffer

	# Look at first two bytes to determine if they correspond to the gzip signature.
	first2bytes = f.peek(2)

	# https://docs.python.org/3/library/io.html#io.BufferedReader.peek
	# "The number of bytes returned may be less or more than requested."
	# TODO: Error if less than two bytes
	assert len(first2bytes) > 1, "f.peek(2) did not return enough bytes to determine if stdin is gzipped. This situation is not handled."

	isgzip = False
	if first2bytes[:2] == b'\x1f\x8b':
		isgzip = True

	if isgzip:
		f = gzip.GzipFile(fileobj=sys.stdin.buffer)

line = ""
if options.info is not None:
	# Must be given if headerless data response
	if options.info[0:4] == "http":
		# Info given as URL
		fi = urlopen(options.info)
		lines = fi.read().decode('utf8')
	else:
		# Info given as file
		if len(options.info) > 3 and options.info[-3:] == '.gz':
			with gzip.GzipFile(options.info, 'rb') as fi:
				lines = fi.read()
		else:
			with open(options.info, 'r', encoding='utf8') as fi:
				lines = fi.read()
	json = jsonparse(lines)
else:
	# Header in input data
	flog.write("Expecting header in input data because --info URL or --info FILE not given\n")
	lines = "";
	for line in f:
		line = line.decode('utf8')
		if stdout:
			sys.stdout.write(line)
		if line[0] is not "#":
			break
		else:
			lines = lines + line[1:]
		
	json = jsonparse(lines)

files = {}
columns = {}
ca = 0
cb = -1
for p in range(len(json['parameters'])):
	parameter = json['parameters'][p]['name']
	ca = cb + 1
	if 'size' in json['parameters']:
		cb = ca + prod(json['parameters']['size'])
	else:
		cb = ca
	columns[parameter] = range(ca, cb+1)

linea = []
Lines = []

if line == "":
	collecting = False
	l = 0
else:
	# Header was in stdin, file, or data response
	flog.write("Header was in input.\n")
	collecting = False
	l = 1
	linea = line.split(sep=",")
	daylast = firstline(linea)
	if daylast == "00000000":
		collecting = True
		Lines.append(linea)
		flog.write("Collecting started at time %s\n" % linea[0])

for line in f:

	l = l + 1
	flog.write(str(l) + " " + line.decode())
	line = line.decode('utf8')

	if stdout:
		sys.stdout.write(line)

	linea = line.split(sep=",")

	day = linea[0].replace("-", "")
	if l == 1:
		daylast = firstline(linea)

	if day[6:8] != daylast[6:8]:
		from datetime import datetime, timedelta
		a = datetime.strptime(daylast[0:8],'%Y%m%d')
		b = datetime.strptime(day[0:8],'%Y%m%d')
		flog.write("Gap = %d\n" % (b-a).days)
		for d in range(1,(b-a).days):
			daylastx = a + timedelta(days=d)
			flog.write("Writing empty file for %d%02d%02d\n" % (daylastx.year, daylastx.month, daylastx.day))

		if collecting:
			if daylast != "00000000":
				dump(Lines, daylast, columns)
				Lines = []			
		else:
			if len(Lines) > 0:
				flog.write("First %d lines not dumped.\n" % (l-1))
		
		if not collecting:
			flog.write("Collecting started at time %s\n" % linea[0])
		collecting = True

	daylast = day
	if collecting:
		Lines.append(linea)

flog.write("Last line time: %s\n" % linea[0])
flog.write("Input contained %d data lines.\n" % l)

if len(Lines) > 0:
	flog.write("Last %d lines not dumped.\n" % len(Lines))

flog.close()
