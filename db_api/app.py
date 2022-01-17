from typing import Optional, List
from fastapi import FastAPI, File, UploadFile,Form
import pymongo
from pymongo import MongoClient
import uvicorn
from pydantic import BaseModel
import shutil
import os
from bson.json_util import dumps
import datetime
import utils.models as models
import utils.auxiliary_functions as auxiliary_functions

app = FastAPI()
# todo: posiblemente refactorizar los procesos de remove y restore, pueden ser juntados en una sola ruta respectivamente.
#       solo que habra que tomar en cuenta la autenticacion en el proceso de remove/restore de admins, ya que solo el super admin
#       debe ser capaz de hacerlo.



# todo: hay que setear para que el omega administrador sea el que cree las bases de datos, y hay que definir como va a ser ese proceso.
def get_db(company_code):
    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
                        
    dbnames = client.list_database_names()
    if company_code in dbnames:   
        db = client[company_code]
        return db
    else:
        return False

# por ahora se va a utilizar esta funcion para hacer bases de datos de prueba, pero se va a tener que refactorizar para que se haga a traves del omega administrador.
def create_db(company_code):
    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")
    print(company_code)
    db = client[company_code]
    return db



@app.get('/')
def ping_server():
    return "Face database api is running!!!"

# por ahora esta funcion va a ser usada sin tomar en cuenta el caching ni hahsing. y hay que ver si terminamos usando el mismo endpoint para ambas cosas o si seran separadas.
@app.post('/admin_login')
async def admin_login(admin_credentials: models.admin_credentials):
    # revisar si esta en la base de datos
    # primero buscar username, y luego comparas contraseña
    print(admin_credentials)

    client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")

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
            return{"access": True, "status": "found, password correct", "name": x["nombre_completo"], "company_code": x["company_code"]}

        if x["password"] != admin_credentials.password:
            return{"access": False, "status": "found, password incorrect", "name": x["nombre_completo"]}
    if not x:
        return{"access": False, "status": "not found"}



# esta ruta solo se va a usar para pruebas, posteriormente se va a formalizar un proceso de creacion de base de datos utilizando el concepto del omega administrador.
# por ahora este proceso tambien requiere la creacion del super administrador, pero esto es sujeto a cambio dependiendo de las decisiones de diseño futuras.

# ahora que lo pienso hay que enforzar que no se puede crear super usuarios con el mismo nombre de usuario.
@app.post('/create_company', status_code = 201)
async def create_company(admin_schema: models.admin_schema):
    db=""
    try:
        db = get_db(admin_schema.company_code)
        if not db:
            os.mkdir("./db/" + admin_schema.company_code)
            db = create_db(admin_schema.company_code)
            collection = db["super_administrador"]
            current_date = datetime.datetime.now()
            super_admin = {"company_code": admin_schema.company_code, 
                            "employee_code": admin_schema.employee_code, 
                            "username": admin_schema.username, 
                            "password": admin_schema.password, 
                            "nombre_completo": admin_schema.nombre_completo, 
                            "serial_de_dispositivo": "", 
                            "created": current_date, 
                            "updated": current_date }

            collection.insert_one(super_admin)
            return ("company " + admin_schema.company_code + " created succesfully with " + admin_schema.employee_code+ " as administrator")


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
            return {'status': "company doesnt exist"}
        
        directory = "./db/" + company_code + "/" + employee_code

        # todo: error handling de cuando ya existe el colaborador. por ahora voy a poner esto, pero hay que ver que es apropiado hacer.
        if os.path.isdir(directory):
            return {'status': 'collaborator already exists'}
        
        collaborators = db["colaboradores"]

        os.mkdir(directory)
        
        image_paths = []
        for file in files:
            image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
            with open(image_path,'wb') as image:
                shutil.copyfileobj(file.file, image)
                image_paths.append(image_path)
                

        current_date = datetime.datetime.now()
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

        return(dumps(x))
    except Exception as e:
        print(e)
        return(dumps(e))
    finally:
        if type(db)==MongoClient:
            db.close()

