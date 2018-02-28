#encoding=utf-8

from application import app
from flask import render_template, make_response, send_from_directory
import os

@app.route('/mobile')
def mobile():
    return render_template('mobile/index.html')

@app.route('/apps')
def apps():
    site_info = {
        'title':'app下载'
    }
    url_args = {
        
    }
    return render_template('download.html', site_info = site_info, url_args = url_args)


@app.route('/download/<filename>')
def download(filename):
    app.logger.debug(os.getcwd())
    response = make_response(send_from_directory(os.getcwd() + '/download/app/', filename, as_attachment = True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('utf-8'))
    return response