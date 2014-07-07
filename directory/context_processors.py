from multi_city import is_multi_city

def multi_city(request):
    return {'MULTI_CITY': is_multi_city(request)}
