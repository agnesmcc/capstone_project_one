
$(document).ready(function() {
    console.log('started')
    $('#currentList').text(localStorage.getItem('currentList')).show();
});
