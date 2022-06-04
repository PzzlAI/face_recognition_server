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

<<<<<<< HEAD
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
=======
//pagina principal
app.get('/', (req, res) => {
  res.sendFile(__dirname + "/views/dashboard-pagina-principal.html")
})

app.listen(4000, () => {
  console.log('listening for requests on port 4000')
})
>>>>>>> 05dd7189b8991f3e626a900eac0e10cdeacfeee7
