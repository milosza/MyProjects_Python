import credentials
import json
from pyAllegro.api import AllegroRestApi


RestApi = AllegroRestApi()

RestApi.credentials_set(
        appName='',
        clientId=credentials.ClientID,
        clientSecred=credentials.ClientSecret,
        redirectUrl=credentials.Redirect_URI
        )
RestApi.get_token()

# status_code, json_data = RestApi.resource_get(
#         resource_name='/users/{userId}/ratings-summary'.format(
#                 **{'userId': 11791190}),
#         params={}
#         )

status_code, json_data = RestApi.resource_get(
        resource_name='/offers/listing',
        params={'phrase': 'Dunlop SP SPORT BLURESPONSE 205/55R16 91V',
                'limit': 10,
                'parameter.11323': 11323_2
                }
        )
print(status_code)
print(json.dumps(json_data, sort_keys=True, indent=4))