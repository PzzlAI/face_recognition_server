from typing import Optional, List
from fastapi import FastAPI, File, UploadFile,Form, Depends
import pymongo
from pymongo import MongoClient
import uvicorn
from pydantic import BaseModel
import shutil
import os
from bson.json_util import dumps
from datetime import datetime
from pytz import timezone
import utils.models as models
import utils.auxiliary_functions as auxiliary_functions
import requests

app = FastAPI(dependencies=[Depends(auxiliary_functions.get_api_key)])
# todo: posiblemente refactorizar los procesos de remove y restore, pueden ser juntados en una sola ruta respectivamente.
#       solo que habra que tomar en cuenta la autenticacion en el proceso de remove/restore de admins, ya que solo el super admin
#       debe ser capaz de hacerlo.

client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")

# todo: hay que setear para que el omega administrador sea el que cree las bases de datos, y hay que definir como va a ser ese proceso.
def get_db(company_code):               
    dbnames = client.list_database_names()
    if company_code in dbnames:   
        db = client[company_code]
        return db
    else:
        return False

# por ahora se va a utilizar esta funcion para hacer bases de datos de prueba, pero se va a tener que refactorizar para que se haga a traves del omega administrador.
def create_db(company_code):
    print(company_code)
    db = client[company_code]
    return db

def validate_unique(username: str):
    dbnames = client.list_database_names()
    administrator = { "username": username}
    for company_code in dbnames:
        db = client[company_code]
        sa_collection = db["super_administrador"]
        a_collection = db["administradores"]
        super_admin = sa_collection.find_one(administrator)
        admin = a_collection.find_one(administrator)
        if super_admin or admin:
            return False
    return True

@app.get('/')
def ping_server():
    return "Face database api is running!!!"

# por ahora esta funcion va a ser usada sin tomar en cuenta el caching ni hahsing. y hay que ver si terminamos usando el mismo endpoint para ambas cosas o si seran separadas.
@app.post('/admin_login')
async def admin_login(admin_credentials: models.admin_credentials):
    # revisar si esta en la base de datos
    # primero buscar username, y luego comparas contraseña
    print(admin_credentials)

    dbnames = client.list_database_names()
    print(dbnames)
    administrator = { "username": admin_credentials.username}

    for company_code in dbnames:
        print(company_code)
        db = client[company_code]
        collection = db["administradores"]

        x = collection.find_one(administrator)

        if not x:
            continue

        if x["password"] == admin_credentials.password:
            return{"access": True, "code": 5001, "status": "found, password correct", "name": x["nombre_completo"], "company_code": x["company_code"], "employee_code": x["employee_code"]}

        if x["password"] != admin_credentials.password:
            return{"access": False, "code": 6001, "status": "found, password incorrect", "name": x["nombre_completo"]}
    if not x:
        return{"access": False, "code": 1004, "status": "not found"}


@app.post('/admin_update_images')
async def admin_save_images(company_code: str = Form(...), 
                            employee_code: str = Form(...),
                            nombre_completo: str =Form(...),
                            files: List[UploadFile] = File(...) ):
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return {"code": 1001, "status": "Compañia no existe"}

        collection = db["administradores"]
        directory = "./db/" + company_code + "/" + employee_code
        directory_tmp = directory + "_old"
        
        # rename directory
        os.rename(directory, directory_tmp)

        os.mkdir(directory)

        # loop through image list and copy to folder, then add path to list.
        image_paths = []
        for file in files:
            image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
            with open(image_path,'wb') as image:
                shutil.copyfileobj(file.file, image)
                image_paths.append(image_path)
        
        # validate fotos
        req = requests.post('http://app_df:8000/validar_fotos', data = {'company_code': company_code, "employee_code": employee_code}, headers = {os.environ['API_KEY_NAME']: os.environ['API_KEY']})
        resp = req.json()
        if not resp["created"]:
            # the endpoint already deletes the fotos if face detection error occurs
            # rename old directory to default name
            print("trying to rename directory")
            os.rename(directory_tmp, directory)
            return{"created": False, "code": 3001, "status": "no se encuentra cara en la foto"}

        # delete old image directory
        shutil.rmtree(directory_tmp)
        
        # find employee and modify relevant data.
        employee = { "employee_code": employee_code }
        new_path = { "$set": { "image_paths": image_paths , "updated": datetime.now(timezone('America/Panama')), "nombre_completo": nombre_completo} }
        collection.update_one(employee, new_path)


        return{"created": True, "code": 4002, "status": "representations created successfully"}

    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()


    
