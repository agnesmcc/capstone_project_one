$('#currentListMenu').click(function(evt) {
    localStorage.setItem('currentList', evt.target.innerText)
    $('#currentList').text(evt.target.innerText)
})