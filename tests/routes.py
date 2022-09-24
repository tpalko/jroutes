from jroutes.routing import responsify, authorize, route 
import logging 

logger = logging.getLogger(__name__)

def wrapResponse(response):
    logger.debug("Hitting this!")
    return response

@responsify(wrapResponse)
@authorize('lrichie')
@route("/echo", "GET")
def echo(body, query):
    logger.debug(f'echo body: {body}')
    response = {'body': body, 'query': query}
    logger.debug(response)
    return response

if __name__ == "__main__":

    pass 