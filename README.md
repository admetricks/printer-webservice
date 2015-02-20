# HTML to PDF Web Service

A WSGI web service for rendering HTML to PDF using wkhtmltopdf.

This work was inspired by https://github.com/openlabs/docker-wkhtmltopdf

## TODO

* Add a routing system
* Use URL params to generate wkhtmltopdf cmd-line options
* Add a cache system
* Add a `Procfile` and `.buildpack` for a better Heroku compatibility
* Add an auth system

## Running the Service localy

 1. Install python3 (virtualenv recommendend)

 2. Install `wkhtmltopdf` [here](http://wkhtmltopdf.org/downloads.html)

 3. Install dependencies:

    ```
    pip3 install -r requirements.txt
    ```

 4. Run server:

    ```
    python3 app.py
    ```

The development server listens on port 5000.


## Using the Service

The web service accepts an HTML document as the "html" and "filename" parameter in the body
of a URL-encoded web form POST request and responds with the rendered PDF. For
example:

```sh
curl -d html='<p>Hello world!</p>' -d filename='test.pdf' http://localhost:5000 > output.pdf
```

An HTML file can also be included as multipart form data, for example:

```sh
cat sample.html | curl -F html=@- http://localhost:5000 > output.pdf
```


## Running as Docker Container

To run the service as a Docker container:

 1. Build the Docker image:

    ```sh
    docker build -t printer-webservice .
    ```

 2. Run a Docker container (binding to port 5000):

    ```sh
    docker run -p 5000:8080 printer-webservice
    ```
