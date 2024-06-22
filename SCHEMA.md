## TABLES

### Users

Primary key: id

* id; autoinc integer
* first_name; string; required
* last_name; string; required
* username; string; required; unique
* email; string; required; unique
* password; string; required
* favorites; fk to Recipes
* lists; fk to Lists

### Lists

Primary key: id

* id; autoinc integer
* title; string; required; unique
* description; string
* recipes; fk to recipes
* username; fk to users

### Recipes

Primary key: id

* id; autoinc integer
* source_id; integer; required
* title; string; required
* image_url; string; required

### UsersFavoritesRecipes

Primary key: user_id + recipe_id

* user_id; fk to user
* recipe_id; fk to recipes

### ListsRecipes

Primary key: lists_id + recipe_id

* lists_id; fk to lists
* recipe_id; fk to recipes
