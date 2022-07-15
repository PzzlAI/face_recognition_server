const express = require('express');
const morgan = require('morgan');
const apis = require('./controller/dbAPI');
const cookieParser = require('cookie-parser');
const requireAuth = require('./middleware/auth');
const authRouter = require('./routes/authRouter');
const app = express();

// template engine
app.set('view engine','ejs');

// listening on port
app.listen(3000,()=>{
  console.log("Express server listening on port 3000");
});

// public files
app.use(express.static('public'));

// middleware
app.use(express.json());
app.use(cookieParser());
app.use(express.urlencoded({extended:true}));


// logger middleware
app.use(morgan('dev'));

app.get('/',(req,res)=>{
  res.redirect('login');
})

// routes
app.use(authRouter);


app.get('/dashboard',requireAuth,(req,res)=>{
  res.render('dashboard-pagina-principal');
});

app.get('/crear-admin',requireAuth,(req,res)=>{
  const response = '';
  res.render('dashboard-crear-admin',{response});
});

app.post('/crear-admin', requireAuth,async(req,res)=>{
  console.log(req.body);
  const response = await apis.createAdmin({
    "username": req.body.UserName,
    "password": req.body.UserPass,
    "company_code": req.user.company_code, 
    "employee_code":req.body.employee_code , // asignarle uno generado.
    "nombre_completo":`${req.body.UserName} ${req.body.UserLastName}`
  });
  res.render('dashboard-crear-admin',{response});
});

app.get('/admin-list', requireAuth,async(req,res)=>{
  const result = await apis.getAdminList({"company_code": req.user.company_code}); 
  console.log(result);
  res.render('adminList',{result});
});
app.get('/collaborators-list', requireAuth,async(req,res)=>{
  const result = await apis.getCollaboratorList({"company_code": req.user.company_code}); 
  console.log(result);
  res.render('collaboratorList',{result});
});

// error 404 middleware
app.use((req, res) => {
  res.status(404).send('404');
});
