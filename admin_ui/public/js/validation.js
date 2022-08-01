// FIXME Revisar nuevo codigo para evitar el refresh de la página.
//NOTA: lo hace pero no recibe el feedback. Revisar los videos de the net ninja!
// if(document.title !== 'Login'){
// const form = document.querySelector('form').addEventListener('submit',(event) => event.preventDefault());
// }

// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  var forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.prototype.slice.call(forms)
    .forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }

        form.classList.add('was-validated')
      }, false)
    })
})();