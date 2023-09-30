import sys 
print(sys.path)
from jroutes.routing import responsify, authorize, route, context
import cowpy

logger = cowpy.getLogger()

def wrapResponse(response):
    logger.debug("Hitting this!")
    return response

@context()
def init(context, next):
    logger.debug("in init!!")
    context['this'] = 'works'
    next(context)

# @responsify(wrapResponse)
@authorize('lrichie')
@route("/echo", "GET")
def echo(jtext):
    logger.debug(jtext.context)
    logger.debug(f'echo body: {jtext.body}')
    response = {'body': jtext.body, 'query': jtext.query}
    logger.debug(response)
    return response

if __name__ == "__main__":

    pass 