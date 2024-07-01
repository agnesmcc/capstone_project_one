$('.favorite-selector').click(async function(evt) {
    let favorited = evt.target.classList.contains('fas')
    let recipeId = evt.target.dataset.recipeid
    
    if (!favorited) {
        let resp = await axios.post('/favorites/add', {
            recipeId: recipeId
        })
        console.log(resp)

        evt.target.classList.add('fas')
        evt.target.classList.remove('far')
        
    } else {
        let resp = await axios.post('/favorites/remove', {
            recipeId: recipeId
        })
        console.log(resp)

        evt.target.classList.add('far')
        evt.target.classList.remove('fas')
    }
});
