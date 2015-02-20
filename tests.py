"""
    html-pdf-webservice

    Copyright 2014 Nathan Jones
    See LICENSE for more details
"""

from unittest.case import TestCase
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from app import application


class AppTest(TestCase):
    def setUp(self):
        self.client = Client(application, BaseResponse)

    def test_post_html_file_should_produce_pdf_response(self):
        response = self.client.post('/', data={'html': open('sample.html')})
        self.assertEquals(200, response.status_code)
        self.assertEquals('application/pdf', response.headers['Content-Type'])

    def test_post_html_file_as_form_param_should_produce_pdf_response(self):
        response = self.client.post('/', data={'html': '<html><body><p>Hello</p></body></html>'})
        self.assertEquals(200, response.status_code)
        self.assertEquals('application/pdf', response.headers['Content-Type'])

    def test_get_request_should_produce_method_not_allowed_response(self):
        response = self.client.get('/')
        self.assertEquals(405, response.status_code)
        self.assertEquals('POST', response.headers['Allow'])

    def test_request_without_file_should_produce_bad_request(self):
        response = self.client.post('/')
        self.assertEquals(400, response.status_code)
        self.assertIn('html is required', response.data)
