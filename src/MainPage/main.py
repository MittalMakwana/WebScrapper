import functions_framework
import os


@functions_framework.http
def main(request):
    return os.environ.get('TEST')
