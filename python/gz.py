import sys
import gzip

from datetime import datetime
daylast = '2009-01-01'
day = '2009-01-03'

sys.exit(0)

file = 'abc.gz'
if file[-3:] == '.gz':
	print('file is gzipped')
	sys.exit(0)
f = sys.stdin.buffer

raise NotImplemented

# Look at first two bytes to determine if they correspond to the gzip signature.
first2bytes = f.peek(2)
if len(first2bytes) < 2:
	# https://docs.python.org/3/library/io.html#io.BufferedReader.peek
	# "The number of bytes returned may be less or more than requested."
	# TODO: Error if less than two bytes
	pass
else:
	isgzip = False
	if first2bytes[:2] == b'\x1f\x8b':
		isgzip = True

if isgzip:
	f = gzip.GzipFile(fileobj=sys.stdin.buffer)
	for line in f:
		sys.stdout.write(line.decode('utf8')+"\n")
else:
	for line in f:
		sys.stdout.write(line.decode('utf8')+"\n")
f.close()

#f = gzip.GzipFile('a.gz', 'wb', compresslevel=0)
#f.write('test'.encode())
#f.close()
