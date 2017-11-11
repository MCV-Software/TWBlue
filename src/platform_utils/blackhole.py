# Replacement for py2exe distributed module
# Avoids the use of the standard py2exe console.
# Just import this file and it should go away

from builtins import object
import sys
if hasattr(sys,"frozen"): # true only if we are running as a py2exe app
 class Blackhole(object):
  def write(self,text):
   pass
  def flush(self):
   pass
 sys.stdout = Blackhole()
 sys.stderr = Blackhole()
 del Blackhole
 del sys

