import werkzeug

from flask import render_template
from site_package import app


"""Werkzeug main exceptions

BadRequest -- 400
Unauthorized -- 401
Forbidden -- 403
NotFound -- 404
MethodNotAllowed -- 405

InternalServerError -- 500
GatewayTimeout -- 504
"""


@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    context = {
        'title': "400 Error",
        'error_message': "This request shocked server!",
    }

    return render_template('error_template.html', **context), 400


@app.errorhandler(werkzeug.exceptions.Unauthorized)
def handle_bad_request(e):
    context = {
        'title': "401 Error",
        'error_message': "Are you not authorized yet?",
    }

    return render_template('error_template.html', **context), 401


@app.errorhandler(werkzeug.exceptions.Forbidden)
def handle_bad_request(e):
    context = {
        'title': "403 Error",
        'error_message': "It seems like you don't have enough rights :)",
    }

    return render_template('error_template.html', **context), 403


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_bad_request(e):
    context = {
        'title': "404 Error",
        'error_message': "Where are you?",
    }

    return render_template('error_template.html', **context), 404


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def handle_bad_request(e):
    context = {
        'title': "405 Error",
        'error_message': "Method Not Allowed. What are you wanna do?",
    }

    return render_template('error_template.html', **context), 405


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_bad_request(e):
    context = {
        'title': "500 Error",
        'error_message': "Server failed :)",
    }

    return render_template('error_template.html', **context), 500


@app.errorhandler(werkzeug.exceptions.GatewayTimeout)
def handle_bad_request(e):
    context = {
        'title': "504 Error",
        'error_message': "What's with your gateway?",
        'without_home_link': True
    }

    return render_template('error_template.html', **context), 504
