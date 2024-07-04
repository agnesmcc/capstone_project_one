$(document).ready(function() {
    console.log('started')

    if (!localStorage.getItem('currentList')) {
        const firstListTitle = $('#currentListMenu li:first-child a').text();
        localStorage.setItem('currentList', firstListTitle);
    }

    $('#currentList').text(localStorage.getItem('currentList')).show();
})

$('#currentListMenu').click(function(evt) {
    localStorage.setItem('currentList', evt.target.innerText)
    $('#currentList').text(evt.target.innerText)
})