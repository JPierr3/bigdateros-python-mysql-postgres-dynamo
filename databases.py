import psycopg2
import pymysql
import boto3
import uuid

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import NoCredentialsError 

class DatabaseManager:
    def __init__(self):
        self.databases = [
            {'type': 'postgresql', 'connection_str': 'dbname=bigdateros user=postgres password=bigdateros2023 host=localhost port=5432'},
            {'type': 'mysql', 'connection_str': {'host':'localhost', 'user':'root', 'password':'bigdateros2023', 'db':'bigdateros', 'charset':'utf8mb4'}},
            {'type': 'dynamodb', 'connection_str': {'region_name':'us-east-1', 'aws_access_key_id':'AKIAYKD2PK23BETDJ6GZ', 'aws_secret_access_key':'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'}},
        ]

    def connect(self, db_type):
        db = next((db for db in self.databases if db['type'] == db_type), None)
        if db is None:
            print(f"No database of type {db_type} found")
            return None

        if db_type == 'postgresql':
            print('postgresql')
            return psycopg2.connect(db['connection_str'])
        elif db_type == 'mysql':
            return pymysql.connect(**db['connection_str'])
        elif db_type == 'dynamodb':
            return boto3.resource('dynamodb', 
            region_name=db['connection_str']['region_name'],
                                  aws_access_key_id=db['connection_str']['aws_access_key_id'],
                                  aws_secret_access_key=db['connection_str']['aws_secret_access_key'])
        

    def disconnect(self, db_type, conn):
        print('disconnect')
        if db_type == 'postgresql' or db_type == 'mysql' or db_type == 'mssql':
            conn.close()
        else:
            pass
    
    def create_ticket(self, db_type, conn, ticket_id, status, created_at, number, name, description):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"INSERT INTO tickets (ticket_id, status, created_at, number, name, description) VALUES ('{ticket_id}', '{status}', '{created_at}', '{number}', '{name}', '{description}')"
            cur.execute(query)
            conn.commit()
            cur.close()
        elif db_type == 'dynamodb':
            table = conn.Table('tickets')
            item = {
                'ticket_id': ticket_id,
                'status': status,
                'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S") ,
                'number': number,
                'name': name,
                'description': description
            }
            table.put_item(Item=item)
    
    def get_ticket(self, db_type, conn, ticket_id):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"SELECT status FROM tickets WHERE ticket_id = '{ticket_id}'"
            cur.execute(query)
            result = cur.fetchone()
            cur.close()
            if result is not None:  # validamos en caso no exista el ticket
                return result[0]
            else:
                print(f"No se encontró ningún ticket con ID {ticket_id} en {db_type}.")
                return None
            
        elif db_type == 'dynamodb':
            table = conn.Table('tickets')
            response = table.get_item(Key={'ticket_id': ticket_id})
            # Revisa si existe el ticket y retorna el status
            if 'Item' in response:
                return response['Item'].get('status', None)
            else:
                print(f"No se encontró ningún ticket con ID {ticket_id} en DynamoDB.")
                return None
    def update_ticket(self, db_type, conn, ticket_id, description):
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = f"UPDATE tickets SET description = '{description}' WHERE ticket_id = '{ticket_id}'"
            cur.execute(query)
            conn.commit()
            updated_rows = cur.rowcount
            cur.close()
            return updated_rows > 0  # Devuelve True si se actualizó al menos una fila
        elif db_type == 'dynamodb':
            table = conn.Table('tickets')
            response = table.update_item(
                Key={'ticket_id': ticket_id},
                UpdateExpression="set #st=:s",
                ExpressionAttributeValues={':s': description},
                ExpressionAttributeNames={"#st": "description"},
                ReturnValues='UPDATED_OLD'
            )
            return 'Attributes' in response  # Devuelve True si se encontró y actualizó el ticket
    def generate_next_ticket_id(self, db_type, conn):
        last_ticket_id=''
        if db_type == 'postgresql' or db_type == 'mysql' :
            cur = conn.cursor()
            query = "SELECT ticket_id FROM tickets ORDER BY ticket_id DESC LIMIT 1"
            cur.execute(query)
            result = cur.fetchone()
            last_ticket_id = result[0] if result else "TKT000"  
            cur.close()
        elif db_type == 'dynamodb':
            table = conn.Table('tickets')
            response = table.scan(
                ProjectionExpression="ticket_id"
            )
            ticket_ids = [item['ticket_id'] for item in response['Items']]
            last_ticket_id = max(ticket_ids) if ticket_ids else "TKT000"
        
        last_number = int(last_ticket_id[3:])
        next_number = last_number + 1
        next_ticket_id = f"TKT{str(next_number).zfill(3)}"
        return next_ticket_id