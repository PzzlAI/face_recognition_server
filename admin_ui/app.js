const express = require('express');
const res = require('express/lib/response');
const morgan = require('morgan');

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
app.get('/admin-list',(req,res)=>{
  res.render('adminList');
})

// error 404 middleware
app.use((req, res) => {
  res.status(404).send('404');
});