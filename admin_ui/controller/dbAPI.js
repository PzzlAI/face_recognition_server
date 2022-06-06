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


const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const password = 'dW4gY2hpc3Rl';
const port = '5000';
const domain = "localhost";


async function getData(url = '', data = {}) {
    const response = await fetch(url, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      
      headers:  {
        'Accept': 'application/json',
        'Content-Type': 'application/json',   
        'key': password
       
      },
      body: JSON.stringify(data),
    });
    return response.json(); // parses JSON response into native JavaScript objects
  }

// Request
const  adminlist = (data) => {
  url=`http://${domain}:${port}/read_administrators`
  const res = getData(url,data )
  .then(result => {
    // console.log(res); // JSON data parsed by `data.json()` call
    return result;
  });
  return res;
}
 module.exports = {adminlist};