"""
Custom middleware for multi-tenancy support.
"""


class RestaurantContextMiddleware:
    """
    Middleware that attaches the current restaurant to the request object.

    For authenticated users with a restaurant_user profile, it sets:
    - request.restaurant: The restaurant the user belongs to
    - request.user_role: The user's role (SUPER_ADMIN, RESTAURANT_MANAGER, KITCHEN_STAFF)

    For anonymous users or users without a restaurant, these are set to None.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Initialize restaurant and role
        request.restaurant = None
        request.user_role = None

        # If user is authenticated, try to get their restaurant
        if request.user.is_authenticated:
            try:
                restaurant_user = request.user.restaurant_user
                request.restaurant = restaurant_user.restaurant
                request.user_role = restaurant_user.role
            except Exception:
                # User doesn't have a RestaurantUser profile
                pass

        response = self.get_response(request)
        return response
