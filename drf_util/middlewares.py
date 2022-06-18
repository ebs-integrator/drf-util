from django.conf import settings

from drf_util.utils import Colors


class PrintSQlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        debug_level = getattr(settings, 'DEBUG_LEVEL', None)
        if settings.DEBUG and debug_level and debug_level.lower() == 'debug':
            from django.db import connection
            count = 0
            total_time = float()
            for queries in connection.queries:
                count += 1
                print(f"{Colors.GREEN} sql: {Colors.END} {Colors.WARNING}{queries['sql']} {Colors.END}")
                print(f"{Colors.GREEN} time: {Colors.END} {Colors.WARNING}{queries['time']} {Colors.END}")
                print(f"{Colors.FAIL}---------------------------------------------------{Colors.END}")

                total_time += float(queries['time'])

                if count == len(connection.queries):
                    print()

            if total_time:
                print(f"{Colors.BOLD} Total queries: {count} {Colors.END}")
                print(f"{Colors.BOLD} Total time of execution: {total_time} {Colors.END}\n")
        return response
