# Universal Provisioning System
Python/Flask project designed to manage access of users to specific roles. 
Each request must go through an approval process involving managers and role approvers.
This is a work-in-progress and not all functionality is complete, however many of the core functionalities are completely finished.

## Running the Application ##
  * Install required packages
    * `pip3 install -r requirements.txt`
  * Create the database
    * Execute `python3 scripts/db_create.py`
  * Populate the database with sample data
    * Execute `python3 scripts/db_create.py`
  * Run the application
    * `python3 run.py`
    
## Technologies ##
  * Python/Flask
  * Web Design (Bootstrap)
    * HTML, CSS, JQuery, Jinja
  * Database Object-Relational Mapping (Sql-Alchemy)
    * Database in third normal form
    * Includes many-to-many relationships, mapping tables, and complex database constraints
    * Passwords and hashing
  * AJAX Requests
    * Submitting forms (WTForms), dynamic population of drop downs and other interface elements
  * Clean code, plenty of comments, and well maintained!
  * More to come...