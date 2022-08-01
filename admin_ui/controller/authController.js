require('dotenv').config();
const jwt = require('jsonwebtoken');
const dbAPI = require('../helper/APIs');

// .env
// TODO Configurar docker secrets para proteger crendenciales. y probar si sirve el llamado a la variable de entorno

const EXPIRATION_TIME = process.env.EXPIRATION_TIME;
const EXPIRATION_TIME_TOKEN = process.env.EXPIRATION_TIME_TOKEN; 
const SECURE_PHRASE = process.env.SECURE_PHRASE;

module.exports.login_get = (req,res)=>{
    res.render('login');
};

module.exports.login_post =  async(req,res)=>{
    const response = await dbAPI.verifyPassword(req.body.UserName,req.body.UserPass);
    if(response.access){
        const token = jwt.sign({userName:response.name,employee_code:response.employee_code,company_code:response.company_code},SECURE_PHRASE,{expiresIn:EXPIRATION_TIME_TOKEN});
        res.cookie('jwt',token,{EXPIRATION_TIME : 1000*EXPIRATION_TIME,httpOnly:true});
        res.redirect('/');
    }
    else{

        res.render('login',{result: response});
    }
};

module.exports.register_get  = (req,res)=>{
    // TODO Agregar accion de acceder al contenido cuando se registra
    res.render('register'); // TODO Cambiar frontend del createCompany.ejs y habilitar el sitio en el view de login. 
};

module.exports.register_post = (req,res)=>{
    res.render('login');
};

module.exports.logout =  (req,res)=>{
    res.cookie('jwt','',{EXPIRATION_TIME:1}); // 1 milisecond
    res.redirect('/login');
};
