import _mysql
from MySQLdb.constants import FIELD_TYPE

class DictObject(object):
  """
    Class that creates dynamic attributes from a specified dictionary
  """
  def __init__(self, dict):
    """
      Constructor
      
      Parameter:
        dict - Dictionary with attributes for object
    """
    self._dict = dict
    
  def __getattribute__( self, name):
    """
      Get attribute hook
      
      Parameter:
        name - Name of attribute
    """
    # Get internal _dict attribute
    dict = object.__getattribute__(self, "_dict")
    
    # if attribute define in dict, use that it
    # otherwise use real attribute of class
    if name in dict:
      return dict[name]
    else:
      return object.__getattribute__(self, name)
  

class DBDictGenerator:
  """
    Class that creates a dictionary from the results of a DB query
  """
  def __init__( self, db, query):
    db.query(query)
    self.result = db.store_result()

  def generate_dict(self):
    (dict,) = self.result.fetch_row(1,1)
    return dict
  
class Row(DictObject):
  """
    Class that represents a row result of a database query
    with dynamic attributes of a python object
  """
  def __init__( self, generator):
    """
      Constructor
      
      Requires a generator object that has a generate_dict()
      method that returns a dictionary with the desired attribute
      
      Parameter:
        generator - Generator of internal dictonary for attributes
    """
    DictObject.__init__( self, generator.generate_dict())
    
  def __str__( self ):
    dict = object.__getattribute__(self, "_dict")

    return str(dict)
    
class SimpleDictGenerator:
  """
    Simple DictGenerator object that simple returns a specified
    dictionary
  """
  def __init__(self, dict):
    self.dict = dict
    
  def generate_dict(self):
    return self.dict

def open_database( host, db_name, config_file):
  my_conv = { FIELD_TYPE.LONG: int }
  config = open(config_file)
  line = config.readline()
  (user, password) = line.split()
  db = _mysql.connect(host=host, user=user, passwd=password, 
                      db=db_name, conv=my_conv)
  return db


def table_generator( db, query):
  """
    A generator function that returns the rows of a database query
    
    Parameters:
      db - Database connection
      query - Query to use
      
  """
  db.query(query)
  result = db.store_result()
  done = False
  while not done:
    row = result.fetch_row(1,1)
    done = len(row) == 0
    if not done:
      (dict,) = row
      yield Row(SimpleDictGenerator(dict))

def get_table( db, table_name, key_name, suffix=None, columns='*'):
  """
    Get table as a dictonary of items keyed by database key
    
    This method only works with a single field database key
    
    Parameters:
      db - Database connection 
      table_name - Name(s) of table to retrieve data from (comma separated)
      key_name - Name of table primary key
      suffix - Suffix for SELECT statement (put WHERE and ORDERED BY here)
      columns - Which columns to return (defaults to all)
      
    Returns:
      A dictionary of Row objects from query
  """
  
  if suffix == None:
    query =  'SELECT ' + columns + ' FROM ' + table_name + ';'
  else:
    query =  'SELECT ' + columns + ' FROM ' + table_name + ' ' + suffix + ';'
  
  #print query
  rowList = [ x for x in table_generator(db, query)]
  table = {}
  for r in rowList:
    table[r.__getattribute__(key_name)] = r
    
  return table

def get_table_with_composite_key( db, table_name, key_names, suffix=None, columns='*'):
  """
    Get table as a dictonary of items keyed by a composite database key
    
    This method only works with a composite key of two fields
    
    Parameters:
      db - Database connection 
      table_name - Name(s) of table to retrieve data from (comma separated)
      key_names - List of composite key fields
      suffix - Suffix for SELECT statement (put WHERE and ORDERED BY here)
      columns - Which columns to return (defaults to all)
      
    Returns:
      A dictionary of Row objects from query
  """
  
  if suffix == None:
    query = 'SELECT ' + columns + ' FROM ' + table_name + ';'
  else:
    query =  'SELECT ' + columns + ' FROM ' + table_name + ' ' + suffix + ';'
  
  rowList = [ x for x in table_generator(db, query)]
  table = {}
  for r in rowList:
    table[(r.__getattribute__(key_names[0]), r.__getattribute__(key_names[1]))] = r
    
  return table
