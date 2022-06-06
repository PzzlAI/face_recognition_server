const { json } = require('express');
const express = require('express');
const morgan = require('morgan');
const apis = require('./controller/dbAPI');


const app = express();

// template engine
app.set('view engine','ejs');

// listening on port
app.listen(3000,()=>{
  console.log("Express server listening on port 3000");
});

// public files
app.use(express.static('public'))

// logger middleware
app.use(morgan('dev'));

app.get('/',(req,res)=>{
  res.redirect('login');
})

app.get('/login',(req,res)=>{
  res.render('login');
});

app.get('/dashboard',(req,res)=>{
  res.render('dashboard-pagina-principal');
});

app.get('/crear-admin',(req,res)=>{
  res.render('dashboard-crear-admin');
});
app.get('/admin-list', async(req,res)=>{
  const result = await apis.adminlist({"company_code": "29"}); // pensar en como hacer la busqueda dinamica para cada respectiva compañia
  console.log(result);
  const data =  JSON.stringify(result);
  console.log(typeof	data);
  res.render('adminList',{data});

});

// error 404 middleware
app.use((req, res) => {
  res.status(404).send('404');
});
