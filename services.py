import requests
import sett
import json
import time
import re

from datetime import datetime
from databases import DatabaseManager

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

def administrar_chatbot(text,number, messageId, name, timestamp):
    db_manager = DatabaseManager() #instanciamos el objeto
    db_type = 'dynamodb' # previamente configuramos solo mysql, postgresql, dynamodb
    conn = db_manager.connect(db_type)
    text = text.lower() #mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Soporte Bigdateros. ¿Cómo podemos ayudarte hoy?"
        footer = "Equipo Bigdateros"
        options = ["🎫 generar ticket", "🔍 ver estado ticket", "🔄 actualizar ticket"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        list.append(replyReaction)
        list.append(replyButtonData)
    elif "generar ticket" in text:
        textMessage = text_Message(number,"Buena elección! Por favor ingresa su consulta con el siguiente formato: \n\n*'Ingresar Incidente:  <Ingresa breve descripción del problema>*' \n\n Para que nuestros analistas lo revisen 😊")
        list.append(textMessage)
    elif "ingresar incidente" in text:
        description = re.search("ingresar incidente:(.*)", text, re.IGNORECASE).group(1).strip()  # extraemos la descripción del incidente
        created_at = datetime.fromtimestamp(timestamp)  
        ticket_id = db_manager.generate_next_ticket_id(db_type, conn) 

        db_manager.create_ticket(db_type, conn, ticket_id, 'Nuevo', created_at, number, name, description)  
        body = f"Perfecto, se generó el ticket *{ticket_id}*, en breves se estarán comunicando contigo. \n\n¿Deseas realizar otra consulta?"
        footer = "Equipo Bigdateros"
        options = ["✅ Sí", "⛔ No, gracias"]
        replyButtonData = buttonReply_Message(number, 
                                              options, 
                                              body, 
                                              footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "sí" in text:
        body = "¿Cómo podemos ayudarte hoy?"
        footer = "Equipo Bigdateros"
        options = ["🎫 generar ticket", "🔍 ver estado ticket", "🔄 actualizar ticket"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        list.append(replyButtonData)
    elif "ver estado ticket" in text:
        textMessage = text_Message(number,"Buenísima elección! Para verificar su estado ingresa el siguiente formato:\n\n*Buscar TKXXX* \n\n ")
        list.append(textMessage)
    elif  "buscar tk" in text:
        # extraemos el id del ticket
        ticket_id = re.search("buscar (tk.*)", text, re.IGNORECASE).group(1).upper().strip() 
        status = db_manager.get_ticket(db_type, conn,ticket_id)  
        if status == None:
            body = f"Lo siento, no se encontré el ticket *{ticket_id}*.\n\n¿Deseas realizar otra consulta?"
        else :
            body =  f"Perfecto, el ticket *{ticket_id}* se encuentra en {status}. \n\n¿Deseas realizar otra consulta?"
        footer = "Equipo Bigdateros"
        options = ["✅ Sí", "⛔ No, gracias"]
        replyButtonData = buttonReply_Message(number, 
                                              options, 
                                              body, 
                                              footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "actualizar ticket" in text:
        textMessage = text_Message(number,"De acuerdo, Por favor ingresa el siguiente formato:\n\n*Actualizar TKXXX: <Breve descripción a actualizar>*. ")
        list.append(textMessage)
    elif  "actualizar tkt" in text:
        match = re.search("actualizar (tkt.*): (.*)", text, re.IGNORECASE) 
        ticket_id = match.group(1).upper().strip()
        descripcion_actualizada = match.group(2).strip()
        updated = db_manager.update_ticket(db_type, conn, ticket_id, descripcion_actualizada)

        if updated:
            body = f"Perfecto, se actualizón el ticket *{ticket_id}*. \n\n¿Deseas realizar otra consulta?"
        else:
            body = f"Lo siento, no se encontró el ticket *{ticket_id}*.\n\n¿Deseas realizar otra consulta?"
        footer = "Equipo Bigdateros"
        options = ["✅ Sí", "⛔ No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "no, gracias." in text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes más preguntas. ¡Hasta luego! 😊")
        list.append(textMessage)
    else :
        data = text_Message(number,"Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)
    db_manager.disconnect(db_type, conn)

#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s
