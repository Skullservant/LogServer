import sqlite3
import os
import pandas as pd
import numpy as np

class CSVDatabaseManager:

	""" class representing and managing a CSV file database with the given name"""

	def __init__(self,name="/CSVDatabase"):

		"""
		bief: constructor of the database manager (it also creates the actual database if it doesn't yet exist)
		param name: name of the directory representing the database
		"""

		self.path=os.path.dirname(os.path.abspath(__file__))+name
		if not os.path.exists(self.path):
    			os.mkdir(self.path)

	def names(self):

		"""
		bief: reads the name of all stored files
		return: a list containing the name of all stored files
		"""

		f=open(self.path+"/CSVDatabaseManager.txt", "a+")
		f.seek(0)
		names=f.read().split('\n')
		f.close()
		return names[:len(names)-1]

	def write(self, files):

		"""
		bief: adds or updates all given files to the database
		param files: dictionary mapping csv file names to the corresponding content to add
		"""

		new_names=[]
		for name in files:
			lines=files[name][0]
			for elem in files[name][1:]:
				lines+=','+elem
			f= open(self.path+'/'+name, "a")
			f.write(lines)
			f.close()
			if(name not in self.names()):
				new_names.append(name)
		f=open(self.path+"/CSVDatabaseManager.txt", "a")
		f.write('\n'.join(new_names)+'\n')
		f.close()

	def read(self, name):

		"""
		bief: reads the content of the specified CSV file
		param names: the name of the file to read
		return: a dictionary mapping each parameter of the CSV file to the corresponding values
		"""

		if name==None:
			return {}
		return pd.read_csv(self.path+'/'+name)

