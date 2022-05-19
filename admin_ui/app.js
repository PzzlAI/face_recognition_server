const express = require('express')
const cors = require('cors')
const path = require('path')

const app = express()
// app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'views')));

// app.set('view engine', 'pug');

app.use(cors())


//login
// app.get('/', (req, res) => {
//   res.sendFile(__dirname + "/views/login.html")
// })

//pagina principal
app.get('/', (req, res) => {
  res.sendFile(__dirname + "/views/dashboard-pagina-principal.html")
})

// crear admin
app.get('/create_admin', (req, res) => {
  res.send("create_admins");
})

// lista de admins
app.get('/get_admins', (req, res) => {
  res.send("get_admins");
})

// lista de colaboradores
app.get('/get_colaborators', (req, res) => {
  res.send("get_admins");
})



app.listen(4000, () => {
  console.log('listening for requests on port 4000')
})