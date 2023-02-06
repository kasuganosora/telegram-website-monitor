
import requests
from jsonpath_ng import jsonpath, parse
import json
import hashlib
from pyquery import PyQuery as pq
import dns.resolver

def content_check(url, query_str):
    # get url content
    try:
        resp = requests.get(url)
        status_code = resp.status_code
    except:
        status_code = 0

    if status_code < 200 or status_code >= 400:
        ret = dict()
        ret['status_code'] = status_code
        ret['fetch'] = False
        ret['match_hash'] = ''
        ret['match_content'] = ''
        return ret
    

    context_type = resp.headers['Content-Type']
    resp.encoding = resp.apparent_encoding

    if context_type.find('json') == -1 and (resp.text[0] == '[' or resp.text[0] == '{' or resp.text[0] == '"'):
        context_type = 'json'

    body = resp.text.strip()

    if len(body) == 0:
        ret = dict()
        ret['status_code'] = status_code
        ret['fetch'] = True
        ret['match_hash'] = ''
        ret['match_content'] = ''
        return ret

    if len(query_str) == 0:
        ret = dict()
        ret['status_code'] = status_code
        ret['fetch'] = True
        ret['match_hash'] = hashlib.md5(body.encode('utf-8')).hexdigest()
        ret['match_content'] = body.encode('utf-8')
        return ret

    if context_type.find('json') != -1:
        json_data = json.loads(body)
        jsonpath_expression = parse(query_str)
        match = jsonpath_expression.find(json_data)
        match_hash = ''
        if len(match) > 0:
            # md5 hash match content
            match_hash = hashlib.md5(match[0].value.encode('utf-8')).hexdigest()
        ret = dict()
        ret['status_code'] = status_code
        ret['fetch'] = True
        ret['match_hash'] = match_hash
        ret['match_content'] = match[0].value
        return ret
    
    # if is html
    d = pq(body.encode('utf-8'))
    html = d(query_str).html()

    if html is None:
        ret = dict()
        ret['status_code'] = status_code
        ret['fetch'] = True
        ret['match_hash'] = ''
        ret['match_content'] = ''
        return ret

    match = html.strip()
    match_hash = ''

    if len(match) > 0:
        match_hash = hashlib.md5(match.encode('utf-8')).hexdigest()
    ret = dict()
    ret['status_code'] = status_code
    ret['fetch'] = True
    ret['match_hash'] = match_hash
    ret['match_content'] = match
    return ret


def check_domain_can_reg(domain):
    try:
        dns.resolver.query(domain, 'NS')
        return False
    except:
        return True