"""
    html-pdf-webservice

    Copyright 2014 Nathan Jones
    See LICENSE for more details
"""

import unittest
from io import StringIO
from unittest.case import TestCase
from unittest.mock import patch
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse, Request

from app import application, is_valid_origin


class AppTest(TestCase):
    def setUp(self):
        self.valid_origin = 'http://localhost:8080'
        self.client = Client(application, BaseResponse)
        self.valid_data = {
            'filename': 'testing.pdf',
            'html': '<html><body><p>Hello</p></body></html>'}

    def test_post_html_file_should_produce_pdf_response(self):
        response = self.client.post('/', data={'html': open('sample.html', 'rb')})
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/pdf', response.headers['Content-Type'])

    def test_post_html_file_as_form_param_should_produce_pdf_response(self):
        response = self.client.post('/', data=self.valid_data)
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/pdf', response.headers['Content-Type'])

    def test_get_request_should_produce_method_not_allowed_response(self):
        response = self.client.get('/')
        self.assertEqual(405, response.status_code)
        self.assertEqual('POST', response.headers['Allow'])

    def test_request_without_file_should_produce_bad_request(self):
        response = self.client.post('/')
        self.assertEqual(400, response.status_code)
        self.assertIn('html and filename params are required', str(response.data, 'utf-8'))

    def test_valid_origin(self):
        with patch.dict('os.environ', {'PRINTER_WHITELIST': self.valid_origin}):
            # config client to post with another origin
            response = self.client.options('/', data=self.valid_data, headers={'origin': self.valid_origin})
            self.assertEqual(200, response.status_code)

    def test_invalid_origin(self):
        with patch.dict('os.environ', {'PRINTER_WHITELIST': 'http://github.com'}):
            # config client to post with another origin
            response = self.client.options('/', data=self.valid_data, headers={'origin': self.valid_origin})
            self.assertEqual(405, response.status_code)


if __name__ == '__main__':
    unittest.main()
