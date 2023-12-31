
# Python y MySQL/PostgreSQL/DynamoDB: Chatbot Soporte Tickets

Aprende a usar Python y MySQL/PostgreSQL para construir un chatbot de soporte excepcional. Este video te proporcionará las herramientas y conocimientos que necesitas para empezar tu viaje en el desarrollo de chatbots.
link del video: [https://youtu.be/puYWiZDJnL0](https://youtu.be/vik6wLKjx-Q)

## Descarga el proyecto


```bash
git clone https://github.com/JPierr3/bigdateros-python-mysql-postgres-dynamo/tree/main
```
    
## Funcionalidades

- Integrar python con mysql, postgres y  DynamoDB (se requiere py3.8+)
- Chatbot para soporte de tickets: Métodos CRUD
- Uso de whatsapp cloud api oficial (no terceros)
- Enviar mensaje de texto
- Enviar menus como botones o listas
- Enviar stickers
- Marcar los mensajes como "visto" (doble check azul)
- Reaccionar con emojis los mensajes del usuario
- Enviar documentos pdf



## Para probarlo localmente

1. Dirigete al directorio donde descargaste el proyecto

```bash
  cd mi_proyecto
```
2. Crea un ambiente virtual con la version de python 3.10

```bash
  virtualenv -p 3.10.11 .venv
```
3. Activa el ambiente virtual

```bash
  source .venv/bin/activate
```
4. Instala las dependencias

```bash
  pip install -r requirements.txt
```

5. Corre el aplicativo

```bash
  python app.py
```


## Scripts mencionados en el video

```javascript
Canal de ayuda en slack
https://join.slack.com/t/bigdaterosask/shared_invite/zt-1y000g9fk-mUI~9vRjs8uoLuIjXN5Okg
 
Instalar las liberias de bases de datos
pip install psycopg2-binary pymysql boto3

Crear los objetos de base de datos

#mysql
CREATE DATABASE bigdateros 
CREATE TABLE tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20),
    created_at DATETIME,
    number VARCHAR(50),
    name VARCHAR(50),
    description TEXT
);


# postgres 
CREATE DATABASE bigdateros 
CREATE TABLE tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(20),
    created_at TIMESTAMP,
    number VARCHAR(50),
    name VARCHAR(50),
    description TEXT
);

#dynamodb
se debe configurar primero en el terminarl:
aws configure

luego crear la tabla
aws dynamodb create-table \
    --table-name tickets \
    --attribute-definitions \
        AttributeName=ticket_id,AttributeType=S \
    --key-schema AttributeName=ticket_id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1 

Para postman, solo su numero en "from" y el contenido del texto en "body"
url: http://127.0.0.1:5000/webhook

{
  "object": "whatsapp_business_account",
  "entry": [{
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [{
          "value": {
              "messaging_product": "whatsapp",
              "metadata": {
                  "display_phone_number": "PHONE_NUMBER",
                  "phone_number_id": "PHONE_NUMBER_ID"
              },
              "contacts": [{
                  "profile": {
                    "name": "NAME"
                  },
                  "wa_id": "PHONE_NUMBER"
                }],
              "messages": [{
                  "from": "agrega tu numero",
                  "id": "wamid.ID",
                  "timestamp": "TIMESTAMP",
                  "text": {
                    "body": "hola"
                  },
                  "type": "text"
                }]
          },
          "field": "messages"
        }]
  }]
}
```

