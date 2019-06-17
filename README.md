LogServer
===========

This is a python plugin for receiving, storing and displaying the results of the analysis. It was tested:

  - With Python 3.7.1
  - On Ubuntu 18.04

See [/doc/index.html](index.html) for the API.

Dependencies
-------------

  - [dash, dash_core_components, dash_html_components](https://dash.plot.ly/installation): Allows easy setup a server with an analytics-oriented visual interface, go to the linked page for intallation instructions
  - [plotly](https://plot.ly/python/getting-started/): Displays interactive plots of many kinds, go to the linked page for intallation instructions
  - [pandas](https://pandas.pydata.org/pandas-docs/stable/install.html): Among other things, allows easy access to local or online CSV files, go to the linked page for intallation instructions
  - [hug](http://www.hug.rest/website/quickstart): Allows easy setup of basic non-specialized servers, go to the linked page for intallation instructions

Utilization:
-------------

Listener.py
------------

	Launch: hug -f Listener.py
	Access: /IP:8000/

Converter.py
-------------

	Launch: python Converter.py
	Access: /IP:8051/


Emitter.py
-----------

	Launch: python Emiter.py
	Access: /IP:8050/

Generate Mock Data For The Data Visualization Interface (Emitter.py)
---------------------------------------------------------------------
	Use TestSetup.py




