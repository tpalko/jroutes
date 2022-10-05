import os
import sys
import importlib 

def process_modules():

    route_modules = os.getenv('SERVER_ROUTE_MODULES')
    # logger.debug(f'Route modules: {route_modules}')
    if route_modules:
        for module_name in [ m for m in route_modules.split(',') if m ]:
            # logger.debug(f'Importing routing module {module_name}')
            importlib.import_module(module_name)

process_modules()

# -- we can't touch anything that creates a logger until all modules are imported
# -- why?
# -- because maybe one of the imported modules just happens to be using a logging library that messes with the logging default logger class
# -- and maybe adds custom formatting fields
# -- because maybe, just may be..
from .routing import _routes 
import logging 
import json 

logger = logging.getLogger('jroutes')
logger.info(f'{json.dumps({ m: { p: { **_routes[m][p], "fn": _routes[m][p]["fn"].__name__ } for p in _routes[m] } for m in _routes }, indent=4)}')

if __name__ == "__main__":

    # -- if executed directly, we use our gunicorn BaseApplication implementation
    from .serving import JroutesApplication
    port = os.getenv('PORT', 9001)
    JroutesApplication({'bind': f'0.0.0.0:{port}', 'workers': 1}).run()

else:

    # -- if imported by gunicorn.app.wsgiapp
    # -- give it what it wants 
    from .serving import handler as application 
