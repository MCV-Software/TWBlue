# -*- coding: cp1252
import sys, os, config

def restart_program():
 """ Function that restarts the application if is executed."""
 config.main.write()
 args = sys.argv[:]
 if not hasattr(sys, "frozen"):
  args.insert(0, sys.executable)
 if sys.platform == 'win32':
  args = ['"%s"' % arg for arg in args]
 os.execv(sys.executable, args)