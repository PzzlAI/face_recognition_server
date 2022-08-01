const requireAuth = require('../middleware/auth');
const contentController = require('../controller/contentController');
const Router = require('express');
const router = Router();
// TODO Cambiar nombres de direccion, quitando los verbos.
router.get('/', requireAuth, contentController.get_homePage);

router.get('/create-administrator', requireAuth, contentController.get_createAdministrator);

router.post('/create-administrator', requireAuth, contentController.post_createAdministrator);

router.get('/administrators-list', requireAuth, contentController.get_administratorsList);

router.delete('/administrators-list', requireAuth, contentController.delete_administrator); 

router.get('/collaborators-list', requireAuth, contentController.get_collaboratorsList);

router.delete('/collaborators-list', requireAuth, contentController.delete_collaborator); 

router.get('/collaborator-images-gallery', requireAuth, contentController.get_collaboratorPathsImages); 

router.get('/collaborator-images', requireAuth, contentController.get_collaboratorImage);.

module.exports = router;