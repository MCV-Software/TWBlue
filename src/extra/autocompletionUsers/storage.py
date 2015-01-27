# -*- coding: utf-8 -*-
import sqlite3, paths

class storage(object):
 def __init__(self, session_id):
  self.connection = sqlite3.connect(paths.config_path("%s/autocompletionUsers.dat" % (session_id)))
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

 def get_all_users(self):
  self.cursor.execute("""select * from users""")
  return self.cursor.fetchall()

 def get_users(self, term):
  self.cursor.execute("""SELECT * FROM users WHERE user LIKE ?""", ('{}%'.format(term),))
  return self.cursor.fetchall()

 def set_user(self, screen_name, user_name, from_a_buffer):
  self.cursor.execute("""insert or ignore into users values(?, ?, ?)""", (screen_name, user_name, from_a_buffer))
  self.connection.commit()

 def remove_user(self, user):
  self.cursor.execute("""DELETE FROM users WHERE user = ?""", (user,))
  self.connection.commit()
  return self.cursor.fetchone()

 def remove_by_buffer(self, bufferType):
  """ Removes all users saved on a buffer. BufferType is 0 for no buffer, 1 for friends and 2 for followers"""
  self.cursor.execute("""DELETE  FROM users WHERE from_a_buffer = ?""", (bufferType,))
  self.connection.commit()
  return self.cursor.fetchone()

 def create_table(self):
  self.cursor.execute("""
  create table users(
user TEXT UNIQUE,
name TEXT,
from_a_buffer INTEGER
)""")

 def __del__(self):
  self.cursor.close()
  self.connection.close()