class MainDatabaseManager:

	""" class managing a SQLite3 database with the given name"""

	def __init__(self,name='Main.db'):

		"""
		bief: constructor of the database manager (it also creates the actual database if it doesn't yet exist)
		param name: name of the database
		"""

		self.dbname=name
		if not os.path.isfile(self.dbname):
			self._create()

	def write(self, name, rows, update):

		"""
			bief: adds the given rows to the table of the given name, ignoring collisions or performing an update in case there's one, depending on the value of "update"
			param name: name of the table to update
			param rows: list of tuples representing each a row to add to the table
			param update: boolean indicating whether to overwrite existing lines or not
		"""

		db = sqlite3.connect(self.dbname)
		c = db.cursor()
		if update:
			op='REPLACE'
		else:
			op='INSERT OR IGNORE'
		for row in rows:
			c.execute(op+' INTO '+name+' VALUES ('+(', ').join(['"'+str(e)+'"' for e in row])+')')
		db.commit()
		db.close()

	def names(self):

		"""
			bief: reads the name of all the tables in the database
			return: list of the table names
		"""

		db = sqlite3.connect(self.dbname)
		c = db.cursor()
		c.execute('''SELECT name FROM sqlite_master WHERE type= "table"''')
		names=[i[0] for i in c.fetchall()]
		db.close()
		return np.array(names)

	def keys(self, name):

		"""
			bief: returns the name of each of the keys of the table with the given name
			param name: name of the table to get the key names from
			return: list of the key names
		"""

		db = sqlite3.connect(self.dbname)
		db.row_factory = sqlite3.Row
		c = db.cursor()
		request='SELECT * FROM '+name
		c.execute(request)
		keys=[d[0] for d in c.description]
		db.close()
		return np.array(keys)

	def read(self, name, filters, columns):

		"""
			bief: reads the table with the given name after having applied the given filters on it
			param name: name of the table to read
			param filters: list of lists representing each the values to keep for the primary 
			key with same index (an empty list meaning no restriction)
			param columns: name of the the columns to retrieve from the specified table
			return: the wanted filtered table
		"""

		k=self.keys(name)
		req_opt=['WHERE']
		for i,fil in enumerate(filters):
			if len(fil)!=0:
				req_opt+=[k[i]+' IN ('+(', ').join(['"'+str(e)+'"' for e in fil])+')', 'AND']
		req_opt=req_opt[:len(req_opt)-1]
		request='SELECT '+((', ').join(columns) if len(columns)!=0 else '*')+' FROM '+name
		if len(req_opt)!=0:
			request+=' '+(' ').join(req_opt)
		db = sqlite3.connect(self.dbname)
		c = db.cursor()
		c.execute(request)
		table=c.fetchall()
		db.close()
		return np.array([list(t) for t in table])

	def _create(self):

		"""brief: builds a new database with the given name (warning: do not run this if the database has already been built!)"""

		db = sqlite3.connect(self.dbname)
		c = db.cursor()

		#Conventions:
		#robot_id is the MAC address of the robot
		#game_id is the unique identifier of the activity
		#user_id is the unique identifier of the player
		#iter is the iteration of the activity (ex: iter=4 <=> it's the 4th time that the activity has been launched)
		#timestamp is the amount of milliseconds since 01/01/1970
		#x is the x-coordinate of the robot
		#y is the y-coordinate of the robot
		#theta is the rotation angle of the robot

		c.execute('''CREATE TABLE Position (robot_id integer NOT NULL, game_id integer NOT NULL, user_id integer NOT NULL, iter integer NOT NULL, timestamp integer NOT NULL, x real, y real, theta real, PRIMARY KEY (robot_id, game_id, user_id, iter, timestamp))''')

		#Conventions:
		#robot_id is the MAC address of the robot
		#game_id is the unique identifier of the activity
		#user_id is the unique identifier of the player
		#zone_id is the unique identifier of the zone triggering the event
		#iter is the iteration of the activity (ex: iter=4 <=> it's the 4th time that the activity has been launched)
		#timestamp is the amount of milliseconds since 01/01/1970
		#event is the name of the recorded event ("kidnap", "border" or "inner")
		#state is the identifier of the state associated at that point with the recorded event (finite options, so represented with an integer)
		#for "kidnap", state=1 at the start, state=0 at the end
		#for "border", state=1 when crossing the border
		#for "inner", state=1 when entering the zone, state=0 when exiting it

		c.execute('''CREATE TABLE DiscreteEvent (robot_id integer NOT NULL, game_id integer NOT NULL, user_id integer NOT NULL, zone_id integer NOT NULL, iter integer NOT NULL, timestamp integer NOT NULL, event text NOT NULL, state integer, PRIMARY KEY (robot_id, game_id, user_id, zone_id, iter, timestamp, event))''')

		#Conventions:
		#robot_id is the MAC address of the robot
		#game_id is the unique identifier of the activity 
		#user_id is the unique identifier of the player
		#zone_id is the unique identifier of the zone triggering the event
		#iter is the iteration of the activity (ex: iter=4 <=> it's the 4th time that the activity has been launched)
		#timestamp is the amount of milliseconds since 01/01/1970
		#event is the name of the recorded event (can only be "distance" for now)
		#value is the measure associated with the recorded event (infinite options, so represented with a float)
		#for "distance", value=3.5 <=> the distance to the zone is 3.5

		c.execute('''CREATE TABLE ContinuousEvent (robot_id integer NOT NULL, game_id integer NOT NULL, user_id integer NOT NULL, zone_id integer NOT NULL, iter integer NOT NULL, timestamp integer NOT NULL, event text NOT NULL, value real, PRIMARY KEY (robot_id, game_id, user_id, zone_id, iter, timestamp, event))''')

		#Conventions:
		#game_id is the unique identifier of the activity 
		#name is the name of the activity (ex: "Handwriting")

		c.execute('''CREATE TABLE Game (game_id integer NOT NULL PRIMARY KEY, name text)''')

		#Conventions:
		#game_id is the unique identifier of the user
		#name is the name of the user (ex: "Scrooge McDuck")

		c.execute('''CREATE TABLE User (user_id integer NOT NULL PRIMARY KEY, name text)''')

		#Conventions:
		#game_id is the unique identifier of the zone 
		#name is the name of the zone (ex: "Letter a")

		c.execute('''CREATE TABLE Zone (zone_id integer NOT NULL PRIMARY KEY, name text)''')
		db.commit()
		db.close()
			
