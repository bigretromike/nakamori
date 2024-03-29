from enum import Enum
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from io import BytesIO
import gzip
import json
from lib import cache
from lib.kodi_utils import debug


class APIType(Enum):
    GET = 1
    POST = 2
    DELETE = 3
    PATCH = 4
    PUT = 5


class APIClient:
    """
    Class that create object that will handle all API Calls (aka API Client)

    Attributes
    ----------
    api_address : str
        default address is localhost, use hostname or ip address
    api_port : int
        default port is 8111
    api_version : int
        version of api used for endpoints
    api_key : str
        api_key if needed for most calls
    timeout : int
        time until Request timeout without getting any response
    try_cache: bool
        enable ability to first ask for cached for data and if its expired or missing ask server and cache response

    Methods
    -------
    call(url, call_type, query, data, auth):
        call api based on given url, call_type, query, data and auth parameter while using base class attributes

    """
    def __init__(self,
                 api_proto: str = 'http',
                 api_address: str = 'localhost',
                 api_port: int = 8111,
                 api_version: int = 3,
                 api_key: str = '',
                 timeout: int = 120,
                 try_cache: bool = False
                 ):
        """
        Constructs all the necessary attributes for the person object.

        Parameters
        ----------
            api_proto : str
                protocol used with api call, default is http
            api_address : str
                address that will be used to call api
            api_port : int
                port that will be used to call api
            api_version : int
                version of api that will be used with calls
            api_key: str
                authentication api_key
            timeout: int
                time until Request timeout without getting any response
            try_cache: bool
                nable ability to first ask for cached for data and if its expired or missing ask server and cache response
        """
        self.proto = api_proto
        self.address = api_address
        self.port = api_port
        self.version = api_version
        self.apikey = api_key
        self.timeout = timeout
        self.try_cache = try_cache

    def call(self,
             url: str = '/',
             call_type:
             APIType = APIType.GET,
             query: dict = None,
             data: dict = None,
             auth: bool = True):
        """
        call api based on given url, call_type, query, data and auth parameter while using base class attributes

        Parameters
        ----------
            proto: str
                protocol used with api call, default is http
            url : str
                url that will be added to api address and api port to make full endpoint address to call
            call_type : APIType
                type of call GET/POST/DELETE etc.
            query : dict()
                pass needed query to api
            data: str
                pass data to POST/UPDATE
            auth: bool
                should api call use Authentication (with api_key)
        """
        if query:
            # clear QUERY from all NONE items
            filtered = {k: v for k, v in query.items() if v is not None}
            query.clear()
            query.update(filtered)

            query = urlencode(query)
            url = f"{self.proto}://{self.address}:{self.port}{url}?{query}&api-version={self.version}"
        else:
            if self.version == 2:
                # unfortunately 'api-version' parameter is must-have in api v2
                url = f"{self.proto}://{self.address}:{self.port}{url}?api-version={self.version}"
            else:
                url = f"{self.proto}://{self.address}:{self.port}{url}"  # ?api-version={self.version}"

        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'api-version': f'{self.version}'
        }

        if auth:
            headers['apikey'] = self.apikey
        # if we are doing localhost lets disable gzip for "extra" speed
        if '127.0.0.1' not in url and 'localhost' not in url:
            headers['Accept-Encoding'] = 'gzip'
        # force version 1.0 for Stream because its the way it is
        if '/Stream/' in url:
            headers['api-version'] = '1.0'

        # Api Calls
        req = None
        if call_type == APIType.GET:
            req = Request(url, data=data, headers=headers, method="GET")

        elif call_type == APIType.POST:
            if type(data) is dict:
                data = json.dumps(data).encode("utf-8")
            else:
                byte_data = ('"' + str(data) + '"').encode("utf-8")
                data = byte_data
            req = Request(url, data=data, headers=headers, method="POST")

        elif call_type == APIType.DELETE:
            data = json.dumps(data).encode("utf-8")
            req = Request(url, data=data, headers=headers, method="DELETE")

        elif call_type == APIType.PATCH:
            data = json.dumps(data).encode("utf-8")
            req = Request(url, data=data, headers=headers, method="PATCH")

        elif call_type == APIType.PUT:
            data = json.dumps(data).encode("utf-8")
            req = Request(url, data=data, headers=headers, method="PUT")
        else:
            print(f"Unknown === {url}")
            debug(f"Unknown === {url}")

        print(f"Sending HTTP request: {req.method} {req.get_full_url()}\r\nHeaders: {req.headers}\r\nData: {req.data}")
        debug(f"Sending HTTP request: {req.method} {req.get_full_url()}")
        debug(f"\t\tHeaders: {req.headers}")
        debug(f"\t\tData: {req.data}")

        if req is not None:
            if self.try_cache and req.method == 'GET':
                found_in_cache, response = cache.try_cache(req.selector)
                if not found_in_cache:
                    response = urlopen(req, timeout=int(self.timeout))
                    if response.status == 200:
                        response = response.read()
                        cache.remove_cache(req.selector)
                        try:
                            cache.add_cache(req.selector, response)
                        except:
                            # silent this one
                            pass
                data = response
            else:
                response = urlopen(req, timeout=int(self.timeout))

            if not self.try_cache:
                if response.info().get('Content-Encoding') == 'gzip':
                    try:
                        buf = BytesIO(response.read())
                        f = gzip.GzipFile(fileobj=buf)
                        data = f.read()
                    except Exception as e:
                        print(f"Failed to decompress === {e}")
                else:
                    data = response.read()
                response.close()
            try:
                return json.loads(data)
            except:
                print(f'json fallback to string')
                return data
        return None

    def replace_apikey(self, apikey: str = ''):
        """
        Replace apikey while in-runtime

        Parameters
        ----------
            apikey: str
                apikey that will be pass and save into api client
        """
        self.apikey = apikey

    def set_cache(self, enable_cache):
        self.try_cache = enable_cache
