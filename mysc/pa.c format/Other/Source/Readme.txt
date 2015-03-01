You can get tw blue's source code at https://github.com/manuelcortez/TWBlue

LICENSE
=======

This package's installer and launcher are released under the GPL. The launcher
is the PortableApps.com Launcher, available with full source and documentation
from http://portableapps.com/development. We request that developers using the
PortableApps.com Launcher please leave this directory intact and unchanged.

USER CONFIGURATION
==================

Some configuration in the PortableApps.com Launcher can be overridden by the
user in an INI file next to TWBluePortable.exe called TWBluePortable.ini.
If you are happy with the default options, it is not necessary, though.  There
is an example INI included with this package to get you started.  To use it,
copy AppNamePortable.ini from this directory to TWBluePortable.ini next to
TWBluePortable.exe. The options in the INI file are as follows:

   AdditionalParameters=
   DisableSplashScreen=false
   RunLocally=false

(There is no need for an INI header in this file; if you have one, though, it
won't damage anything.)

The AdditionalParameters entry allows you to pass additional command-line
parameters to the application.

The DisableSplashScreen entry allows you to run the launcher without the splash
screen showing up.  The default is false.

The RunLocally entry allows you to run the portable application from a read-
only medium. This is known as Live mode. It copies what it needs to to a
temporary directory on the host computer, runs the application, and then
deletes it afterwards, leaving nothing behind. This can be useful for running
the application from a CD or if you work on a computer that may have spyware or
viruses and you'd like to keep your device set to read-only. As a consequence
of this technique, any changes you make during the Live mode session aren't
saved back to your device.  The default is false.
