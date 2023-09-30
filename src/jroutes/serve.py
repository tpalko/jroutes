import os
import sys
import importlib 

def process_modules(route_modules):
    # logger.debug(f'Route modules: {route_modules}')
    if route_modules:
        for module_name in [ m for m in route_modules.split(',') if m ]:
            # logger.debug(f'Importing routing module {module_name}')
            importlib.import_module(module_name)

route_modules = os.getenv('SERVER_ROUTE_MODULES')
port = int(os.getenv('JROUTES_LISTEN_PORT', 8000))
host = os.getenv('JROUTES_LISTEN_HOST', '0.0.0.0')
workers = int(os.getenv('JROUTES_WORKERS', 1))
keyfile = os.getenv('JROUTES_KEYFILE', None)
certfile = os.getenv('JROUTES_CERTFILE', None)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '-r' and len(sys.argv) > i + 1:                
                route_modules = sys.argv[i+1]
            elif arg == '-p' and len(sys.argv) > i + 1:
                port = sys.argv[i+1]
            elif arg == '-h' and len(sys.argv) > i + 1:
                host = sys.argv[i+1]
            elif arg == '-w' and len(sys.argv) > i + 1:
                workers = sys.argv[i+1]

    process_modules(route_modules)

    # -- we can't touch anything that creates a logger until all modules are imported
    # -- why?
    # -- because maybe one of the imported modules just happens to be using a logging library that messes with the logging default logger class
    # -- and maybe adds custom formatting fields
    # -- because maybe, just may be..
    from .routing import _routes 
    import cowpy 
    import json 

    logger = cowpy.getLogger()
    logger.info(f'{json.dumps({ m: { p: { **_routes[m][p], "fn": _routes[m][p]["fn"].__name__ } for p in _routes[m] } for m in _routes }, indent=4)}')

    # -- if executed directly, we use our gunicorn BaseApplication implementation
    from .serving import JroutesApplication    
    
    gunicorn_settings = {
        'bind': f'{host}:{port}', 
        'workers': workers,
        'keyfile': keyfile,
        'certfile': certfile,
        # 'print_config': False,
        # 'logging_class': cowpy.CowpyGunicorn
    }

    logger.debug(gunicorn_settings)

    japp = JroutesApplication(gunicorn_settings)

    logger.info(f'Starting JroutesApplication')
    japp.run()

else:

    process_modules(route_modules)

    # -- if imported by gunicorn.app.wsgiapp
    # -- give it what it wants 
    from .serving import handler as application 

    import cowpy
    logger = cowpy.getLogger()
    logger.info("application is available")
