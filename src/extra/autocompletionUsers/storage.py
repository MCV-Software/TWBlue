# -*- coding: utf-8 -*-
import sqlite3, paths
from sessionmanager import manager

class storage(object):
 def __init__(self):
  self.connection = sqlite3.connect(paths.config_path("%s/autocompletionUsers.dat" % (manager.manager.get_current_session())))
  self.cursor = self.connection.cursor()
  if self.table_exist("users") == False:
   self.create_table()

 def table_exist(self, table):
  ask = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % (table))
  answer = ask.fetchone()
  if answer == None:
   return False
  else:
   return True

 def get_users(self, term):
  self.cursor.execute("""SELECT * FROM users WHERE user LIKE ?""", ('{}%'.format(term),))
  return self.cursor.fetchall()

 def set_user(self, screen_name, user_name):
  self.cursor.execute("""insert or ignore into users values(?, ?)""", (screen_name, user_name))
  self.connection.commit()

 def remove_user(self, user):
  self.cursor.execute("""DELETE FROM users WHERE user = ?""", (user,))
  return self.cursor.fetchone()

 def create_table(self):
  self.cursor.execute("""
  create table users(
user TEXT UNIQUE,
name TEXT
)""")

 def __del__(self):
  self.cursor.close()
  self.connection.close()