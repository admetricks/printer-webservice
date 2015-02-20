#! /usr/bin/env python
import shutil
import io
from subprocess          import Popen, PIPE
from werkzeug.wsgi       import wrap_file
from werkzeug.exceptions import MethodNotAllowed, BadRequest
from werkzeug.wrappers   import Request, Response

@Request.application
def application(request):
    if is_valid_request(request):
        if is_valid_file_request(request):
            html_file  = request.files['html']
            pdf_file   = generate_pdf(html_file)
            response   = build_response(request, pdf_file)

        elif is_valid_form_request(request):
            html_param = request.form.get('html').encode()
            html_file  = io.BytesIO(html_param)
            file_name  = request.form.get('filename')
            pdf_file   = generate_pdf(html_file)
            response   = build_post_response(request, pdf_file, file_name)

        else:
            response = BadRequest('html and filename params are required')

    else:
        response = BadRequest('Expect a POST request')

    return response


def is_valid_request(request):
    return request.method == 'POST'


def is_valid_form_request(request):
    html_param     = request.form.get('html')
    filename_param = request.form.get('filename')

    return  html_param and filename_param


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
    return ['wkhtmltopdf', '--dpi', '300', '--page-size', 'A4', '--enable-javascript', '--no-stop-slow-scripts', '--javascript-delay', '1000', '-q', '-', '-']


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )
