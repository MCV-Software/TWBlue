# -*- coding: cp1252
import sys, os

def restart_program():
 """ Function that restarts the application if is executed."""
 args = sys.argv[:]
 if not hasattr(sys, "frozen"):
  args.insert(0, sys.executable)
 if sys.platform == 'win32':
  pidpath = os.path.join(os.getenv("temp"), "client.pid")
  if os.path.exists(pidpath):
   os.remove(pidpath)
  args = ['"%s"' % arg for arg in args]
 os.execv(sys.executable, args)