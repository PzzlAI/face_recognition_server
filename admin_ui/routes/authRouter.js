const authController  = require('../controller/authController');
const Router = require('express');
const router = Router();

router.get('/login',authController.login_get);

router.post('/login',authController.login_post);

router.get('/register',authController.register_get);

router.post('/register',authController.register_post);

router.get('/logout',authController.logout);

module.exports =  router;