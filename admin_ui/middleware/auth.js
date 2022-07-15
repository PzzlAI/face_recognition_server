const jwt = require("jsonwebtoken");
require('dotenv').config();

const securePhrase = process.env.FRASE;

const verifyToken = (req, res, next) => {
  const token = req.cookies.jwt

  if (!token) {
    return res.status(403).redirect('/login');
  }
  try {
    const decoded = jwt.verify(token, securePhrase);
    req.user = decoded;
  } catch (err) {
    return res.status(401).redirect('/login');
  }
  return next();
};

module.exports = verifyToken;