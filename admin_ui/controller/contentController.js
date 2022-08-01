//[x] Crear controller del contenido

//TODO Validar campos vacios en el body. Posiblemente crear un adapter*
// 
const apis = require('../helper/APIs');

module.exports.get_homePage = (req, res) => {
  try {
    res.render('homePage');
  } catch (err) {
    res.status(400).send(err);
  }
};

module.exports.get_createAdministrator = (req, res) => {
  try {
    res.render('createAdministrator');
  } catch (error) {
    res.status(400).send(err);
  }
};

module.exports.post_createAdministrator = async (req, res) => {
  try {
    const feedback = await apis.createAdministrator(req.body.UserNick, req.body.UserPass, req.user.company_code, req.body.employee_code, req.body.UserName, req.body.UserLastName);
    console.log(feedback); // TODO Verificar Endpoint de crear administrador.
    res.render('createAdministrator', { feedback });
  } catch (err) {
    res.status(400).send(err);
  }
};

module.exports.get_administratorsList = async (req, res) => {
  try {
    const employees = await apis.getAdministratorList(company_code = req.user.company_code);
    res.render('administratorsList', { employees, webTitle: "administratorsList" });
  } catch (err) {
    res.status(400).send(err);
  }
};

module.exports.get_collaboratorsList = async (req, res) => {
  try {
    const employees = await apis.getCollaboratorList(req.user.company_code);
    res.render('collaboratorsList', { employees, webTitle: "collaboratorsList" });
  } catch (err) {
    res.status(400).send(err);
  }
};
// [x] Agregar controller de borrar administrador
module.exports.delete_administrator = async (req, res) => {
  try {
    const deleteAdministratorFeedBack = await apis.deleteAdministrator(req.user.company_code, req.query.employee_code);
    res.status(deleteAdministratorFeedBack.status);
  } catch (err) {
    res.status(400).send(err);
  }
};
// [x] Agregar controller de borrar colaborador
module.exports.delete_collaborator = async (req, res) => {
  try {
    const deleteCollaboratorFeedback = await apis.deleteCollaborator(req.user.company_code, req.query.employee_code);
    res.status(deleteCollaboratorFeedback.status);
  } catch (err) {
    res.status(400).send(err);
  }
};
// [x] Agregar controller de obtener sitio de galeria de imagenes de colaborador
module.exports.get_collaboratorPathsImages = async (req, res) => {
  try {
    const pathsImages = await apis.getCollaboratorPathsImages(req.user.company_code, req.query.employee_code);
    res.render('collaboratorImagesGallery', { pathsImages: pathsImages.paths, fullname: req.query.fullname });
  } catch (err) {
    res.status(400).send(err);
  }
};
// [x] Agregar controller de obtener imagen de colaborador
module.exports.get_collaboratorImage = async (req, res) => {
  try {
    const image = await apis.getCollaboratorImage(req.query.path);
    res.send(image);
  } catch (err) {
    res.status(400).send(err);
  }
};