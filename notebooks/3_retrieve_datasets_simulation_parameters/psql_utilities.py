import psycopg2 as pg
from configparser import ConfigParser

def load_config(config_file='database/database.ini', section='postgresql'):

    ### read config file
    parser = ConfigParser()
    parser.read(config_file)

    ### parse config file    
    if(parser.has_section(section)):
        config_dict = dict(parser[section])
    else:
        raise Exception(f"File {config_file} has no section {section}")

    ### create connection string
    config_dict['db_uri'] = f'postgresql://{config_dict['db_user']}:{config_dict['db_password']}@{config_dict['db_host']}:{config_dict['db_port']}/{config_dict['db_name']}'

    return config_dict

def connect(config):
    """ Function to connect to the PostgreSQL database server """
    
    try:
        conn = pg.connect(**config)
    except (pg.DatabaseError, Exception) as error:
        print(error)
    
    return conn
        
def run_query(db_connect,query_str):
    """ Run a query (query_str) over a database """
    ### define a cursor
    cur = db_connect.cursor()
    ### execute query 
    try:
        cur.execute(query_str)
        print("The number of rows: ", cur.rowcount)
        query_res = cur.fetchall()
    except:
        print("WARNING Something wrong with the query")
        db_connect.rollback()
        query_res = []
    ### close cursor
    cur.close()
    return query_res


### note number of placeholders '%s' must coincide with the number of (column) values to insert
def insert_many_rows(sqlquery_str,list_values,connector):
    """ Insert multiple vendors into a table  """

    #sql = "INSERT INTO dataset (id_ds, name, type, fk_exp_id, spatial_coverage) VALUES(%s,%s,%s,%s,%s) RETURNING *"
    sql = sqlquery_str
    #config = load_config()
    try:
        with connector.cursor() as cur:
            # execute the INSERT statement
            cur.executemany(sql, list_values)
        # commit the changes to the database
        connector.commit()
        print("Rows Inserted")
        cur.close()
    except (Exception, pg.DatabaseError) as error:
        print("ERROR: ", error) 