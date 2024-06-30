$('.recipe-item').click(async function(evt) {
    console.log(evt.target.dataset.recipeid)

    let resp = await axios.post('/lists/add', {
        recipeId: evt.target.dataset.recipeid,
        listTitle: localStorage.getItem('currentList')
    })

    console.log(resp)
})
