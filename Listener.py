import hug
from DatabaseManagers import CSVDatabaseManager

"""
	Remote server designed to store received logs.
"""

@hug.cli() #sets-up the function to be remotely accessible
@hug.post('/') #sets-up the function to be run in response to any post query to 'http://ip:8000/'

def updateRemoteLogs(body):

	"""
	bief: duplicates locally (in the 'CSVDatabase' directory) all log files sent by the client
	param body: log file updates sent by the client (as a 'name->logs' map)
	"""

	CSVDatabaseManager().write(body)

if __name__ == '__main__': 
	add.interface.cli() #launches the server



