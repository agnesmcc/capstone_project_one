# Tender
### Like Tinder, But For Food!

API used: https://spoonacular.com/food-api/docs

## Description
Tender is a website that allows users to build lists of recipes that are shown to them at random. The homepage displays three random recipes that the user can add to their lists or favorites. 

Users can...

* Be shown images of random recipes
* Add recipes to lists
* Create new lists
* Add receipes to favorites
* Edit their account

## Typical User Flow

1. A user is presented with a signup page. After they sign up they are redirected to the homepage.

2. On the homepage the user sees three random recipes and a button to show three new ones. They also have a default list created and selected in the navigation bar.

3. Clicking on a recipe will add that recipe to the user's list. Clicking on the heart icon will add a recipe to the user's favorites.

4. The user can click on a link in the nav bar to see a list of their lists. From here they can create new lists. They can click on a list to see the recipes added to that list.

5. After viewing a list, they can remove recipes from the list, add or remove recipes on the list to their favorites, or delete the entire list.

6. Similar to lists, the user can click on a link in the nav bar to view their favorites. The can click on the heart icon to remove favorited recipes.

7. After adding new lists, the user can select which list they are adding recipes to using the dropdown in the nav bar.

8. Finally, there is a link in the navbar for editing the user's account. They can change their username or password, or delete their account.

## Technology Used
* Python
* Flask
* WTForms
* Postgres
* SQLAlchemy
* Spoonacular API