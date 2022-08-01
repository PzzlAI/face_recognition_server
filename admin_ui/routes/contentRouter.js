const requireAuth = require('../middleware/auth');
const contentController = require('../controller/contentController');
const Router = require('express');
const router = Router();
// TODO Cambiar nombres de direccion, quitando los verbos.
router.get('/', requireAuth, contentController.get_homePage);

router.get('/create-administrator', requireAuth, contentController.get_createAdministrator);

router.post('/create-administrator', requireAuth, contentController.post_createAdministrator);

router.get('/administrators-list', requireAuth, contentController.get_administratorsList);

router.delete('/administrators-list', requireAuth, contentController.delete_administrator); // [x] Agregar middleware de borrar administrdores

router.get('/collaborators-list', requireAuth, contentController.get_collaboratorsList);

router.delete('/collaborators-list', requireAuth, contentController.delete_collaborator); // [x] Agregar middleware de borrar colaboradores

router.get('/collaborator-images-gallery', requireAuth, contentController.get_collaboratorPathsImages); //[x] Agregar middleware de galeria de imagenes del colaborador de lista de colaboradores.

router.get('/collaborator-images', requireAuth, contentController.get_collaboratorImage);//[x] Agregar middleware obtener de imagenes del colaborador.

module.exports = router;