from zeep import Client
from api_key import api_key

client = Client('https://www.hurtopon.pl/HurtoponAPIService.svc?wsdl')
# result1 = client.service.GetOrderByNumber(api_key, 725224)
# print(result1)

result2 = client.service.GetTireOffers(api_key)
print(result2)
