#!/usr/bin/env python3

import json
import traceback 
import sys 
import logging
from gunicorn.app.base import BaseApplication
from .routing import parse_request, authorize, lookup, authorize, UnauthorizedException, RouteNotFoundException

logger = logging.getLogger(__name__)

def handler(environ, start_response):
    
    return_code = 500
    return_code_message = ''

    response = { 'success': False, 'status_code': return_code, 'server_message': '', 'response': None }
    body = ''
    headers = [('content-type', 'text/plain'),('Access-Control-Allow-Origin', '*')]
    options_headers = [('content-type', 'text/plain'),]

    try:

        logger.debug(",".join([ f'{k}: {v}' for k,v in environ.items() ]))

        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        if method == "OPTIONS":

            logger.debug(f'hey looky, we got us an options!')
            
            response['response'] = {
                'success': True,
                'message': "",
                'data': {}
            }
            
            HAC_method = environ['HTTP_ACCESS_CONTROL_REQUEST_METHOD'] # POST 
            HAC_headers = environ['HTTP_ACCESS_CONTROL_REQUEST_HEADERS'] # content-type
            origin = environ['HTTP_ORIGIN'] # http://localhost:3000
            options_headers.append(('Access-Control-Allow-Origin', origin))
            options_headers.append(('Access-Control-Allow-Methods', HAC_method))
            options_headers.append(('Access-Control-Allow-Headers', HAC_headers))
            options_headers.append(('Access-Control-Max-Age', '86400'))
            
            response['success'] = True 
            response['status_code'] = 204 

            start_response('204 No Content', options_headers)

        else:

            logger.debug(f'Handling {method} {path}')

            thisRoute, parameters = lookup(method, path)

            logger.debug(f'Found route!')

            authorize(thisRoute)

            logger.debug('Authorized!')
            
            body, query = parse_request(environ)

            logger.debug(f'Entering route --- {method} {path}')
            response['response'] = thisRoute['fn'](body, query, **parameters)

            response['success'] = True 
            
            return_code = 200
            return_code_message = 'OK'

            response['status_code'] = return_code

            start_response(f'{return_code} {return_code_message}', headers)
            
    except UnauthorizedException as nae:
        return_code = 401
        return_code_message = 'unauthorized'
        start_response(f'{return_code} {return_code_message}', headers)
        response['server_message'] = str(sys.exc_info()[1])
        response['status_code'] = 401
        logger.error(nae)
    except RouteNotFoundException as rnfe:
        return_code = 404
        return_code_message = 'not found'
        start_response(f'{return_code} {return_code_message}', headers)
        response['server_message'] = str(sys.exc_info()[1])
        response['status_code'] = 404
        logger.error(rnfe)
    except:
        return_code = 500
        return_code_message = 'server error'
        start_response(f'{return_code} {return_code_message}', headers)
        traceback.print_tb(sys.exc_info()[2])
        response['server_message'] = f'{sys.exc_info()[0].__name__}: {str(sys.exc_info()[1])}'
        logger.error(sys.exc_info()[0])
        logger.error(sys.exc_info()[1])
    finally:
        response_str = json.dumps(response)
        logger.info(f'{method} {path} {return_code} {len(response_str)}')        
        return [bytes(response_str, 'utf-8')]

class JroutesApplication(BaseApplication):
    
    def __init__(self, options=None):
        self.options = options or {}
        self.application = handler
        super().__init__()

    def load_config(self):
        config = { key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)
            
    def load(self):
        return self.application 
