class EnsureCORSHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            # If your view/Lambda crashes, this ensures CORS is still returned
            from django.http import JsonResponse
            response = JsonResponse({"error": str(e)}, status=500)

        # Add CORS headers manually on ALL responses
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"

        return response
