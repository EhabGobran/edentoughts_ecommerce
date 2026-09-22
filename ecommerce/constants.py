from enum import Enum

class MethodsEnum(Enum):
    GET = "GET"
    POST = "POST"

request_method_enum= {
    MethodsEnum.GET.value: lambda request:None,
    MethodsEnum.POST.value: lambda request:request.POST,
    }



ALLOWED_CONSUMER_DOMAINS = [
    # Google Ecosystem
    "@gmail.com",
    
    # Microsoft Ecosystem (Current & Legacy)
    "@outlook.com",
    "@hotmail.com",
    "@live.com",
    "@msn.com",
    
    # Apple Ecosystem
    "@icloud.com",
    "@me.com",
    "@mac.com",
    
    # Yahoo & AOL
    "@yahoo.com",
    "@aol.com",
    
    # Privacy & Independent Providers
    "@proton.me",
    "@protonmail.com",
    "@fastmail.com",
    "@zoho.com",
    "@yandex.com",
    "@mail.com",
    
    # Major Regional / European Providers
    "@gmx.de",
    "@gmx.net",
    "@web.de",
    "@t-online.de",
    "@orange.fr",
    "@wanadoo.fr",
    "@sfr.fr",
    "@free.fr",
    "@libero.it",
    "@virgilio.it",
    "@uol.com.br",
    "@bol.com.br",
    "@mail.ru",
    "@rambler.ru"
]