# esta ruta solo se va a usar para pruebas, posteriormente se va a formalizar un proceso de creacion de base de datos utilizando el concepto del omega administrador.
# por ahora este proceso tambien requiere la creacion del super administrador, pero esto es sujeto a cambio dependiendo de las decisiones de diseño futuras.

# ahora que lo pienso hay que enforzar que no se puede crear super usuarios con el mismo nombre de usuario.
@app.post('/create_company', status_code = 201)
async def create_company(admin_schema: models.admin_schema):
    db=""
    try:
        db = get_db(admin_schema.company_code)
        if db:
            return{"code": 2001, "status": "Compañia ya existe"}

        if not validate_unique(admin_schema.username):
            return{"code": 2004, "status": "usuario ya existe"}

        if not db:
            os.mkdir("./db/" + admin_schema.company_code)
            db = create_db(admin_schema.company_code)
            collection = db["super_administrador"]


            tz = timezone('America/Panama')
            current_date = datetime.now(tz)

            super_admin = {"company_code": admin_schema.company_code, 
                            "employee_code": admin_schema.employee_code, 
                            "username": admin_schema.username, 
                            "password": admin_schema.password, 
                            "nombre_completo": admin_schema.nombre_completo, 
                            "serial_de_dispositivo": "", 
                            "created": current_date, 
                            "updated": current_date }

            collection.insert_one(super_admin)
            return{"code": 7001, "status": "creado exitosamente"}


    except Exception as e:
        print(e)
        return "unable to create database for company"
    finally:
        if type(db)==MongoClient:
            db.close()


# determinar si este proceso se hace con imagen inicial o sin image, por ahora esta sin imagen.
# tomar en cuenta que en este punto no se sabe el serial del dispositivo del colaborador,
# asi que se tendra que updatear ese field cuando el colaborador haga su primera marcacion
# con la aplicacion.

# no se puede usar pydantic models junto con upload file. por lo cual hay que hacerlo de esta forma,
# este deberia ser el unico que se debe hacer de esta forma, en terminos del cliente no hay diferencia
# en el formato de la peticion.
@app.post("/create_collaborator")
async def create_collaborator(company_code: str = Form(...), 
                              employee_code: str = Form(...),
                              nombre_completo: str =Form(...),
                              files: List[UploadFile] = File(...) ):

    db=""
    try:
        db = get_db(company_code)

        if not db:
            return {"code": 1001, 'status': "company doesnt exist"}
        
        directory = "./db/" + company_code + "/" + employee_code

        # todo: error handling de cuando ya existe el colaborador. por ahora voy a poner esto, pero hay que ver que es apropiado hacer.
        if os.path.isdir(directory):
            return {"code": 2001, 'status': 'collaborator already exists'}
        
        collaborators = db["colaboradores"]

        os.mkdir(directory)
        
        image_paths = []
        for file in files:
            image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
            with open(image_path,'wb') as image:
                shutil.copyfileobj(file.file, image)
                image_paths.append(image_path)
                
        # validate fotos
        req = requests.post('http://app_df:8000/validar_fotos', data = {'company_code': company_code, "employee_code": employee_code}, headers = {os.environ['API_KEY_NAME']: os.environ['API_KEY']})
        resp = req.json()
        if not resp["created"]:
            return{"created": False, "code": 3001, "status": "no se encuentra cara en una de las fotos"}

        tz = timezone('America/Panama')
        current_date = datetime.now(tz)
        collaborator = {"company_code": company_code, 
                        "employee_code": employee_code,
                        "nombre_completo": nombre_completo,
                        "image_paths": image_paths,
                        "serial_de_dispositivo": "",
                        "created": current_date, 
                        "updated": current_date}

        collaborators.insert_one(collaborator)
        x = collaborators.find()

        # crear coleccion para guardar marcaciones del colaborador. 
        marcador = {"company_code": company_code, "employee_code": employee_code, "marcaciones": []}
        marcaciones = db["marcaciones"]
        marcaciones.insert_one(marcador)

        return{"created": True, "code": 4002, "status": "representations created successfully"}
    except Exception as e:
        print(e)
        return("error del servidor")
    finally:
        if type(db)==MongoClient:
            db.close()

