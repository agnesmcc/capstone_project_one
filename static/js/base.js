$(document).ready(function() {
    console.log('started')
    $('#currentList').text(localStorage.getItem('currentList')).show();
});

$('#currentListMenu').click(function(evt) {
    localStorage.setItem('currentList', evt.target.innerText)
    $('#currentList').text(evt.target.innerText)
})