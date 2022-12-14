#!/usr/bin/env python3

import os
import json
import traceback 
import sys 
from .routing import _routes, parse_request, JsonResponse, authorize, route, responsify, lookup, authorize, UnauthorizedException, RouteNotFoundException
import importlib 

from common.log import LogProvider 
logger = LogProvider.getLogger(__name__)

def wrapResponse(response):
    logger.debug("Hitting this!")
    return response

@responsify(wrapResponse)
@authorize('tpalko')
@route("/echo", "GET")
def echo(body, query):
    logger.debug(f'echo body: {body}')
    response = {'body': body, 'query': query}
    logger.debug(response)
    return response

route_modules = os.getenv('SERVER_ROUTE_MODULES')
logger.debug(f'Route modules: {route_modules}')
if route_modules:
    for module_name in [ m for m in route_modules.split(',') if m ]:
        logger.info(f'Importing routing module {module_name}')
        importlib.import_module(module_name)

logger.debug(f'{json.dumps({ m: { p: { **_routes[m][p], "fn": _routes[m][p]["fn"].__name__ } for p in _routes[m] } for m in _routes }, indent=4)}')

def handler(environ, start_response):
    
    response = { 'success': False, 'status_code': 500, 'message': '', 'response': None }
    body = ''
    headers = [('content-type', 'text/plain'),]
    
    try:

        logger.debug(",".join([ f'{k}: {v}' for k,v in environ.items() ]))

        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        logger.debug(f'Handling {method} {path}')

        thisRoute = lookup(method, path)

        logger.debug(f'Found route!')

        authorize(thisRoute)

        logger.debug('Authorized!')
        
        body, query = parse_request(environ)

        logger.debug(f'Entering route --- {method} {path}')
        response['response'] = thisRoute['fn'](body, query)
        response['success'] = True 
        response['status_code'] = 200

        start_response('200 OK', headers)

    except UnauthorizedException as nae:
        start_response('401 unauthorized', headers)
        response['message'] = str(sys.exc_info()[1])
        response['status_code'] = 401
        logger.error(response['message'])
    except RouteNotFoundException as rnfe:
        start_response('404 not found', headers)
        response['message'] = str(sys.exc_info()[1])
        response['status_code'] = 404
        logger.error(response['message'])
    except:
        traceback.print_tb(sys.exc_info()[2])
        start_response('500 server error', headers)
        response['message'] = f'{sys.exc_info()[0].__name__}: {str(sys.exc_info()[1])}'
        logger.error(response['message'])        
    finally:
        return [bytes(json.dumps(response), 'utf-8')]