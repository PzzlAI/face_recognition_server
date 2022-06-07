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
app.use(express.static('public'));
app.use(express.urlencoded({extended:true}));
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
  const response = '';
  res.render('dashboard-crear-admin',{response});
});

app.post('/crear-admin', async(req,res)=>{
  console.log(req.body);
  const response = await apis.createAdmin(req.body);
  res.render('dashboard-crear-admin',{response});
});

app.get('/admin-list', async(req,res)=>{
  const result = await apis.getAdmin({"company_code": "29"}); // pensar en como hacer la busqueda dinamica para cada respectiva compañia
  res.render('adminList',{result});

});

// error 404 middleware
app.use((req, res) => {
  res.status(404).send('404');
});
