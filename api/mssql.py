import pyodbc
from django.conf import settings

def get_db_mssql_connection():
    """
    Returns a pyodbc Connection object using configuration from settings.py
    """
    return pyodbc.connect(settings.MSSQL_CONNECTION_STRING)