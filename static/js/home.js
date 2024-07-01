$('.recipe-item').click(async function(evt) {
    let resp = await axios.post('/lists/add', {
        recipeId: evt.target.dataset.recipeid,
        listTitle: localStorage.getItem('currentList')
    })

    console.log(resp)
})
