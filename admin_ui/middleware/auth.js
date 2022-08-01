const jwt = require("jsonwebtoken");
require('dotenv').config();

const SECURE_PHRASE = process.env.SECURE_PHRASE;

const verifyToken = (req, res, next) => {
  const token = req.cookies.jwt;

  if (!token) {
    return res.status(403).redirect('/login');
  }
  try {
    const decoded = jwt.verify(token, SECURE_PHRASE);
    // Obtener datos de usuario utiles para hacer los request al API
    req.user = decoded;
  } catch (err) {
    return res.status(401).redirect('/login');
  }
  return next();
};

module.exports = verifyToken;