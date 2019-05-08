#! /usr/bin/env python
import io
import json
import os
import shutil

from subprocess import Popen, PIPE
from urllib.parse import urlparse
from werkzeug.wsgi import wrap_file
from werkzeug.exceptions import MethodNotAllowed, BadRequest
from werkzeug.wrappers import Request, Response


@Request.application
def application(request):
    if request.method == 'OPTIONS' and is_valid_origin(request):
        response = Response()
        response.headers.add(
            'Access-Control-Allow-Origin', request.headers.get('origin'))
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

    if is_valid_request(request):
        data = get_data(request)

        if is_valid_file_request(request):
            html_file = request.files['html']
            pdf_file = generate_pdf(html_file)
            response = build_response(request, pdf_file)

        elif is_valid_post_request(request):
            html_param = data.get('html').encode()
            html_file = io.BytesIO(html_param)
            file_name = data.get('filename')
            pdf_file = generate_pdf(html_file)
            response = build_post_response(request, pdf_file, file_name)

        else:
            response = BadRequest('html and filename params are required')

    else:
        response = MethodNotAllowed(['POST'], 'Expect a POST request')

    return response


def get_data(request):
    return json.loads(request.data) if request.data else request.form


def is_valid_request(request):
    is_valid = request.method == 'POST'
    return is_valid


def is_valid_post_request(request):
    data = get_data(request)
    if not data:
        return False

    html_param = data.get('html')
    filename_param = data.get('filename')
    return html_param and filename_param


def is_valid_origin(request):
    ENV = os.getenv('PRINTER_WHITELIST', '')

    if ENV == '*':
        return True

    if not ENV:
        return False

    return request.headers.get('origin') in [uri.strip() for uri in ENV.split(',')]


def is_valid_file_request(request):
    html_param = request.files.get('html')
    return html_param


def generate_pdf(html_file):
    process = Popen(wkhtmltopdf_cmd(), stdin=PIPE, stdout=PIPE)

    shutil.copyfileobj(html_file, process.stdin)
    process.stdin.close()

    return process.stdout


def build_response(request, pdf_file):
    response = Response(wrap_file(request.environ, pdf_file), content_type="application/pdf")
    return response


def build_post_response(request, pdf_file, file_name):
    response = build_response(request, pdf_file)

    response.headers.add('Content-Disposition', header_filename(file_name))
    response.headers.add('Content-Transfer-Encoding', 'binary')
    response.headers.add(
            'Access-Control-Allow-Origin', request.headers.get('origin'))

    return response


def header_filename(file_name):
    return "attachment; filename={0}".format(file_name)


def wkhtmltopdf_cmd():
    return ['/usr/bin/wkhtmltopdf.sh', '-q', '-d', '300', '-s', 'A4', '-', '-']


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    PORT = os.getenv('PORT', 5000)
    DEBUG = os.getenv('DEBUG', False) == 'True'
    RELOADER = os.getenv('RELOADER', False) == 'True'

    run_simple(
        '127.0.0.1', PORT, application, use_debugger=DEBUG, use_reloader=RELOADER
    )
