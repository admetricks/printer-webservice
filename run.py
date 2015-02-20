import os
from waitress import serve
from app      import application

serve(application, host='0.0.0.0', port=8080)
