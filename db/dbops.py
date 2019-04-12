import pymysql as pymy

class DBMan:

    def __init__(self, db_addr, db_port,db_user, db_pass, db_name):
        self.db_addr = db_addr
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self.db_port = db_port

    def connect(self):
        '''
        Creates a connection to the db using credentials stored in __init__
        Returns Connection and Cursor objects
        Returns [None, None] if there is an error
        '''
        try:
            conn = pymy.connect(self.db_addr,self.db_port, self.db_user, self.db_pass, self.db_name)
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            print('Exception in connecting to DB:', e)
            return None, None
            raise

    def fetch(self, sql, rows=None):
        '''
        Returns all rows affected by your query
        Returns None if there is an error
        '''
        try:
            conn, cursor = self.connect()
            if conn:
                if rows:
                    cursor.execute(sql, rows)
                    result = cursor.fetchall()
                else:
                    cursor.execute(sql)
                    result = cursor.fetchall()
                return result
            else:
                return None

        except Exception as e:
            print('Exception in fetching rows:', e)
            raise

        finally:
            if conn:
                self.close(conn)

    def insert(self, sql, rows):
        '''
        Inserts rows and returns that last inserted row id
        Returns the first inserted row id if multiple rows are inserted
        Returns None if there is an error
        '''
        try:
            conn, cursor = self.connect()
            if conn:
                cursor.executemany(sql, rows)
                conn.commit()
                return cursor.lastrowid
            else:
                return None

        except Exception as e:
            if conn:
                conn.rollback()
            print('Exception in inserting rows:', e)
            print(rows)
            raise

        finally:
            if conn:
                self.close(conn)

    def update(self, sql, rows):
        '''
        Updates rows and returns number of rows affected by the query
        Returns None if there is an error
        '''
        try:
            conn, cursor = self.connect()
            if conn:
                num_rows_affected = cursor.executemany(sql, rows)
                conn.commit()
                return num_rows_affected
            else:
                return None

        except Exception as e:
            if conn:
                conn.rollback()
            print('Exception in updating rows:', e)
            print(rows)
            raise

        finally:
            if conn:
                self.close(conn)

    def clearTable(self, table):
        '''
        Clears all rows in a table without deleting the table itself
        Returns True if all goes well
        Returns None if there is an error
        '''
        try:
            conn, cursor = self.connect()
            if conn:
                sql = "DELETE FROM "+table
                cursor.execute(sql)
                conn.commit()
                return True
            else:
                return None

        except Exception as e:
            if conn:
                conn.rollback()
            print('Exception in clearing table:', e)
            raise

        finally:
            if conn:
                self.close(conn)

    def close(self, conn):
        '''Closes a connection'''
        try:
            conn.close()
        except Exception as e:
            print('Exception in closing connection:', e)
            raise
