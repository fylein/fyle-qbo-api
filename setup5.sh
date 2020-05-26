#!/bin/bash# Django Settings
export SECRET_KEY='#)^6o52k_j&wl$39k-e^w&@9%mi-o#c3*!p=+2cl(&4q@u384x'
export ALLOWED_HOSTS='localhost'
export DEBUG=True

# Database Settings
export DB_NAME=qbo_api
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_SCHEMA=public
export DB=localhost
export DB_PORT=5432 # Fyle Settings

# Fyle Settings
#export API_URL='http://337245c8.ngrok.io/api'
#export FYLE_BASE_URL='https://staging.fyle.in'
#export FYLE_CLIENT_ID='tpaPu6HJt8hfL'
#export FYLE_CLIENT_SECRET='1TzV6yhy6U'
#export FYLE_TOKEN_URI='https://accounts.staging.fyle.in/api/oauth/token'
#export FYLE_JOBS_URL='https://jobs.staging.fyle.in/v2/jobs'

#export API_URL='http://localhost:8000/api'
export API_URL='http://337245c8.ngrok.io/api'
export FYLE_BASE_URL='https://accounts.staging.fyle.in'
export FYLE_CLIENT_ID='tpaPu6HJt8hfL'
export FYLE_CLIENT_SECRET='1TzV6yhy6U'
export FYLE_TOKEN_URI='https://accounts.staging.fyle.in/api/oauth/token'
export FYLE_JOBS_URL='https://jobs.staging.fyle.in/v2/jobs'

# QBO Settings
export QBO_CLIENT_ID='ABTemcw1ngLRye1iqW25EI2CyNUzdBSkNYWYxaFtkaJNgRcbM5'
export QBO_CLIENT_SECRET='LrJ9lXeC3QCnLeTqAaQSF8iPk36TX8Enh4KcUorP'
export QBO_REDIRECT_URI='http://localhost:4200/workspaces/qbo/callback'
#export QBO_REDIRECT_URI='https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl'
export QBO_TOKEN_URI='https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
export QBO_ENVIRONMENT='sandbox'



## Redis Settings
#export REDIS_HOST=''
#export REDIS_PORT='6379'
#export REDIS_DB=''#client_id = tpa3I6wzhbnnR
#client_secret = WkZ36KxO06
