import json 
import base64

import logging
logger = logging.getLogger(__name__)

class RouteNotFoundException(Exception):
    pass 

class UnauthorizedException(Exception):
    pass 

_routes = {}

def _register(method, path, fn):
    logger.warning('hey')
    if method not in _routes:
        _routes[method] = {}
    if path not in _routes[method]:
        _routes[method][path] = { 'fn': fn, 'authorize': [] }
        logger.warning('hasdfjasdfhjasdf')
        logger.warning(_routes)

def lookup(method, path):
    if method in _routes:
        if path in _routes[method]:
            return _routes[method][path]
    raise RouteNotFoundException(f'{method} {path} not found')

def wrap(method, path, wrappingFn):
    if method in _routes:
        if path in _routes[method]:
            oldFn = _routes[method][path]['fn']
            del _routes[method][path]['fn']
            _routes[method][path]['fn'] = lambda b,q: wrappingFn(oldFn(b, q))
            return 
    logger.warn(f'{method} {path} was not found as registered, could not wrap')

def parse_request(environ):
    body = environ['wsgi.input'].readline().decode('utf-8')
    logger.debug(f'Request body: {body}')

    if body:
        logger.debug(f'Parsing body as JSON')
        body = json.loads(body)
    
    query = environ['QUERY_STRING']

    if query:
        logger.debug(f'Processing query content')
        query = [ tuple(p.split('=')) for p in query.split('&') ]

    return body, query 

def authorize(route, environ):
    username = None 
    password = None 
    authenticated = False 

    if 'HTTP_AUTHORIZATION' in environ:
        logger.debug(f'Request has authorization information')
        codedAuth = environ['HTTP_AUTHORIZATION'].split(' ')[1]
        username, password = bytes.decode(base64.b64decode(codedAuth), 'utf-8').split(':')
        authenticated = _authenticate(username, password)

    user_authorized_for_route = username and username in route['authorize']

    if len(route['authorize']) > 0 and not (user_authorized_for_route and authenticated):
        raise UnauthorizedException(f'unauthenticated access is not permitted to {environ["REQUEST_METHOD"]} {environ["PATH_INFO"]}')

def _authenticate(username, password):
    logger.warning(f'CAREFUL, authentication is fake')
    return True 

def responsify(*args):
    
    logger.debug("in responsify with")
    logger.debug(args)

    fn = args[0]
    
    def wrapper(*chain):
        
        logger.debug('in responsify wrapper with')
        logger.debug(chain)
        
        method = chain[0][0][1]
        path = chain[0][0][2]

        # def routeWrapper(response):
        #     logger.warn('muauaha, calling and are wrapping stuff!')
        #     return JsonResponse(response)

        wrap(method, path, fn)

        return chain 

    return wrapper 

def authorize(*args):
    
    logger.debug('in authorize with')
    logger.debug(args)

    username = args[0]

    def wrapper(*funcTup):
    
        logger.debug('in authorize wrapper with')
        logger.debug(funcTup)
    
        method = funcTup[0][1]
        path = funcTup[0][2]
        thisRoute = lookup(method, path)
        if thisRoute:
            logger.debug(f'restricting {method} {path} to {username}')
            thisRoute['authorize'].append(username)
        else:
            logger.warning(f'{method} {path} is not a registered route. cannot restrict with authorization')
        return funcTup
        
    return wrapper 


# def any(*args):
#     return route(args[0])

def post(*args):
    return route(args[0], 'POST')

def get(*args):
    return route(args[0], 'GET')

def route(*args):

    logger.warning(f'in route with')
    logger.debug(args)

    method = args[1]
    path = args[0]

    def wrapper(*chain):

        logger.debug('in route wrapper with')
        logger.debug(chain)

        logger.info(f'registering {method} {path} -> {chain[0].__name__}')
        _register(method, path, chain[0])
        return chain, method, path

    return wrapper

def JsonResponse(obj):
    return json.dumps(obj) #, [('content-type', 'application/json'),]