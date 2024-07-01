$('.favorite-selector').click(async function(evt) {
    let resp = await axios.post('/favorites/add', {
        recipeId: evt.target.dataset.recipeid
    })

    console.log(resp)
});
