const userRaw = document.querySelector('tbody');

userRaw.addEventListener('click', e => {
    if (e.target.classList.contains('icon-delete')) {
        e.target.parentElement.parentElement.remove()
        const id = e.target.parentElement.parentElement.id;
        fetch(`/administrators-list?employee_code=${id}`, { method: 'DELETE' }); // FIXME Se queda esperando la respuesta del servidor.
    }
});