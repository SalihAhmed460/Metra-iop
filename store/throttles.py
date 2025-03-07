from rest_framework.throttling import AnonRateThrottle

class SearchRateThrottle(AnonRateThrottle):
    rate = '60/minute'  # More permissive for search to allow for autocomplete
    
    def get_cache_key(self, request, view):
        # Use the IP address and search term as the unique cache key
        ident = self.get_ident(request)
        return f'search_throttle_{ident}_{request.GET.get("q", "")}'