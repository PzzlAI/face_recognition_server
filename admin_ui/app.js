const express = require('express')
const cors = require('cors')
const path = require('path')

const app = express()
// app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'views')));

// app.set('view engine', 'pug');

app.use(cors())


//pagina principal
app.get('/', (req, res) => {
  res.sendFile(__dirname + "/views/dashboard-pagina-principal.html")
})

app.listen(4000, () => {
  console.log('listening for requests on port 4000')
})