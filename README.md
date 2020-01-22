# Fyle QBO API
Django Rest Framework API for Fyle Quickbooks Online Integration


### Setup

* Rename setup_template.sh to setup.sh

    ```
    $ mv setup_template.sh setup.sh
    ```
  
* Setup environment variables in setup.sh

    ```bash
    # Django Settings
    export SECRET_KEY=YOUR DJANGO SECRET KEY
    export ALLOWED_HOSTS=HOSTS SEPARATED BY COMMAS
    export DEBUG=True
    
    # Database Settings
    export DB_NAME=POSTGRES DB NAME
    export DB_USER=POSTGRES DB USER
    export DB_PASSWORD=POSTGRES DB PASSWORD
    export DB_HOST=POSTGRES DB
    export DB_PORT=POSTGRES DB PORT
    
    # Fyle Settings
    export FYLE_BASE_URL=FYLE BASE URL
    export FYLE_CLIENT_ID=FYLE CLIENT ID
    export FYLE_CLIENT_SECRET=FYLE CLIENT SECRET
    export FYLE_TOKEN_URI=FYLE TOKEN URI
    
    # QBO Settings
    export QBO_CLIENT_ID=QBO CLIENT ID
    export QBO_CLIENT_SECRET=QBO CLIENT SECRET
    export QBO_REDIRECT_URI=QBO REDIRECT URI
    export QBO_TOKEN_URI=QBO TOKEN URI
   ```

* Install the requirements

    ```
    pip install -r requirements.txt
    ```

* Run the migrations

    ```
    python manage.py migrate
    ```

* Create superuser

    ```
    python mange.py createsuperuser
    ```

* run the development server

    ```
    bash run.sh
    ```
