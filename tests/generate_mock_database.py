import requests
# import cv2
import names

counter = 0

def generate_mock_companies(endpoint: str, company_count: int):

    global counter
    for i in range(company_count):
        data = {"company_code": i, 
                "employee_code": counter, 
                "username": "admin" + str(counter), 
                "password": "admin" + str(counter) + "pass", 
                "nombre_completo": names.get_full_name()
                }
        counter += 1
        response = requests.post(
            endpoint,
            json = data
        )

        print(response.json())

def generate_mock_administrators(endpoint: str, amount: int, company_count: int):
    global counter
    for i in range(company_count):
        for w in range(counter, counter + amount):
            data = {"company_code": i, 
                    "employee_code": w, 
                    "username": "admin" + str(w), 
                    "password": "admin" + str(w) + "pass", 
                    "nombre_completo": names.get_full_name()
                    }
            counter += 1
            response = requests.post(
                endpoint,
                json = data
            )

            print(response.json())

def generate_mock_collaborators(endpoint: str, amount: int, company_count: int):

    global counter
    for i in range(company_count):
        for w in range(counter, counter + amount):
            data = {"company_code": i, 
                    "employee_code": w, 
                    "nombre_completo": names.get_full_name()
                    }
            counter += 1
            response = requests.post(
                endpoint,
                json = data
            )

            print(response.json())

if __name__ == "__main__":
    company_count = 3
    collaborator_count = 3
    admin_count = 3
    generate_mock_companies(endpoint = 'http://localhost:5000/create_company', company_count = company_count)
    generate_mock_collaborators(endpoint = 'http://localhost:5000/create_collaborator', amount = collaborator_count, company_count = company_count)
    generate_mock_administrators(endpoint = 'http://localhost:5000/create_admin', amount = admin_count, company_count = company_count)
