import os
from pprint import pprint

from app import db, app
from models import Recipe

import spoonacular
from spoonacular.models.search_recipes200_response import SearchRecipes200Response
from spoonacular.rest import ApiException

# with app.app_context():
#     db.drop_all()
#     db.create_all()

configuration = spoonacular.Configuration(
    host = "https://api.spoonacular.com"
)
configuration.api_key['apiKeyScheme'] = os.environ["API_KEY"]

with spoonacular.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = spoonacular.RecipesApi(api_client)
    number = 30
    try:
        # Search Recipes
        api_response = api_instance.search_recipes(query='', number=number)
        print("The response of RecipesApi->search_recipes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecipesApi->search_recipes: %s\n" % e)

    recipes = [
        Recipe(
            source_id = recipe.id,
            title = recipe.title,
            image_url = recipe.image
        )
        for recipe in api_response.results
    ]

    with app.app_context():
        db.session.bulk_save_objects(recipes)
        db.session.commit()
