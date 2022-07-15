require('dotenv').config();
const jwt = require('jsonwebtoken');
const dbAPI = require('../controller/dbAPI');
const { response } = require('../routes/authRouter');

// test for example of credential validation 
const  pass = 'passto123test';
const id = 10;

// controllers
const maxAge = process.env.MAXAGE; // 259200 = 1 day
const maxAgeToken = process.env.MAXAGETOKEN; //24h 
const securePhrase = process.env.FRASE;

module.exports.login_get = (req,res)=>{
    res.render('login')
}

module.exports.login_post =  async(req,res)=>{
    // verifica contraseña
    const response = await dbAPI.verifyPassword({
        "username": req.body.UserName,
        "password": req.body.UserPass
    });
    
    if(response.access){
        //console.log(req.body);
        const token = jwt.sign({userName:response.name,employee_code:response.employee_code,company_code:response.company_code},securePhrase,{expiresIn:maxAgeToken});
        res.cookie('jwt',token,{maxAge : 1000*maxAge,httpOnly:true});
        res.redirect('/dashboard');
    }
    else{
        // agregar feedback en caso de introduccion mal de credenciales
        res.redirect('/login');
    }
}

module.exports.register_get  = (req,res)=>{
    res.render('createCompany') // cambiar frontend del createCompany.ejs
}
module.exports.register_post = (req,res)=>{
    res.render('register');
}

module.exports.logout =  (req,res)=>{
    res.cookie('jwt','',{maxAge:1});
    res.redirect('/login');
}

