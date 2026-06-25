from app import app, init_db
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

init_db()

# Permet à Flask de fonctionner sous le sous-chemin /mvpt4
application = DispatcherMiddleware(
    Response('Not Found', status=404),
    {'/mvpt4': app}
)
