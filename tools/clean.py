import sys, os, os.path, glob, argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose')
verbose = parser.parse_args().verbose

srcpath = os.path.normpath(os.path.join(sys.path[0], "../src"))
file_count = 0
dir_count = 0
filenames = []
for (path, subdirs, files) in os.walk(srcpath):
 filenames.extend(glob.glob(os.path.join(path, "*.pyc")))
# filenames.extend(glob.glob(os.path.join(path, "*.py")))
for filename in filenames:
 try:
  os.remove(filename)
  if verbose: print "Removed " + filename
  file_count += 1
 except:
  if verbose: print "Can't remove " + filename

#Remove empty directories.
if verbose: print "Removing empty directories..."
run_again = True
while run_again:
 run_again = False
 removals = []
 for (path, subdirs, files) in os.walk(srcpath, topdown=False):
  if len(subdirs) == 0 and len(files) == 0:
   removals.append(path)
 for path in removals:
  try:
   os.rmdir(path)
   run_again = True
   if verbose: print "Removed directory " + path
   dir_count += 1
  except:
   if verbose: print "Can't remove directory " + path

print
print "{0} file(s), {1} dir(s) removed.".format(file_count, dir_count)
