#! /usr/bin/env python
import io
import json
import shutil

from subprocess import Popen, PIPE
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
        response = BadRequest('Expect a POST request')

    return response


def get_data(request):
    if request.form.get('filename'):
        return request.form
    else:
        data = json.loads(request.data)
        if data.get('filename'):
            return data
    return None


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
    origin = request.headers.get('origin')

    if origin == 'https://localhost:3100' or origin == "http://localhost:3100":
        return True

    # if origin includes "web.admetricks.com"

    return False


def is_valid_file_request(request):
    html_param = request.files.get('html')
    return html_param


def generate_pdf(html_file):
    process = Popen(wkhtmltopdf_cmd(), stdin=PIPE, stdout=PIPE)

    shutil.copyfileobj(html_file, process.stdin)
    process.stdin.close()

    return process.stdout


def build_response(request, pdf_file):
    response = Response(wrap_file(request.environ, pdf_file))

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('content-type', 'application/pdf')

    return response


def build_post_response(request, pdf_file, file_name):
    response = build_response(request, pdf_file)

    response.headers.add('Content-Disposition', header_filename(file_name))
    response.headers.add('Content-Transfer-Encoding', 'binary')

    return response


def header_filename(file_name):
    return "attachment; filename={0}".format(file_name)


def wkhtmltopdf_cmd():
    return ['/usr/bin/wkhtmltopdf.sh', '-q', '-d', '300', '-s', 'A4', '-', '-']


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )
