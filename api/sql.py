import pyodbc
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

MSSQL = pyodbc.connect(
    UID=config.get('mssql','UID'),
    PWD=config.get('mssql','PWD'),
    Driver='{SQL Server}',
    Server=config.get('mssql','SERVERNAME'),
    Database=config.get('mssql','DB')
)
cursor = MSSQL.cursor()

def SQLRecordsCount():
    cursor.execute("select SUM(st.row_count) from sys.dm_db_partition_stats st where object_name(object_id)='News'")
    for row in cursor:
        return row[0]

def GetAllNews():
    cursor.execute("select NewsId, Title, Body, NewsCategoryId from News")
    results = []
    for row in cursor:
        results.append(row)
    return results

def GetAllTitles():
    cursor.execute("select Title from News")
    results = []
    for row in cursor:
        results.append(row[0])
    return results

def GetAllCategories():
    cursor.execute("select NewsCategoryId, Name from NewsCategory")
    results = []
    for row in cursor:
        results.append(row)
    return results