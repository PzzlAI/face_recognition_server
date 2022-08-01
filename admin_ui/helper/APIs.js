// References:
// NODE FETCH
// https://docs.thousandeyes.com/product-documentation/browser-synthetics/transaction-tests/api-monitoring/node-fetch-module#example-get-request-with-authentication
// https://www.codegrepper.com/code-examples/javascript/node-fetch+authorization+header
// https://www.npmjs.com/package//node-fetch#simple-post
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#body

//FASAPI
// https://stackoverflow.com/questions/63984555/fetch-in-javascript-for-fastapi-in-localhost
// https://fastapi.tiangolo.com/tutorial/cors/#origin

//  'Authorization': "Basic " + Buffer.from(`${username}:${password}`).toString('base64')
//  'Content-Type':'application/x-www-form-urlencode'
//  mode: 'cors', // no-cors, *cors, same-origin

//https://javascript.info/coding-style#function-placement

const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));
require('dotenv').config();

const API_TOKEN = process.env.API_TOKEN;
const API_DOMAIN = process.env.API_DOMAIN;
const API_PORT = (process.env.API_PORT).toString();


// funciones de peticiones.
const getAdministratorList = (company_code) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/read_administrators`;
  const body = {
    company_code
  }
  const administradorList = fetchData(url, body)
    .then(response => {
      return response.json();
    });
  return administradorList;
};

const getCollaboratorList = (company_code) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/read_collaborators`;
  const body = {
    company_code
  }
  const collaboratorList = fetchData(url, body)
    .then(response => {
      return response.json();
    });
  return collaboratorList;
};

const verifyPassword = (username, password) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/superadmin_login`;
  const body = {
    username,
    password
  }
  const validation = fetchData(url, body)
    .then(response => {
      return response.json();
    });
  return validation;
};


const createAdministrator = (username, password, company_code, employee_code, name, lastname) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/create_admin`;
  const body = {
    username,
    password,
    company_code,
    employee_code, //TODO Asignar codigo de empleado autogenerado.
    nombre_completo: `${name} ${lastname}`
  };
  const feedback = fetchData(url, body)
    .then(response => {
      return response.json();
    });
  return feedback;
};

const deleteAdministrator = (company_code, employee_code) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/delete_admin`;
  const body = {
    company_code,
    employee_code
  };
  const feedback = fetchData(url, body, 'DELETE')
    .then(response => {
      return response.json();
    });
  return feedback;
};

const deleteCollaborator = (company_code, employee_code) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/delete_collaborator`;
  const body = {
    company_code,
    employee_code
  };
  const feedback = fetchData(url, body, 'DELETE')
    .then(response => {
      return response.json();
    });
  return feedback;
};

const getCollaboratorPathsImages = (company_code, employee_code) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/get_image_paths`;
  const body = {
    company_code,
    employee_code
  }
  const pathsImages = fetchData(url, body)
    .then(response => {
      return response.json();
    });
  return pathsImages;
}

const getCollaboratorImage = (path) => {
  const url = `http://${API_DOMAIN}:${API_PORT}/get_image_from_path`;
  body = {
    path
  }
  const image = fetchImage(url, body)
    .then(response => {
      return response.buffer();
    });
  return image;
}

async function fetchData(url = '', body = {}, method = 'POST') {
  const promise = await fetch(url, {
    method, 
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'key': API_TOKEN
    },
    body: JSON.stringify(body),
  });
  return promise;
}

async function fetchImage(url, body) {
  const promise = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'key': API_TOKEN
    },
    body: new URLSearchParams(body)
  });
  return promise;
}




module.exports = { getAdministratorList, getCollaboratorList, createAdministrator, verifyPassword, deleteAdministrator, deleteCollaborator, getCollaboratorPathsImages, getCollaboratorImage };