const express = require('express');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const contentRouter = require('./routes/contentRouter');
const authRouter = require('./routes/authRouter');
require('dotenv').config();

const BACKEND_PORT = process.env.BACKEND_PORT;
const app = express();

// template engine
app.set('view engine', 'ejs');

// listening on port
app.listen(BACKEND_PORT, () => {
  console.log("Express server listening on port", BACKEND_PORT);
});

// public files
app.use(express.static('public'));

// tools middleware
app.use(express.json());
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev')); // logger middleware

app.use(authRouter);
app.use(contentRouter);

app.use((req, res) => res.status(404).render('404'));