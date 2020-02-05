from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import sqlite3
import logging
import datetime
import json

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

parser.add_argument('user_id', type=str)
parser.add_argument('guid', type=str)
parser.add_argument('location', type=str)

def create_connection(db_file):        
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.DatabaseError as e:
        print(e)
    return conn
    
class DeviceRegistration(Resource):
    
    dbconn = None

    def check_user_id(self, user_id):
        cur = self.dbconn.cursor()
        sql_statement = 'select count(*) from tbl_users where user_id=\'%s\' and status=1;' % (user_id)
        logging.debug(sql_statement)
        ret = cur.execute(sql_statement).fetchone()[0]
        if ret == 0:
            return False
        else:
            return True

    def create_device(self, args):
        '''
        rejestrowanie urządzenia w bazie
        @device - parametr z danymi POST (user_id, guid, location)
        '''
        #sprawdzenie czy jest utworzone konto do rejestracji i czy jest aktywne
        if self.check_user_id(args['user_id']):
            sql_statement = ''' INSERT INTO tbl_devices(user_id, guid, location) 
                                VALUES (?,?,?);'''  
            cur = self.dbconn.cursor()
            logging.debug(sql_statement)
            try:
                device = (args['user_id'],args['guid'],args['location'])
                cur.execute(sql_statement,device)
                self.dbconn.commit()
                return True, 'Device has been registered'
            except sqlite3.IntegrityError:
                return False, 'Device already registered'
            else:
                return False, 'Error during device registration'
        else:
            return False, 'User not registered or not active'
        
    def post(self):
        logging.debug('Receiving POST /device request')
        args = parser.parse_args()
        self.dbconn = create_connection('infocms.db')
        ret, message = self.create_device(args)
        self.dbconn.close()
        if ret == True:
            logging.debug({'ok':message})
            return {'ok':message}
        else:
            logging.debug({'error':message})
            return {'error':message}
        
    
api.add_resource(DeviceRegistration, '/device')

if __name__ == '__main__':
    logging.basicConfig(filename='infocms.log',level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.run(debug=True)