# todo: refactorizar para aclarar/robustizar el proceso de autenticacion de administrador, ya sea con hashing o viendo si se usa la misma imagen de la persona, sin embargo, esto tendria implicaciones en
# la estructura general del prototipo. 
# tomar en cuenta que se hashea antes de mandar al servidor, osea en el app/browser.
@app.post("/create_admin")
async def create_admin(admin_schema: models.admin_schema):
    db=""
    try:
        db = get_db(admin_schema.company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        if not validate_unique(admin_schema.username):
            return{"code": 2004, "status": "usuario ya existe"}

        collection = db["administradores"]
        x = collection.find_one({"employee_code": admin_schema.employee_code})
        if x:
            return{"code": 2003, "status": "Administrador ya existe"}


        # todo: revisar si el username ya existe
        
        tz = timezone('America/Panama')
        current_date = datetime.now(tz)
        admin = {"company_code": admin_schema.company_code, 
                 "employee_code": admin_schema.employee_code, 
                 "username": admin_schema.username, 
                 "password": admin_schema.password, 
                 "nombre_completo": admin_schema.nombre_completo,
                 "image_paths": [],
                 "serial_de_dispositivo": "", 
                 "created": current_date, 
                 "updated": current_date }

        print(admin)
        collection.insert_one(admin)
        os.mkdir("./db/" + admin_schema.company_code + "/" + admin_schema.employee_code)

        x = collection.find()
        return{"code": 7001, "status": "creado exitosamente"}
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# todo: ver si se necesita el update de admin, ya sea por updatear contraseña u otra cosa.

@app.put("/update_collaborator")
async def update_collaborator(company_code: str = Form(...), 
                              employee_code: str = Form(...),
                              nombre_completo: str =Form(...),
                              files: List[UploadFile] = File(...) ):
    db=""
    try:
        db = get_db(company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collection = db["colaboradores"]
        directory = "./db/" + company_code + "/" + employee_code
        directory_tmp = directory + "_old"
        
        # rename directory
        os.rename(directory, directory_tmp)

        os.mkdir(directory)

        # loop through image list and copy to folder, then add path to list.
        image_paths = []
        for file in files:
            image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
            with open(image_path,'wb') as image:
                shutil.copyfileobj(file.file, image)
                image_paths.append(image_path)
        
        # validate fotos
        req = requests.post('http://app_df:8000/validar_fotos', data = {'company_code': company_code, "employee_code": employee_code}, headers = {os.environ['API_KEY_NAME']: os.environ['API_KEY']})
        resp = req.json()
        if not resp["created"]:
            # the endpoint already deletes the fotos if face detection error occurs
            # rename old directory to default name
            print("trying to rename directory")
            os.rename(directory_tmp, directory)
            return{"created": False, "code": 3001, "status": "no se encontro cara en una de las fotos"}

        # delete old image directory
        shutil.rmtree(directory_tmp)
        
        # find employee and modify relevant data.
        employee = { "employee_code": employee_code }
        new_path = { "$set": { "image_paths": image_paths , "updated": datetime.now(timezone('America/Panama')), "nombre_completo": nombre_completo} }
        collection.update_one(employee, new_path)


        return{"created": True, "code": 4002, "status": "representations created successfully"}

    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# retornar colaborador, por el momento esta escrito para utilizar durante desarrollo, pero se refactorizara para uso en produccion.
# cuando se refactorize tendria que ser el mismo endpoint para buscar colaborador o administrador.
# este enpoint deberia ser get, pero no se puede mandar info por el body con get asi que por el momento lo voy a dejar como post.
@app.post("/read_collaborator",  status_code=200)
async def read(employee_code_model: models.employee_code_model):
    db=""
    try:
        db = get_db(employee_code_model.company_code)
        if not db:
            return{"code": 1001, "status": "Compañia no existe"}
        
        collection = db["colaboradores"]

        employee = { "employee_code": employee_code_model.employee_code}
        employee_data = collection.find_one(employee)

        if not employee_data:
            collection = db["administradores"]
            employee_data = collection.find_one(employee)
        
        if not employee_data:
            return{"code": 1005, "status": "empleado no existe"}

        image_list = [path for path in employee_data['image_paths']]
        print(image_list)
        
        return auxiliary_functions.zipfiles(image_list)

    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()


# retornar lista completa de colaboradores, por el momento esta escrito para ser utilizado durante desarrollo, pero se refactorizara para uso en produccion.
# este enpoint deberia ser get, pero no se puede mandar info por el body con get asi que por el momento lo voy a dejar como post.
@app.post("/read_collaborators") # response_model = models.collaborator_list_return
async def read(company_code_model: models.company_code_model):
    db=""
    try:
        db = get_db(company_code_model.company_code)
        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collaborators = db["colaboradores"].find()

        parsed_list = []

        for collaborator in collaborators:

            colab = {
               "employee_code": collaborator['employee_code'],
               "nombre_completo": collaborator["nombre_completo"] 
            }
            parsed_list.append(colab)

        print(parsed_list)

        return(parsed_list)

    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

@app.post("/read_administrators") # response_model = models.collaborator_list_return
async def read(company_code_model: models.company_code_model):
    db=""
    try:
        db = get_db(company_code_model.company_code)
        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        administrators = db["administradores"].find()

        parsed_list = []

        for administrator in administrators:
            admin = {
                    "employee_code": administrator['employee_code'],
                    "nombre_completo": administrator["nombre_completo"]
                    }
            parsed_list.append(admin)

        print(parsed_list)

        return(parsed_list)

    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

# mover colaboradores a coleccion y directorio separado, aka, papelera de reciclaje.
@app.delete("/remove_collaborator", status_code=200)
async def remove_collaborator(employee_code_model: models.employee_code_model):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(employee_code_model.company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = collection.find_one(employee)
        # insertar en nueva coleccion
        deleted_collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.now(timezone('America/Panama'))} }
        deleted_collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        collection.delete_one(employee)

        # mover imagenes a nueva carpeta asumiendo que el directorio nuevo existe. ./db/(company_code)_deleted/(employee_code)
        shutil.move("./db/"+ employee_code_model.company_code + "/" + employee_code_model.employee_code, "./db/"+ employee_code_model.company_code + "_deleted/" + employee_code_model.employee_code)
        
        return{"code": 7002, "status": "borrado exitosamente"}
    except Exception as e:
        print(e)
        return{"code": 8002, "status": "error al borrar"}
    finally:
        if type(db)==MongoClient:
            db.close()

# mover administrador a coleccion separada.
# todo: refactorizar para usar la misma ruta de remove para ambos administradores y colaboradores, ya sea con parametros de rutas. /remove_{variable}
@app.delete("/remove_admin", status_code=200)
async def remove_admin(employee_code_model: models.employee_code_model):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(employee_code_model.company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collection = db["administradores"]
        deleted_collection = db["administradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = collection.find_one(employee)
        # insertar en nueva coleccion
        deleted_collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.now(timezone('America/Panama'))} }
        deleted_collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        collection.delete_one(employee)
        return{"code": 7002, "status": "se removio exitosamente"}

    except Exception as e:
        return{"code": 8002, "status": "no se pudo remover"}
    finally:
        if type(db)==MongoClient:
            db.close()

# eliminar colaborador completamente.
@app.delete("/delete_collaborator", status_code=200)
async def delete_collaborator(employee_code_model: models.employee_code_model):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(employee_code_model.company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collaborators = db["colaboradores"]
        marcaciones = db["marcaciones"]

        employee = { "employee_code": employee_code_model.employee_code }
        
        collaborators.delete_one(employee)
        marcaciones.delete_one(employee)

        shutil.rmtree("./db/"+ employee_code_model.company_code + "/" + employee_code_model.employee_code)

        return{"code": 7002, "status": "borrado exitosamente"}

    except Exception as e:
        print(e)
        return{"code": 8002, "status": "error al borrar"}
    finally:
        if type(db)==MongoClient:
            db.close()

# eliminar administrador completamente.
@app.delete("/delete_admin", status_code=200)
async def delete_admin(employee_code_model: models.employee_code_model):
    # revisar este codigo para asegurarme de que no se desincronizen los volumenes en el caso de que un proceso funcione y el otro se trabe.
    db=""
    try:
        db = get_db(employee_code_model.company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collection = db["administradores"]

        employee = { "employee_code": employee_code_model.employee_code }
        
        collection.delete_one(employee)
        directory = "./db/"+ employee_code_model.company_code + "/" + employee_code_model.employee_code
        if os.path.isdir(directory):
            shutil.rmtree(directory)

        return{"code": 7002, "status": "borrado exitosamente"}
    except Exception as e:
        print(e)
        return{"code": 8002, "status": "error al borrar"}
    finally:
        if type(db)==MongoClient:
            db.close()


# todo: hacer ruta para restore, en la que restauramos un colaborador que fue borrado. y posiblemente usar una sola ruta para administradores tambien.
@app.put("/restore_collaborator", status_code = 200)
async def restore_collaborator(employee_code_model: models.employee_code_model):
    db=""
    try:
        db = get_db(employee_code_model.company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = deleted_collection.find_one(employee)
        # insertar en nueva coleccion
        collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.now(timezone('America/Panama'))} }
        collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        deleted_collection.delete_one(employee)


        # mover imagenes a nueva carpeta asumiendo que el directorio nuevo existe. ./db/(company_code)_deleted/(employee_code)
        shutil.move("./db/"+ employee_code_model.company_code + "_deleted/" + employee_code_model.employee_code, "./db/"+ employee_code_model.company_code + "/" + employee_code_model.employee_code)

        return{"code": 7001, "status": "restaurado exitosamente"}

    except Exception as e:
        print(e)
        return{"code": 8001, "status": "error al tratar de restaurar"}
    finally:
        if type(db)==MongoClient:
            db.close()

@app.put("/restore_admin", status_code = 200)
async def restore_admin(employee_code_model: models.employee_code_model):
    db=""
    try:
        db = get_db(employee_code_model.company_code)

        if not db:
            return{"code": 1001, "status": "Compañia no existe"}

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = deleted_collection.find_one(employee)
        # insertar en nueva coleccion
        collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.now(timezone('America/Panama'))} }
        collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        deleted_collection.delete_one(employee)

        return{"code": 7001, "status": "restaurado exitosamente"}
    except Exception as e:
        print(e)
        return{"code": 8001, "status": "error al tratar de restaurar"}
    finally:
        if type(db)==MongoClient:
            db.close()


