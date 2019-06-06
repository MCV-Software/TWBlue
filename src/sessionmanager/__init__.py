# -*- coding: utf-8 -*-
""" Module to manage sessions. It can create and configure all sessions.

Contents of this package:
	wxUI: The graphical user interface written in WX Python (for windows). The view.
	session_exceptions: Some useful exceptions when there is an error.
	manager: Handles multiple sessions, setting the configuration files and check if the session is valid. Part of the model.
	session: Creates a twitter session for an user. The other part of the model.
"""
from __future__ import unicode_literals