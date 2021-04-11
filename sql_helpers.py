import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except IOError as e:
        print(e)
    return conn

def update_job_description(conn, job):
    """
    update description
    :param conn:
    :job 
        :description
        :id
   
    """
    sql = ''' UPDATE jobs SET full_description = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, job)
    conn.commit()

def update_outcode(conn,table,job):
    """
    update description
    :param conn:
    :table:
    :job 
        :outcode
        :id
    """
    sql = ''' UPDATE ''' + table + ''' SET outcode = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, job)
    conn.commit()

def update_admin_district(conn,table,job):
    """
    update description
    :param conn:
    :table:
    :job 
        :admin_district
        :id
    """
    sql = ''' UPDATE ''' + table + ''' SET admin_district = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, job)
    conn.commit()