# todo: refactorizar para aclarar/robustizar el proceso de autenticacion de administrador, ya sea con hashing o viendo si se usa la misma imagen de la persona, sin embargo, esto tendria implicaciones en
# la estructura general del prototipo. 
# tomar en cuenta que se hashea antes de mandar al servidor, osea en el app/browser.
@app.post("/create_admin", status_code = 201)
async def create_admin(admin_schema: models.admin_schema):
    db=""
    try:
        db = get_db(admin_schema.company_code)

        if not db:
            return "company doesnt exist"
        
        collection = db["administradores"]
        
        current_date = datetime.datetime.now()
        admin = {"company_code": admin_schema.company_code, 
                 "employee_code": admin_schema.employee_code, 
                 "username": admin_schema.username, 
                 "password": admin_schema.password, 
                 "nombre_completo": admin_schema.nombre_completo, 
                 "serial_de_dispositivo": "", 
                 "created": current_date, 
                 "updated": current_date }

        print(admin)
        collection.insert_one(admin)
        x = collection.find()
        return(dumps(x))
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
            return "company doesnt exist"

        collection = db["colaboradores"]
        directory = "./db/" + company_code + "/" + employee_code
        
        # first delete all files. 
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))

        # loop through image list and copy to folder, then add path to list.
        image_paths = []
        for file in files:
            image_path = directory + "/" + employee_code + "_" + str(len(os.listdir(directory))) + ".jpg"
            with open(image_path,'wb') as image:
                shutil.copyfileobj(file.file, image)
                image_paths.append(image_path)

        # find employee and modify relevant data.
        employee = { "employee_code": employee_code }
        new_path = { "$set": { "image_paths": image_paths , "updated": datetime.datetime.now(), "nombre_completo": nombre_completo} }
        collection.update_one(employee, new_path)

        # for now we return the mongodb document just for developement purposes.
        x = collection.find()
        return(dumps(x))

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
            return "company doesnt exist"
        
        collection = db["colaboradores"]

        employee = { "employee_code": employee_code_model.employee_code}
        employee_data = collection.find_one(employee)

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
            return "company doesnt exist"

        collaborators = db["colaboradores"].find()

        parsed_list = {}

        for collaborator in collaborators:
            parsed_list[collaborator['employee_code']] = collaborator["nombre_completo"]

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
            return "company doesnt exist"

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = collection.find_one(employee)
        # insertar en nueva coleccion
        deleted_collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        deleted_collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        collection.delete_one(employee)

        try:
            # mover imagenes a nueva carpeta asumiendo que el directorio nuevo existe. ./db/(company_code)_deleted/(employee_code)
            shutil.move("./db/"+ employee_code_model.company_code + "/" + employee_code_model.employee_code, "./db/"+ employee_code_model.company_code + "_deleted/" + employee_code_model.employee_code)
            return "se removio colaborador exitosamente"
        except OSError as e:
            return("Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        print(e)
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
            return "company doesnt exist"

        collection = db["administradores"]
        deleted_collection = db["administradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = collection.find_one(employee)
        # insertar en nueva coleccion
        deleted_collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        deleted_collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        collection.delete_one(employee)
        return("se removio administrador existosamente")
    except Exception as e:
        print(e)
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
            return "company doesnt exist"

        collaborators = db["colaboradores"]
        marcaciones = db["marcaciones"]

        employee = { "employee_code": employee_code_model.employee_code }
        
        collaborators.delete_one(employee)
        marcaciones.delete_one(employee)

        try:
            shutil.rmtree("./db/"+ employee_code_model.company_code + "/" + employee_code_model.employee_code)
            return "se borro exitosamente"
        except OSError as e:
            return("Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        print(e)
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
            return "company doesnt exist"

        collection = db["administrador"]

        employee = { "employee_code": employee_code_model.employee_code }
        
        collection.delete_one(employee)
        return("se borro administrador exitosamente")
    except Exception as e:
        print(e)
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
            return "company doesnt exist"

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = deleted_collection.find_one(employee)
        # insertar en nueva coleccion
        collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        deleted_collection.delete_one(employee)

        try:
            # mover imagenes a nueva carpeta asumiendo que el directorio nuevo existe. ./db/(company_code)_deleted/(employee_code)
            shutil.move("./db/"+ employee_code_model.company_code + "_deleted/" + employee_code_model.employee_code, "./db/"+ employee_code_model.company_code + "/" + employee_code_model.employee_code)

        except OSError as e:
            return("Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        print(e)
    finally:
        if type(db)==MongoClient:
            db.close()

@app.put("/restore_admin", status_code = 200)
async def restore_admin(employee_code_model: models.employee_code_model):
    db=""
    try:
        db = get_db(employee_code_model.company_code)

        if not db:
            return "company doesnt exist"

        collection = db["colaboradores"]
        deleted_collection = db["colaboradores_borrados"]

        employee = { "employee_code": employee_code_model.employee_code}
        
        # copiar datos de empleado
        employee_document = deleted_collection.find_one(employee)
        # insertar en nueva coleccion
        collection.insert_one(employee_document)
        # actualizar fecha de actualizacion del colaborador borrado para indicar la fecha en la que fue movido a la nueva coleccion.
        updated = {"$set": {"updated": datetime.datetime.now()} }
        collection.update_one(employee, updated)
        # borrar de coleccion de colaboradores
        deleted_collection.delete_one(employee)

    except Exception as e:
        print(e)
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


        # parsed_list_col = []
        # parsed_list_adm = []
        # parsed_list_sup = []
        # parsed_dict_col = {}
        # parsed_dict_adm = {}
        # parsed_dict_sup = {}

        # print(dumps(collaborators))
        # print(dumps(super_admin))

        # for employee in collaborators:
        #     print("loop de empleados")
        #     print(employee)
        #     parsed_dict_col[employee['employee_code']] = {employee["nombre_completo"], employee["image_paths"]}
        #     parsed_list_col.append(employee)

        # for employee in administrators:
        #     parsed_dict_adm[employee['employee_code']] = employee["nombre_completo"]
        #     parsed_list_adm.append({employee["nombre_completo"]})

        # for employee in super_admin:
        #     parsed_dict_sup[employee['employee_code']] = employee["nombre_completo"]
        #     parsed_list_sup.append({employee["nombre_completo"]})

        # print("aqui")
        # print(parsed_list_col)

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
        client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")

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
        client = MongoClient(host='test_mongodb',
                         port=27017, 
                         username='root', 
                         password='pass',
                        authSource="admin")

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