# ---------------------------------------------------------------------#
# solo para propositos de prueba
@app.post("/read_employees")
async def read_employees(company_code: str):
    db=""
    try:
        db = get_db(company_code)
        if not db:
            return "company doesnt exist"

        collaborators = db["colaboradores"].find()
        administrators = db["administradores"].find()
        super_admin = db["super_administrador"].find()

        return {
            "colaboradores": dumps(collaborators),
            "administradores": dumps(administrators),
            "super_administrador":dumps(super_admin)
        }


    except Exception as e:
        return(e)
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()



@app.delete("/delete_databases", status_code=200)
async def delete_all():
    db=""
    try:
        dbnames = client.list_database_names()

        if dbnames:
            for database in dbnames:
                if not (database == "admin" or database == "local" or database == "config"):
                    client.drop_database(database)

        for f in os.listdir("./db/"):
            shutil.rmtree("./db/" + f)
        return "se borraron exitosamente"
    except OSError as e:
        return("Error: %s - %s." % (e.filename, e.strerror))
    finally:
        if type(db)==MongoClient:
            db.close()

@app.get("/list_databases")
async def list_databases():
    db=""
    try:

        dbnames = client.list_database_names()
        print(dbnames)
        return(dbnames)
    except Exception as e:
        return(e)
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

if __name__ == '__main__':
    print("running on port 5000")
    uvicorn.run(app, host = '0.0.0.0', port = 5000)