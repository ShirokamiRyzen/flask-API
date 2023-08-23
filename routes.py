from flask import (Flask, request, jsonify, redirect, url_for, make_response,
                   render_template, send_from_directory, Response, send_file)

from youtubesearchpython import Search, PlaylistsSearch
from flask_caching import Cache
from flask_cors import CORS, cross_origin
import requests, random, time, urllib, traceback, re, urllib3, socket
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
from datetime import datetime, timedelta
import config as conf
import utils, os, threading, glob
from utils import *
from markupsafe import escape

app = Flask(__name__)
cors = CORS(app)

DOWNLOAD_DIR = "./downloads"


def delete_files():
  current_time = time.time()
  for file in os.listdir(DOWNLOAD_DIR):
    file_path = os.path.join(DOWNLOAD_DIR, file)
    if os.path.isfile(
        file_path) and current_time - os.path.getctime(file_path) > 1800:
      os.remove(file_path)


app.config["CORS_HEADERS"] = "Content-Type"
app.config["TEMPLATES_AUTO_RELOAD"] = conf.AUTO_RELOAD
cache = Cache(app,
              config={
                "CACHE_TYPE": "simple",
                "CACHE_DEFAULT_TIMEOUT": 3600
              })


@cache.memoize()
def get_user_agents():
  with open("user_agents.txt", "r") as f:
    return [line.strip() for line in f.readlines()]


# def generate_visitor_id():
#   timestamp = str(time.time())
#   md5_hash = hashlib.md5(timestamp.encode()).hexdigest()
#   return md5_hash

# def generate_cookie(visitor_id):
#   timestamp = str(time.time())
#   sha1_hash = hashlib.sha1((timestamp + visitor_id).encode()).hexdigest()
#   return sha1_hash


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(503)
@app.errorhandler(504)
def handle_errors(error):
  return redirect(url_for("index"))


@app.route("/")
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def index():
  visitor_id = generate_visitor_id()
  cookie = generate_cookie(visitor_id)
  # Mendapatkan tanggal saat ini
  current_date = datetime.now()

  # Menghitung tanggal kadaluwarsa (7 hari dari tanggal saat ini)
  expiration_date = current_date + timedelta(days=7)

  response = make_response(render_template("index.jinja2", configs=conf))
  response.set_cookie(visitor_id,
                      value=cookie,
                      expires=expiration_date,
                      samesite="None",
                      secure=True)
  return response


@app.route("/robots.txt")
def robots_txt():
  return '''User-agent: *<br />Disallow: <br /><br />Sitemap: https://tr.deployers.repl.co/sitemap.xml
'''


@app.route('/apk/<filename>', methods=['GET'])
def download_apk(filename):
  # Replace 'path_to_apk_folder' with the actual path to the folder containing the APK file
  apk_folder = 'apk'
  file_path = f'{apk_folder}/{filename}'

  try:
    return send_file(file_path, as_attachment=True)
  except Exception as e:
    return str(e), 404


@app.route('/images')
def get_image():
  image_path = 'dana/dana.webp'  # Replace 'data/dana.jpg' with the actual path to your image file
  return send_file(image_path, mimetype='image/jpeg')


# @app.route('/sitemap.xml')
# def generate_sitemap():
# sitemap_content = generate_sitemap_content()

# response = Response(sitemap_content, mimetype='text/xml')
# response.headers['Content-Disposition'] = 'attachment; filename=sitemap.xml'
# return response


def generate_sitemap_content():
  xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<!-- created with Free Online Sitemap Generator www.xml-sitemaps.com -->

<url>
  <loc>https://tr.deployers.repl.co/</loc>
  <lastmod>2023-07-31T23:52:46+00:00</lastmod>
  <priority>1.00</priority>
</url>
<url>
  <loc>https://tr.deployers.repl.co/donasi</loc>
  <lastmod>2023-07-31T23:52:46+00:00</lastmod>
  <priority>0.80</priority>
</url>
<url>
  <loc>https://tr.deployers.repl.co/zerogpt</loc>
  <lastmod>2023-07-31T23:52:46+00:00</lastmod>
  <priority>0.80</priority>
</url>

<loc>https://tr.deployers.repl.co/downloadapk</loc>
  <lastmod>2023-08-14T23:52:46+00:00</lastmod>
  <priority>0.80</priority>
</url>

</urlset>
  '''
  # xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
  # xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
  # xml_content += '    <url>\n'
  # xml_content += '        <loc>https://tr.deployers.repl.co</loc>\n'
  # xml_content += f'        <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
  # xml_content += '        <changefreq>weekly</changefreq>\n'
  # xml_content += '        <priority>1.0</priority>\n'  # Set priority to 1.0 for high
  # xml_content += '    </url>\n'
  # xml_content += '</urlset>'

  return xml_content


@app.route('/sitemap.xml')
def generate_sitemap():
  xml_content = generate_sitemap_content()
  response = Response(xml_content, content_type='application/xml')
  return response


@app.route('/donasi')
def donasi():
  return '''
<!doctype html>
<html lang=en>
<head>
<script>document.write(unescape("%3C%6D%65%74%61%20%63%68%61%72%73%65%74%3D%55%54%46%2D%38%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%76%69%65%77%70%6F%72%74%20%63%6F%6E%74%65%6E%74%3D%22%77%69%64%74%68%3D%64%65%76%69%63%65%2D%77%69%64%74%68%2C%69%6E%69%74%69%61%6C%2D%73%63%61%6C%65%3D%31%22%3E%0A%3C%74%69%74%6C%65%3E%44%6F%6E%61%73%69%20%75%6E%74%75%6B%20%50%72%6F%67%72%61%6D%6D%65%72%3C%2F%74%69%74%6C%65%3E%0A%3C%73%63%72%69%70%74%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%63%64%6E%2E%6A%73%64%65%6C%69%76%72%2E%6E%65%74%2F%6E%70%6D%2F%73%77%65%65%74%61%6C%65%72%74%32%40%31%31%3E%3C%2F%73%63%72%69%70%74%3E%0A%3C%6C%69%6E%6B%20%72%65%6C%3D%69%63%6F%6E%20%68%72%65%66%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%74%69%74%6C%65%20%63%6F%6E%74%65%6E%74%3D%44%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%64%65%73%63%72%69%70%74%69%6F%6E%20%63%6F%6E%74%65%6E%74%3D%22%42%65%72%6B%6F%6E%74%72%69%62%75%73%69%20%64%65%6E%67%61%6E%20%64%6F%6E%61%73%69%20%75%6E%74%75%6B%20%70%65%6D%69%6C%69%6B%20%73%65%72%76%65%72%20%61%74%61%75%20%77%65%62%73%69%74%65%20%74%72%2E%64%65%70%6C%6F%79%65%72%2E%72%65%70%6C%2E%63%6F%20%79%61%6E%67%20%6D%65%6D%62%65%72%69%6B%61%6E%20%41%50%49%20%67%72%61%74%69%73%2C%20%6B%75%6E%6A%75%6E%67%69%20%68%61%6C%61%6D%61%6E%20%69%6E%69%20%73%65%6B%61%72%61%6E%67%2E%22%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%6B%65%79%77%6F%72%64%73%20%63%6F%6E%74%65%6E%74%3D%22%64%6F%6E%61%73%69%2C%61%70%69%2C%64%65%76%65%6C%6F%70%65%72%2C%70%72%6F%67%72%61%6D%6D%69%6E%67%2C%70%72%6F%67%72%61%6D%6D%65%72%2C%67%69%74%68%75%62%2C%6F%70%65%6E%73%6F%75%72%63%65%2C%6F%70%65%6E%20%73%6F%75%72%63%65%2C%73%65%6F%22%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%72%6F%62%6F%74%73%20%63%6F%6E%74%65%6E%74%3D%22%69%6E%64%65%78%2C%20%66%6F%6C%6C%6F%77%22%3E%0A%3C%6D%65%74%61%20%68%74%74%70%2D%65%71%75%69%76%3D%43%6F%6E%74%65%6E%74%2D%54%79%70%65%20%63%6F%6E%74%65%6E%74%3D%22%74%65%78%74%2F%68%74%6D%6C%3B%20%63%68%61%72%73%65%74%3D%75%74%66%2D%38%22%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%6C%61%6E%67%75%61%67%65%20%63%6F%6E%74%65%6E%74%3D%45%6E%67%6C%69%73%68%3E%0A%3C%6D%65%74%61%20%6E%61%6D%65%3D%61%75%74%68%6F%72%20%63%6F%6E%74%65%6E%74%3D%58%6E%75%76%65%72%73%30%30%37%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%74%79%70%65%20%63%6F%6E%74%65%6E%74%3D%77%65%62%73%69%74%65%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%75%72%6C%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%64%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%74%69%74%6C%65%20%63%6F%6E%74%65%6E%74%3D%44%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%64%65%73%63%72%69%70%74%69%6F%6E%20%63%6F%6E%74%65%6E%74%3D%22%42%65%72%6B%6F%6E%74%72%69%62%75%73%69%20%64%65%6E%67%61%6E%20%64%6F%6E%61%73%69%20%75%6E%74%75%6B%20%70%65%6D%69%6C%69%6B%20%73%65%72%76%65%72%20%61%74%61%75%20%77%65%62%73%69%74%65%20%74%72%2E%64%65%70%6C%6F%79%65%72%2E%72%65%70%6C%2E%63%6F%20%79%61%6E%67%20%6D%65%6D%62%65%72%69%6B%61%6E%20%41%50%49%20%67%72%61%74%69%73%2C%20%6B%75%6E%6A%75%6E%67%69%20%68%61%6C%61%6D%61%6E%20%69%6E%69%20%73%65%6B%61%72%61%6E%67%2E%22%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%6F%67%3A%69%6D%61%67%65%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%63%61%72%64%20%63%6F%6E%74%65%6E%74%3D%73%75%6D%6D%61%72%79%5F%6C%61%72%67%65%5F%69%6D%61%67%65%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%75%72%6C%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%64%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%74%69%74%6C%65%20%63%6F%6E%74%65%6E%74%3D%44%6F%6E%61%73%69%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%64%65%73%63%72%69%70%74%69%6F%6E%20%63%6F%6E%74%65%6E%74%3D%22%42%65%72%6B%6F%6E%74%72%69%62%75%73%69%20%64%65%6E%67%61%6E%20%64%6F%6E%61%73%69%20%75%6E%74%75%6B%20%70%65%6D%69%6C%69%6B%20%73%65%72%76%65%72%20%61%74%61%75%20%77%65%62%73%69%74%65%20%74%72%2E%64%65%70%6C%6F%79%65%72%2E%72%65%70%6C%2E%63%6F%20%79%61%6E%67%20%6D%65%6D%62%65%72%69%6B%61%6E%20%41%50%49%20%67%72%61%74%69%73%2C%20%6B%75%6E%6A%75%6E%67%69%20%68%61%6C%61%6D%61%6E%20%69%6E%69%20%73%65%6B%61%72%61%6E%67%2E%22%3E%0A%3C%6D%65%74%61%20%70%72%6F%70%65%72%74%79%3D%74%77%69%74%74%65%72%3A%69%6D%61%67%65%20%63%6F%6E%74%65%6E%74%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%3E%0A%3C%73%74%79%6C%65%3E%62%6F%64%79%7B%66%6F%6E%74%2D%66%61%6D%69%6C%79%3A%41%72%69%61%6C%2C%73%61%6E%73%2D%73%65%72%69%66%3B%6D%61%72%67%69%6E%3A%30%3B%70%61%64%64%69%6E%67%3A%30%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%37%66%37%66%37%7D%2E%63%6F%6E%74%61%69%6E%65%72%7B%6D%61%78%2D%77%69%64%74%68%3A%36%30%30%70%78%3B%6D%61%72%67%69%6E%3A%35%30%70%78%20%61%75%74%6F%3B%70%61%64%64%69%6E%67%3A%32%30%70%78%3B%62%6F%72%64%65%72%3A%31%70%78%20%73%6F%6C%69%64%20%23%63%63%63%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%35%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%66%66%7D%2E%6C%6F%67%6F%2D%77%72%61%70%70%65%72%7B%64%69%73%70%6C%61%79%3A%66%6C%65%78%3B%66%6C%65%78%2D%64%69%72%65%63%74%69%6F%6E%3A%63%6F%6C%75%6D%6E%3B%61%6C%69%67%6E%2D%69%74%65%6D%73%3A%63%65%6E%74%65%72%3B%6D%61%72%67%69%6E%2D%62%6F%74%74%6F%6D%3A%32%30%70%78%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%7B%70%6F%73%69%74%69%6F%6E%3A%72%65%6C%61%74%69%76%65%3B%77%69%64%74%68%3A%32%30%30%70%78%3B%68%65%69%67%68%74%3A%32%30%30%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%30%66%30%66%30%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%35%30%25%3B%6F%76%65%72%66%6C%6F%77%3A%68%69%64%64%65%6E%3B%63%75%72%73%6F%72%3A%70%6F%69%6E%74%65%72%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%20%69%6D%67%7B%77%69%64%74%68%3A%31%30%30%25%3B%68%65%69%67%68%74%3A%31%30%30%25%3B%6F%62%6A%65%63%74%2D%66%69%74%3A%63%6F%76%65%72%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%32%7B%70%6F%73%69%74%69%6F%6E%3A%72%65%6C%61%74%69%76%65%3B%77%69%64%74%68%3A%32%30%30%70%78%3B%68%65%69%67%68%74%3A%32%30%30%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%30%66%30%66%30%3B%6F%76%65%72%66%6C%6F%77%3A%68%69%64%64%65%6E%3B%63%75%72%73%6F%72%3A%70%6F%69%6E%74%65%72%7D%2E%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%32%20%69%6D%67%7B%77%69%64%74%68%3A%31%30%30%25%3B%68%65%69%67%68%74%3A%31%30%30%25%3B%6F%62%6A%65%63%74%2D%66%69%74%3A%63%6F%76%65%72%7D%2E%68%69%64%64%65%6E%2D%6C%69%6E%6B%7B%70%6F%73%69%74%69%6F%6E%3A%61%62%73%6F%6C%75%74%65%3B%74%6F%70%3A%30%3B%6C%65%66%74%3A%30%3B%77%69%64%74%68%3A%31%30%30%25%3B%68%65%69%67%68%74%3A%31%30%30%25%3B%70%6F%69%6E%74%65%72%2D%65%76%65%6E%74%73%3A%6E%6F%6E%65%7D%2E%74%69%74%6C%65%7B%66%6F%6E%74%2D%73%69%7A%65%3A%32%34%70%78%3B%66%6F%6E%74%2D%77%65%69%67%68%74%3A%37%30%30%3B%63%6F%6C%6F%72%3A%23%33%33%33%3B%6D%61%72%67%69%6E%2D%74%6F%70%3A%31%30%70%78%7D%2E%66%6F%6F%74%65%72%7B%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3B%66%6F%6E%74%2D%73%69%7A%65%3A%32%30%70%78%3B%63%6F%6C%6F%72%3A%23%30%30%30%3B%6D%61%72%67%69%6E%2D%62%6F%74%74%6F%6D%3A%31%30%70%78%7D%2A%7B%2D%77%65%62%6B%69%74%2D%74%6F%75%63%68%2D%63%61%6C%6C%6F%75%74%3A%6E%6F%6E%65%3B%2D%77%65%62%6B%69%74%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%2D%6B%68%74%6D%6C%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%2D%6D%6F%7A%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%2D%6D%73%2D%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%3B%75%73%65%72%2D%73%65%6C%65%63%74%3A%6E%6F%6E%65%7D%3C%2F%73%74%79%6C%65%3E"))</script>
</head>
<body>
<script>document.write(unescape("%3C%64%69%76%20%63%6C%61%73%73%3D%63%6F%6E%74%61%69%6E%65%72%3E%0A%3C%68%31%20%73%74%79%6C%65%3D%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3E%44%6F%6E%61%73%69%20%75%6E%74%75%6B%20%53%61%79%61%3C%2F%68%31%3E%0A%3C%70%3E%54%65%72%69%6D%61%20%6B%61%73%69%68%20%74%65%6C%61%68%20%6D%65%6E%67%67%75%6E%61%6B%61%6E%20%77%65%62%73%69%74%65%20%41%50%49%20%6B%61%6D%69%2E%20%4A%69%6B%61%20%41%6E%64%61%20%6D%65%72%61%73%61%20%74%65%72%62%61%6E%74%75%2C%20%41%6E%64%61%20%64%61%70%61%74%20%6D%65%6D%62%65%72%69%6B%61%6E%20%64%6F%6E%61%73%69%20%73%65%62%61%67%61%69%20%64%75%6B%75%6E%67%61%6E%2E%3C%2F%70%3E%0A%3C%70%3E%44%6F%6E%61%73%69%20%41%6E%64%61%20%61%6B%61%6E%20%6D%65%6D%62%61%6E%74%75%20%6B%61%6D%69%20%75%6E%74%75%6B%20%74%65%72%75%73%20%6D%65%6E%69%6E%67%6B%61%74%6B%61%6E%20%6C%61%79%61%6E%61%6E%20%6B%61%6D%69%2E%20%54%65%6B%61%6E%20%67%61%6D%62%61%72%20%61%67%61%72%20%6D%65%6E%75%6A%75%20%6B%65%20%70%65%6D%62%61%79%61%72%61%6E%20%28%4B%65%63%75%61%6C%69%20%44%61%6E%61%29%3C%2F%70%3E%3C%62%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%77%72%61%70%70%65%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%74%69%74%6C%65%3E%53%61%77%65%72%69%61%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%20%6F%6E%63%6C%69%63%6B%3D%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%31%28%29%3E%0A%3C%69%6D%67%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%68%46%78%57%54%31%70%2F%65%7A%67%69%66%2D%32%2D%66%38%36%36%63%66%34%35%30%39%2E%77%65%62%70%20%61%6C%74%3D%22%4C%6F%67%6F%20%50%65%6D%62%61%79%61%72%61%6E%20%53%61%77%65%72%69%61%22%3E%0A%3C%61%20%63%6C%61%73%73%3D%68%69%64%64%65%6E%2D%6C%69%6E%6B%3E%3C%2F%61%3E%0A%3C%2F%64%69%76%3E%0A%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%77%72%61%70%70%65%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%74%69%74%6C%65%3E%44%61%6E%61%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%32%3E%0A%3C%69%6D%67%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%69%6D%61%67%65%73%20%61%6C%74%3D%22%4C%6F%67%6F%20%50%65%6D%62%61%79%61%72%61%6E%20%44%61%6E%61%22%3E%0A%3C%2F%64%69%76%3E%0A%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%77%72%61%70%70%65%72%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%74%69%74%6C%65%3E%54%72%61%6B%74%65%65%72%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%6C%6F%67%6F%2D%63%6F%6E%74%61%69%6E%65%72%20%6F%6E%63%6C%69%63%6B%3D%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%32%28%29%3E%0A%3C%69%6D%67%20%73%72%63%3D%68%74%74%70%73%3A%2F%2F%69%2E%69%62%62%2E%63%6F%2F%53%66%4B%53%4E%4E%73%2F%65%7A%67%69%66%2D%32%2D%62%39%64%32%61%32%39%65%65%65%2E%77%65%62%70%20%61%6C%74%3D%22%4C%6F%67%6F%20%50%65%6D%62%61%79%61%72%61%6E%20%54%72%61%6B%74%65%65%72%22%3E%0A%3C%61%20%63%6C%61%73%73%3D%68%69%64%64%65%6E%2D%6C%69%6E%6B%3E%3C%2F%61%3E%0A%3C%2F%64%69%76%3E%0A%3C%2F%64%69%76%3E%0A%3C%62%72%3E%0A%3C%70%20%73%74%79%6C%65%3D%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3B%66%6F%6E%74%2D%77%65%69%67%68%74%3A%62%6F%6C%64%65%72%3B%66%6F%6E%74%2D%73%69%7A%65%3A%31%37%70%78%3E%54%45%52%49%4D%41%4B%41%53%49%48%20%61%74%61%73%20%73%65%62%65%73%61%72%20%62%65%73%61%72%6E%79%61%20%64%61%72%69%20%64%6F%6E%61%73%69%20%79%61%6E%67%20%61%6E%64%61%20%62%65%72%69%6B%61%6E%2C%20%62%65%73%61%72%20%61%74%61%75%20%6B%65%63%69%6C%2E%20%74%65%74%61%70%20%62%65%72%68%61%72%67%61%20%64%69%6D%61%74%61%20%73%61%79%61%2E%20%53%65%6B%61%6C%69%20%6C%61%67%69%2C%20%54%45%52%49%4D%41%4B%41%53%49%48%20%3C%2F%70%3E%0A%3C%2F%64%69%76%3E%0A%3C%64%69%76%20%63%6C%61%73%73%3D%66%6F%6F%74%65%72%20%73%74%79%6C%65%3D%66%6F%6E%74%2D%77%65%69%67%68%74%3A%62%6F%6C%64%65%72%3E%0A%26%63%6F%70%79%3B%20%32%30%32%33%20%58%6E%75%76%65%72%73%30%30%37%20%41%50%49%20%28%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%29%2E%20%41%6C%6C%20%72%69%67%68%74%73%20%72%65%73%65%72%76%65%64%2E%0A%3C%2F%64%69%76%3E%0A%3C%73%63%72%69%70%74%3E%66%75%6E%63%74%69%6F%6E%20%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%31%28%29%7B%76%61%72%20%65%3D%61%74%6F%62%28%22%61%48%52%30%63%48%4D%36%4C%79%39%7A%59%58%64%6C%63%6D%6C%68%4C%6D%4E%76%4C%33%68%75%64%58%5A%6C%63%6E%4D%77%4D%44%63%22%29%3B%77%69%6E%64%6F%77%2E%6F%70%65%6E%28%65%2C%22%5F%62%6C%61%6E%6B%22%2C%22%6E%6F%6F%70%65%6E%65%72%2C%6E%6F%72%65%66%65%72%72%65%72%22%29%7D%66%75%6E%63%74%69%6F%6E%20%72%65%64%69%72%65%63%74%54%6F%44%6F%6E%61%74%69%6F%6E%50%61%67%65%32%28%29%7B%76%61%72%20%65%3D%61%74%6F%62%28%22%61%48%52%30%63%48%4D%36%4C%79%39%30%63%6D%46%72%64%47%56%6C%63%69%35%70%5A%43%39%34%62%6E%56%32%5A%58%4A%7A%4D%44%41%33%22%29%3B%77%69%6E%64%6F%77%2E%6F%70%65%6E%28%65%2C%22%5F%62%6C%61%6E%6B%22%2C%22%6E%6F%6F%70%65%6E%65%72%2C%6E%6F%72%65%66%65%72%72%65%72%22%29%7D%66%75%6E%63%74%69%6F%6E%20%73%68%6F%77%45%72%72%6F%72%28%29%7B%53%77%61%6C%2E%66%69%72%65%28%7B%69%63%6F%6E%3A%22%65%72%72%6F%72%22%2C%74%69%74%6C%65%3A%22%4F%6F%70%73%2E%2E%2E%22%2C%74%65%78%74%3A%22%43%6C%69%63%6B%69%6E%67%20%6F%6E%20%74%68%65%20%6C%6F%67%6F%20%69%73%20%64%69%73%61%62%6C%65%64%20%66%6F%72%20%73%65%63%75%72%69%74%79%20%72%65%61%73%6F%6E%73%2F%52%69%67%68%74%20%43%6C%69%63%6B%20%64%69%73%61%62%6C%65%64%2E%20%50%6C%65%61%73%65%20%75%73%65%20%74%68%65%20%70%72%6F%76%69%64%65%64%20%6C%69%6E%6B%20%74%6F%20%6D%61%6B%65%20%61%20%64%6F%6E%61%74%69%6F%6E%2E%20%54%65%72%69%6D%61%20%6B%61%73%69%68%20%61%74%61%73%20%64%75%6B%75%6E%67%61%6E%6E%79%61%21%22%2C%66%6F%6F%74%65%72%3A%27%3C%61%20%68%72%65%66%3D%22%2F%22%3E%47%6F%20%54%6F%20%49%6E%64%65%78%3C%2F%61%3E%27%7D%29%7D%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%6F%6E%74%65%78%74%6D%65%6E%75%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%2C%73%68%6F%77%45%72%72%6F%72%28%29%7D%29%29%3C%2F%73%63%72%69%70%74%3E"))</script>
</body>
</html>
'''


@app.route('/downloadapk')
def aplikasi():
  return '''<!doctype html><html lang=en><head><title>Download APK</title><script>document.write(unescape("%3C%6D%65%74%61%20%63%68%61%72%73%65%74%3D%55%54%46%2D%38%3E%3C%6D%65%74%61%20%6E%61%6D%65%3D%76%69%65%77%70%6F%72%74%20%63%6F%6E%74%65%6E%74%3D%22%77%69%64%74%68%3D%64%65%76%69%63%65%2D%77%69%64%74%68%2C%69%6E%69%74%69%61%6C%2D%73%63%61%6C%65%3D%31%22%3E%3C%73%74%79%6C%65%3E%62%6F%64%79%7B%66%6F%6E%74%2D%66%61%6D%69%6C%79%3A%41%72%69%61%6C%2C%73%61%6E%73%2D%73%65%72%69%66%3B%64%69%73%70%6C%61%79%3A%66%6C%65%78%3B%6A%75%73%74%69%66%79%2D%63%6F%6E%74%65%6E%74%3A%63%65%6E%74%65%72%3B%61%6C%69%67%6E%2D%69%74%65%6D%73%3A%63%65%6E%74%65%72%3B%68%65%69%67%68%74%3A%31%30%30%76%68%3B%6D%61%72%67%69%6E%3A%30%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%34%66%34%66%34%7D%2E%63%6F%6E%74%61%69%6E%65%72%7B%74%65%78%74%2D%61%6C%69%67%6E%3A%63%65%6E%74%65%72%3B%62%6F%72%64%65%72%3A%32%70%78%20%73%6F%6C%69%64%20%23%63%63%63%3B%70%61%64%64%69%6E%67%3A%32%30%70%78%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%31%30%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%66%66%66%3B%62%6F%78%2D%73%68%61%64%6F%77%3A%30%20%30%20%31%30%70%78%20%72%67%62%61%28%30%2C%30%2C%30%2C%2E%31%29%7D%2E%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%7B%64%69%73%70%6C%61%79%3A%69%6E%6C%69%6E%65%2D%62%6C%6F%63%6B%3B%70%61%64%64%69%6E%67%3A%31%30%70%78%20%32%30%70%78%3B%66%6F%6E%74%2D%73%69%7A%65%3A%31%38%70%78%3B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%30%30%37%62%66%66%3B%63%6F%6C%6F%72%3A%23%66%66%66%3B%62%6F%72%64%65%72%3A%6E%6F%6E%65%3B%62%6F%72%64%65%72%2D%72%61%64%69%75%73%3A%35%70%78%3B%63%75%72%73%6F%72%3A%70%6F%69%6E%74%65%72%3B%74%72%61%6E%73%69%74%69%6F%6E%3A%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%20%2E%33%73%2C%74%72%61%6E%73%66%6F%72%6D%20%2E%33%73%7D%2E%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%3A%68%6F%76%65%72%7B%62%61%63%6B%67%72%6F%75%6E%64%2D%63%6F%6C%6F%72%3A%23%30%30%35%36%62%33%7D%2E%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%2E%61%6E%69%6D%61%74%65%7B%74%72%61%6E%73%66%6F%72%6D%3A%73%63%61%6C%65%28%31%2E%31%29%7D%2E%73%65%72%76%65%72%2D%73%65%6C%65%63%74%69%6F%6E%7B%6D%61%72%67%69%6E%2D%74%6F%70%3A%32%30%70%78%7D%3C%2F%73%74%79%6C%65%3E"))</script></head><body><script>document.write(unescape("%3C%64%69%76%20%63%6C%61%73%73%3D%63%6F%6E%74%61%69%6E%65%72%3E%3C%68%31%3E%55%6E%64%75%68%20%41%70%6C%69%6B%61%73%69%20%4B%61%6D%69%3C%2F%68%31%3E%3C%70%3E%50%69%6C%69%68%20%73%65%72%76%65%72%20%75%6E%64%75%68%61%6E%3A%3C%2F%70%3E%3C%64%69%76%20%63%6C%61%73%73%3D%73%65%72%76%65%72%2D%73%65%6C%65%63%74%69%6F%6E%3E%3C%62%75%74%74%6F%6E%20%63%6C%61%73%73%3D%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%20%6F%6E%63%6C%69%63%6B%3D%27%64%6F%77%6E%6C%6F%61%64%41%70%70%28%22%73%65%72%76%65%72%31%22%29%27%3E%53%65%72%76%65%72%20%31%3C%2F%62%75%74%74%6F%6E%3E%20%20%20%20%26%6E%62%73%70%3B%26%6E%62%73%70%3B%26%6E%62%73%70%3B%3C%62%75%74%74%6F%6E%20%63%6C%61%73%73%3D%64%6F%77%6E%6C%6F%61%64%2D%62%74%6E%20%6F%6E%63%6C%69%63%6B%3D%27%64%6F%77%6E%6C%6F%61%64%41%70%70%28%22%73%65%72%76%65%72%32%22%29%27%3E%53%65%72%76%65%72%20%32%3C%2F%62%75%74%74%6F%6E%3E%3C%2F%64%69%76%3E%3C%2F%64%69%76%3E%3C%73%63%72%69%70%74%3E%66%75%6E%63%74%69%6F%6E%20%61%6E%69%6D%61%74%65%42%75%74%74%6F%6E%28%65%29%7B%65%2E%63%6C%61%73%73%4C%69%73%74%2E%61%64%64%28%22%61%6E%69%6D%61%74%65%22%29%2C%73%65%74%54%69%6D%65%6F%75%74%28%28%28%29%3D%3E%7B%65%2E%63%6C%61%73%73%4C%69%73%74%2E%72%65%6D%6F%76%65%28%22%61%6E%69%6D%61%74%65%22%29%7D%29%2C%33%30%30%29%7D%66%75%6E%63%74%69%6F%6E%20%64%6F%77%6E%6C%6F%61%64%41%70%70%28%65%29%7B%6C%65%74%20%74%3B%61%6E%69%6D%61%74%65%42%75%74%74%6F%6E%28%65%76%65%6E%74%2E%74%61%72%67%65%74%29%2C%22%73%65%72%76%65%72%31%22%3D%3D%3D%65%3F%74%3D%22%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%61%70%6B%2F%41%50%49%25%32%30%58%6E%75%76%65%72%73%30%30%37%2D%31%2E%61%70%6B%22%3A%22%73%65%72%76%65%72%32%22%3D%3D%3D%65%26%26%28%74%3D%22%68%74%74%70%73%3A%2F%2F%74%72%2E%64%65%70%6C%6F%79%65%72%73%2E%72%65%70%6C%2E%63%6F%2F%61%70%6B%2F%41%50%49%25%32%30%58%6E%75%76%65%72%73%30%30%37%2D%32%2E%61%70%6B%22%29%2C%77%69%6E%64%6F%77%2E%6F%70%65%6E%28%74%2C%22%5F%62%6C%61%6E%6B%22%29%7D%3C%2F%73%63%72%69%70%74%3E"))</script><script>document.write(unescape("%3C%73%63%72%69%70%74%3E%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%6B%65%79%64%6F%77%6E%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%63%74%72%6C%4B%65%79%26%26%22%75%22%3D%3D%3D%65%2E%6B%65%79%26%26%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%6F%6E%74%65%78%74%6D%65%6E%75%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%73%65%6C%65%63%74%73%74%61%72%74%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%64%72%61%67%73%74%61%72%74%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%75%74%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%63%6F%70%79%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%2C%64%6F%63%75%6D%65%6E%74%2E%61%64%64%45%76%65%6E%74%4C%69%73%74%65%6E%65%72%28%22%70%61%73%74%65%22%2C%28%66%75%6E%63%74%69%6F%6E%28%65%29%7B%65%2E%70%72%65%76%65%6E%74%44%65%66%61%75%6C%74%28%29%7D%29%29%3C%2F%73%63%72%69%70%74%3E"))</script></body></html>'''


@app.route("/indonesia", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_berita():
  num_articles = int(request.args.get(
    "berita",
    "5"))  # Get the 'j' query parameter from the URL, defaulting to 5
  url = "https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE55ZVc0U0FtbGtLQUFQAQ?hl=id&gl=ID&ceid=ID%3Aid"
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("c-wiz", attrs={"class": "PIlOad"})
  titles = []
  links = []
  images = []
  for item in test:
    for img in item.find_all("figure", attrs={"class": "K0q4G P22Vib"}):
      images.append(img.find("img")["src"])
    for teks in item.find_all("h4", attrs={"class": "gPFEn"}):
      titles.append(teks.text)
    for link in item.find_all("a"):
      href = link.get("href")
      absolute_url = urljoin("https://news.google.com/", href)
      if "/stories/" not in absolute_url:
        links.append(absolute_url)
  berita_list = []
  for title, link, gambar in zip(titles, links, images):
    berita_list.append({
      "Berita": title,
      "Gambar": gambar,
      "Link Berita": link
    })
    if len(berita_list) == num_articles:
      break
  return jsonify(berita_list)


@app.route("/world", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_berita_world():
  num_articles = int(request.args.get(
    "news", "5"))  # Get the 'j' query parameter from the URL, defaulting to 5
  url = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtbGtHZ0pKUkNnQVAB?hl=id&gl=ID&ceid=ID:id"
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("c-wiz", attrs={"class": "PIlOad"})
  titles = []
  links = []
  images = []
  for item in test:
    for img in item.find_all("figure", attrs={"class": "K0q4G P22Vib"}):
      images.append(img.find("img")["src"])
    for teks in item.find_all("h4", attrs={"class": "gPFEn"}):
      titles.append(teks.text)
    for link in item.find_all("a"):
      href = link.get("href")
      absolute_url = urljoin("https://news.google.com/", href)
      if "/stories/" not in absolute_url:
        links.append(absolute_url)
  berita_list = []
  for title, link, gambar in zip(titles, links, images):
    berita_list.append({"News": title, "Image": gambar, "Link News": link})
    if len(berita_list) == num_articles:
      break
  return jsonify(berita_list)


@app.route("/jam", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_jam():
  wilayah = request.args.get(
    "wilayah", "Jakarta"
  )  # Get the 'wilayah' query parameter from the URL, defaulting to 'Jakarta'
  url = "https://time.is/id/" + wilayah
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("div", attrs={"id": "clock0_bg"})
  for jams in test:
    jam = jams.find("time", attrs={"id": "clock"}).text
  return jsonify({
    "Jam": jam,
    "wilayah": wilayah,
    "Author": "Xnuvers007 [ https://github.com/Xnuvers007 ]",
  })


@app.route("/bp", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_bp():
  # i want it like this localhost:5000/bp?tensi=125&hb=91
  tensi = int(request.args.get("tensi", "125"))
  hb = int(request.args.get("hb", "91"))
  url = "https://foenix.com/BP/is-{0}/{1}-good-blood-pressure-or-high-blood-pressure.html".format(
    tensi, hb)
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  test = soup.find_all("div", attrs={"class": "content"})
  for hasil in test:
    hasil = soup.find_all("b")[15].text

  myhost = f"{request.host_url}bp?tensi={tensi}&hb={hb}"
  return jsonify({
    "Hasil": hasil,
    "Tensi": tensi,
    "Hb": hb,
    "Author": "Xnuvers007 [ Xnuvers007 https://github.com/Xnuvers007 ]",
    "parameter": myhost,
  })


@app.route("/convertuang", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_convertuang():
  uang = int(request.args.get("uang", "1"))
  dari = request.args.get("dari", "IDR")
  ke = request.args.get("ke", "USD")
  url = "https://www.exchange-rates.com/id/{0}/{1}/{2}/".format(uang, dari, ke)
  r = requests.get(url,
                   timeout=5,
                   headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac"})
  soup = BeautifulSoup(r.content, "html.parser")
  for i in soup.find_all("div", class_="fullwidth"):
    for j in i.find_all("div", class_="leftdiv"):
      hasil = j.find_all("p")[2]
      hasil = hasil.text
  return jsonify({
    "Hasil": hasil,
    "Uang": uang,
    "Dari": dari,
    "Ke": ke,
    "Author": "Xnuvers007 [ https://github.com/Xnuvers007 ]",
  })


@app.route("/kamus", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def get_data():
  user_input = request.args.get("text")
  User_agent = UserAgent(browsers=["edge", "chrome", "firefox"])
  headers = {"User-Agent": User_agent.random}

  url = f"https://en.bab.la/dictionary/english-indonesian/{user_input}"
  url2 = f"https://www.oxfordlearnersdictionaries.com/definition/english/{user_input}"
  response = requests.get(url, headers=headers)
  response2 = requests.get(url2, headers=headers)

  soup = BeautifulSoup(response.text, "html.parser")
  soup2 = BeautifulSoup(response2.text, "html.parser")

  words = []
  translations = []
  examples = []
  synonyms = []
  sentences = []
  mp3 = []

  # get mp3 urls
  mp3uk1 = soup2.find("div",
                      {"class": "sound audio_play_button pron-uk icon-audio"})
  mp3uk1 = mp3uk1.get("data-src-mp3") if mp3uk1 else "Data Tidak Ditemukan"

  mp3us1 = soup2.find("div",
                      {"class": "sound audio_play_button pron-us icon-audio"})
  mp3us1 = mp3us1.get("data-src-mp3") if mp3us1 else "Data Tidak Ditemukan"

  # get word title
  title1 = soup2.find("h1", {"class": "headword"})
  title1 = title1.text if title1 else "Data Tidak Ditemukan"

  # append all
  mp3.append(mp3uk1)
  mp3.append(mp3us1)
  words.append(title1)

  # find the first ul tag with the class name 'sense-group-results'
  uls = soup.find("ul", {"class": "sense-group-results"})

  # find all the li tags inside the ul tag again, but this time extract the word from the babTTS link
  for lis in uls.find_all("li"):
    get_a = lis.find("a")
    if get_a is not None and get_a.get("href") and "babTTS" in get_a.get(
        "href"):
      # extract the word from the href attribute
      word = get_a.get("href").split("'")[3]
      words.append(word)

  # find all the li tags inside the ul tag and skip the first one
  for lis in uls.find_all("li")[1:]:
    get_a = lis.find("a")
    if get_a is not None:
      words.append(get_a.text)

  # find translations and examples
  for sense in soup.find_all("span", {"class": "ogl_sense"}):
    for another in sense.find_all_next("span", {"class": "ogl_sense_inner"}):
      for translation in another.find_all("span",
                                          {"class": "ogl_translation noline"}):
        translations.append(translation.text.strip())
      for example in another.find_all("span", {"class": "ogl_examples"}):
        # english
        for eng in example.find_all("span", {"class": "ogl_exa"}):
          examples.append(eng.text.strip())
        # indonesian
        for ind in example.find_all("span", {"class": "ogl_translation"}):
          examples.append(ind.text.strip())

      # translation = another.find('span', {'class': 'ogl_translation noline'})
      # if translation:
      #     translations.append(translation.text.strip())
      #     example = another.find('span', {'class': 'ogl_examples'})
      #     if example:
      #         eng = example.find('span', {'class': 'ogl_exa'})
      #         ind = example.find('span', {'class': 'ogl_translation'})
      #         if eng and ind:
      #             examples.append({'eng': eng.text.strip(), 'ind': ind.text.strip()})

  for tag in soup.select(
      ".icon-link-wrapper.dropdown a, .icon-link-wrapper.dropdown span, .icon-link-wrapper.dropdown ul, .icon-link-wrapper.dropdown li, .icon-link-wrapper.dropdown another"
  ):
    tag.decompose()

  for contextual in soup.find_all("div", {"class": "sense-group"}):
    for example in soup.find_all("div", {"class": "dict-example"}):
      eng1 = None  # Define eng1 outside of the inner loop
      for eng in example.find_all(
          "div", {"class": "dict-source dict-source_examples"}):
        eng1 = eng.text.strip()  # Assign value to eng1
      for ind in example.find_all("div", {"class": "dict-result"}):
        ind1 = ind.text.strip()
        if eng1 and ind1:
          sentences.append({"eng": eng1, "ind": ind1})

  lis = soup.select(".quick-result-entry .quick-result-overview li a")
  for li in lis[9:15]:
    synonym = li.text
    synonyms.append(synonym)

  # create dictionary and return as JSON
  data = {
    "words": words,
    "translations": translations,
    "examples": examples,
    "synonyms": synonyms,
    "sentences": sentences,
    "mp3": mp3,
    "author": "Xnuvers007 [ Https://github.com/Xnuvers007 ]",
  }
  return jsonify(data)


@app.route("/kanjiname", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def kanji_name():
  nama = request.args.get("nama")
  url = f"https://jepang-indonesia.co.id/kanjiname/convert?name={nama}&x=73&y=48"

  headers = {
    "User-Agent":
    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
  }

  response = requests.get(url, headers=headers)

  soup = BeautifulSoup(response.text, "html.parser")

  # get url from this my server menggunakan requests host

  server = f"{request.host_url}kanjiname?nama={nama}"

  result = {
    "kanji":
    soup.find("div", {
      "class": "text-center rounded-box hanzi"
    }).text.strip(),
    "arti":
    soup.find("div", {
      "class": "text-center meantext"
    }).text.strip(),
    "original":
    nama,
    "server":
    server,
  }

  return jsonify(result)


@app.route("/translate", methods=["GET"])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def translate():
  from_lang = request.args.get("from", "en")
  to_lang = request.args.get("to", "id")
  text = request.args.get("text", "")

  # set up headers
  headers = {
    "User-Agent": random.choice(get_user_agents()),
    "Referer": "http://translate.google.com/",
    "Origin": "http://translate.google.com/",
  }

  # send request to Google Translate API
  url = f"https://translate.google.com/translate_a/single?client=gtx&sl={from_lang}&tl={to_lang}&dt=t&q={text}"
  response = requests.get(url, headers=headers)

  # extract translated text from response
  result = response.json()
  if result is not None and len(result) > 0 and len(result[0]) > 0:
    translated_text = result[0][0][0]
  else:
    translated_text = "Translation failed"

  # return result as JSON
  return jsonify({
    "code/status": response.status_code,
    "from": from_lang,
    "to": to_lang,
    "text": text,
    "user_agent": headers["User-Agent"],
    "translated_text": translated_text,
    "credits": "Xnuvers007 ( https://github.com/xnuvers007 )",
  })


def igstalk(username):
  headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
  }
  url = f"https://dumpoir.com/v/{username}"

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    profile = (
      soup.select_one("#user-page > div.user > div.row > div > div.user__img")
      ["style"].replace("background-image: url('", "").replace("');", ""))
    fullname = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > div > a > h1"
    ).get_text()
    username = soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > div > h4"
    ).get_text()
    post = (soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(1)"
    ).get_text().replace(" Posts", ""))
    followers = (soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(2)"
    ).get_text().replace(" Followers", ""))
    following = (soup.select_one(
      "#user-page > div.user > div > div.col-md-4.col-8.my-3 > ul > li:nth-child(3)"
    ).get_text().replace(" Following", ""))
    bio = soup.select_one(
      "#user-page > div.user > div > div.col-md-5.my-3 > div").get_text()

    result = {
      "profile": profile,
      "fullname": fullname,
      "username": username,
      "post": post,
      "followers": followers,
      "following": following,
      "bio": bio,
      "url": f"https://www.instagram.com/{username.replace('@', '')}",
    }

    return result, response.status_code

  except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
      raise Exception("Error: Account not found")
    elif e.response.status_code == 403:
      raise Exception("Error: Account is private")
    else:
      # redirect('https://tr.deployers.repl.co/igstalk?user=Indradwi.25')
      redirect(url_for("index"))


@app.route("/igstalk")
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def igstalk_route():
  username = request.args.get("user")

  if not username:
    # return jsonify({"error": "Missing username parameter"}), 400
    #   return redirect('https://tr.deployers.repl.co/igstalk?user=Indradwi.25'), 400
    return redirect(url_for("/"))

  try:
    result, status_code = igstalk(username)
    result["status"] = status_code
    result["credits"] = "Xnuvers007 (https://github.com/Xnuvers007)"
    return jsonify(result), status_code

  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route('/cariobat', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def cari_obat():
  obat = request.args.get('obat')

  url = "https://www.halodoc.com/obat-dan-vitamin/search/" + obat

  response = requests.get(
    url,
    headers={
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
    })
  time.sleep(1.5)

  soup = BeautifulSoup(response.content, "html.parser")

  data = []

  gambar_elements = soup.find_all("div", class_="img-wrapper")
  gambar_alt = [elem.find("img")["alt"] for elem in gambar_elements]

  fallback_images = soup.find_all("img", class_="fallback-img")
  fallback_image_urls = [img["src"] for img in fallback_images]

  harga = soup.find_all("div", class_="custom-container__list")
  dataharga = []

  for i in harga:
    for j in i.findAll(
        "label", class_="custom-container__list__container__price--label"):
      dataharga.append(j.text.strip())

  datasumber = []
  for i in harga:
    for j in i.findAll("a",
                       class_="custom-container__list__container__item--link"):
      href = j["href"].strip()
      sumber = "https://www.halodoc.com" + href
      datasumber.append(sumber)

  for alt, fallback_url, harga, sumber in zip(gambar_alt, fallback_image_urls,
                                              dataharga, datasumber):
    obat_data = {}
    obat_data['alt'] = alt
    obat_data['fallback_url'] = fallback_url
    obat_data['harga'] = harga
    obat_data['sumber'] = sumber
    data.append(obat_data)

  return jsonify(data)


@app.route('/keterangan', methods=['GET'])
def keterangan_obat():
  datasumber = request.args.get('obat')
  if re.match(r"^https?://", datasumber):
    url = datasumber
  elif not re.match(r"^https?://", datasumber):
    url = "https://" + datasumber
  elif datasumber.startswith("/"):
    datasumber = datasumber[1:]
    datasumber = re.sub(r"\s", "-", datasumber)
    url = "https://www.halodoc.com/obat-dan-vitamin/" + datasumber
  else:
    datasumber = re.sub(r"\s", "-", datasumber)
    url = "https://www.halodoc.com/obat-dan-vitamin/" + datasumber

  if datasumber.startswith("/"):
    url = "https://www.halodoc.com" + datasumber

  response = requests.get(
    url,
    headers={
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
    })
  time.sleep(1.5)

  soup = BeautifulSoup(response.content, "html.parser")

  drug_details = soup.find_all("div", class_="drug-detail col-md-12")

  if len(drug_details) > 0:
    data = {}
    data['Deskripsi'] = drug_details[0].text.strip(
    ) if drug_details[0].text else ""
    data['Indikasi Umum'] = drug_details[1].text.strip(
    ) if drug_details[1].text else ""
    data['Komposisi'] = drug_details[2].text.strip(
    ) if drug_details[2].text else ""
    data['Dosis'] = drug_details[3].text.strip(
    ) if drug_details[3].text else ""
    data['Aturan Pakai'] = drug_details[4].text.strip(
    ) if drug_details[4].text else ""
    data['Peringatan'] = drug_details[5].text.strip(
    ) if drug_details[5].text else ""
    data['Kontra Indikasi'] = drug_details[6].text.strip(
    ) if drug_details[6].text else ""
    data['Efek Samping'] = drug_details[7].text.strip(
    ) if drug_details[7].text else ""
    data['Golongan Produk'] = drug_details[8].text.strip(
    ) if drug_details[8].text else ""
    data['Kemasan'] = drug_details[9].text.strip(
    ) if drug_details[9].text else ""
    data['Manufaktur'] = drug_details[10].text.strip(
    ) if drug_details[10].text else ""
    data['No. Registrasi'] = drug_details[11].text.strip(
    ) if drug_details[11].text else ""
    return jsonify(data)
  else:
    return "Tidak ada data yang ditemukan."


# URL SHORTLINK TINYURL
class UrlShortenTinyurl:
  URL = "http://tinyurl.com/api-create.php"

  @staticmethod
  def shorten(url_long):
    try:
      url = UrlShortenTinyurl.URL + "?" + urllib.parse.urlencode(
        {"url": url_long})
      res = requests.get(url)
      short_url = res.text
      return short_url
    except Exception as e:
      raise e


@app.route('/short', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def shorten_url():
  try:
    url_long = request.args.get('url')
    if not url_long:
      server = f"{request.host_url}short?url=github.com/Xnuvers007"
      return jsonify({
        'error': 'No URL provided.',
        'endpoint': server,
        'author': 'Xnuvers007 [ https://github.com/Xnuvers007 ]'
      }), 400

    # Check if "http://" or "https://" prefix is missing and add it based on server support
    if not url_long.startswith('http://') and not url_long.startswith(
        'https://'):
      if request.is_secure:
        url_long = 'https://' + url_long
      else:
        url_long = 'http://' + url_long

    short_url = UrlShortenTinyurl.shorten(url_long)
    return jsonify({
      'short_url': short_url,
      'status': 200,
      'author': 'Xnuvers007 [ https://github.com/Xnuvers007 ]'
    }), 200
  except Exception as e:
    traceback.print_exc()
    return jsonify({'error': 'An error occurred.'}), 500
    raise e


@app.route('/tiktok', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def download_tiktok_video():
  url = request.args.get('url')
  # sources = input("Enter link Tiktok: ")

  cookies = {
    '_gid': 'GA1.2.1792354021.1686935708',
    '_gat_UA-3524196-6': '1',
    '__gads':
    'ID=a5ab8cd128367568-22143e9f8de100bf:T=1686935709:RT=1686974876:S=ALNI_MZGs_Ok-Opd0utB89Ocx6MHsRPIhg',
    '__gpi':
    'UID=00000c5060eb2f3a:T=1686935709:RT=1686974876:S=ALNI_MaTK25bQMrHcFRzycSi0AkbCKx4Rg',
    '_ga': 'GA1.2.1848273344.1686935708',
    '_ga_ZSF3D6YSLC': 'GS1.1.1686974876.3.0.1686974917.0.0.0',
  }

  headers = {
    'authority':
    'ssstik.io',
    'accept':
    '*/*',
    'accept-language':
    'id,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'cache-control':
    'no-cache',
    'content-type':
    'application/x-www-form-urlencoded; charset=UTF-8',
    # 'cookie': '_gid=GA1.2.1792354021.1686935708; _gat_UA-3524196-6=1; __gads=ID=a5ab8cd128367568-22143e9f8de100bf:T=1686935709:RT=1686974876:S=ALNI_MZGs_Ok-Opd0utB89Ocx6MHsRPIhg; __gpi=UID=00000c5060eb2f3a:T=1686935709:RT=1686974876:S=ALNI_MaTK25bQMrHcFRzycSi0AkbCKx4Rg; _ga=GA1.2.1848273344.1686935708; _ga_ZSF3D6YSLC=GS1.1.1686974876.3.0.1686974917.0.0.0',
    'hx-current-url':
    'https://ssstik.io/en',
    'hx-request':
    'true',
    'hx-target':
    'target',
    'hx-trigger':
    '_gcaptcha_pt',
    'origin':
    'https://ssstik.io',
    'pragma':
    'no-cache',
    'referer':
    'https://ssstik.io/en',
    'sec-ch-ua':
    '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile':
    '?0',
    'sec-ch-ua-platform':
    '"Windows"',
    'sec-fetch-dest':
    'empty',
    'sec-fetch-mode':
    'cors',
    'sec-fetch-site':
    'same-origin',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43',
  }

  params = {
    'url': 'dl',
  }

  data = {
    'id':
    url,  # 'https://www.tiktok.com/@yurii_kun5/video/7225627953185721627?is_from_webapp=1&sender_device=pc'
    'locale': 'en',
    'tt': 'UHZpa0pl',
  }

  response = requests.post('https://ssstik.io/abc',
                           params=params,
                           cookies=cookies,
                           headers=headers,
                           data=data)

  downloadVideos = BeautifulSoup(response.text, 'html.parser')
  downloadLink = downloadVideos.a["href"]
  video_content = requests.get(downloadLink).content

  file_name = f"{time.time()}.mp4"
  file_path = f"{DOWNLOAD_DIR}/{file_name}"
  with open(file_path, 'wb') as video:
    video.write(video_content)

  escaped_data = file_path  #escape(file_name)

  return f"Video downloaded. Access it at: <a href='{escaped_data}'>{escaped_data}</a>"


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
  return send_from_directory(DOWNLOAD_DIR, path=filename, as_attachment=True)


@app.route('/d', methods=['GET'])
@app.route('/de', methods=['GET'])
@app.route('/del', methods=['GET'])
@app.route('/dele', methods=['GET'])
@app.route('/delet', methods=['GET'])
@app.route('/delete', methods=['GET'])
@app.route('/e', methods=['GET'])
@app.route('/el', methods=['GET'])
@app.route('/ele', methods=['GET'])
@app.route('/elet', methods=['GET'])
@app.route('/elete', methods=['GET'])
@app.route('/et', methods=['GET'])
@app.route('/ete', methods=['GET'])
@app.route('/l', methods=['GET'])
@app.route('/le', methods=['GET'])
@app.route('/let', methods=['GET'])
@app.route('/lete', methods=['GET'])
@app.route('/t', methods=['GET'])
@app.route('/te', methods=['GET'])
def delete_files():
  files = glob.glob(f"{DOWNLOAD_DIR}/*")
  current_time = time.time()
  for file in files:
    if os.path.isfile(file):
      modified_time = os.path.getmtime(file)
      if current_time - modified_time > 1:
        os.remove(file)
  time.sleep(1)  # Sleep for 30 minutes
  delete_threads = threading.Thread(target=delete_files)
  delete_threads.start()
  return "<h1><strong>Files deleted.</strong></h1>"


@app.route('/openai', methods=['GET'])
@cross_origin()
@cache.cached(timeout=3600, query_string=True)
def openai():
  APIKEYS_NYA = request.args.get('key')

  if not APIKEYS_NYA:
    return jsonify({
      'error': 'Masukkan APIKEYS OPENAI',
      'path': '/openai?key=APIKEYS_NYA'
    })

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://yenom.pro',
    'Connection': 'keep-alive',
    'Referer': 'https://yenom.pro/cek.php',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
  }

  data = {
    'api_keys': APIKEYS_NYA,
  }

  response = requests.post('https://yenom.pro/cek.php',
                           headers=headers,
                           data=data)

  soup = BeautifulSoup(response.text, 'html.parser')

  # get table of contents
  table = soup.find('table')

  # get all rows from table
  rows = table.find_all('tr')

  # get all columns from table
  columns = [v.text.replace('\n', '') for v in rows[0].find_all('th')]

  # build output as JSON
  output = []
  for i in range(1, len(rows)):
    tds = rows[i].find_all('td')
    row_data = {}
    for j, td in enumerate(tds):
      column_name = columns[j]
      value = td.text.replace('\n', '')
      row_data[column_name] = value
    output.append(row_data)

  result = {
    'author': 'Xnuvers007 (https://github.com/Xnuvers007)',
    'donate': 'https://ndraeee25.000webhostapp.com/dana/DanaXnuvers007.jpeg',
    'data': output
  }

  return jsonify(result)


def scrape_matches_from_table(table):
  tbody = table.find('tbody')
  if not tbody:
    return "Jadwal Pertandingan belum tersedia"

  trs = tbody.find_all('tr')

  matches_data = []

  for tr in trs:
    club_boxes = tr.find_all('span', class_='clubBox-name')
    tds = tr.find_all('td')[0:2]
    if len(club_boxes) >= 2:
      team1, team2 = [club.text.strip() for club in club_boxes]
      match_time = tds[1].text.strip()
      matches_data.append(f"{team1} vs {team2} ({match_time})")

  return matches_data


def scrape_matches_from_table(table):
  tbody = table.find('tbody')
  if not tbody:
    return "Jadwal Pertandingan belum tersedia"

  trs = tbody.find_all('tr')

  matches_data = []

  for tr in trs:
    club_boxes = tr.find_all('span', class_='clubBox-name')
    tds = tr.find_all('td')[0:2]
    if len(club_boxes) >= 2:
      team1, team2 = [club.text.strip() for club in club_boxes]
      match_time = tds[1].text.strip()
      matches_data.append(f"{team1} vs {team2} ({match_time})")

  return matches_data


def get_jadwal_pertandingan(url):
  cookies = {
    'ahoy_visitor': '9f1bb6dc-790f-4664-82e6-7611c0f9a132',
    '_ga_YV9LXF9F74': 'GS1.1.1690092464.11.1.1690092762.42.0.0',
    '_ga': 'GA1.1.970211948.1689523452',
    '__gads':
    'ID=79358ecd1813041a:T=1689523448:RT=1690092467:S=ALNI_MYdBdDc8Vcy0SeNFLWyKRIx1T9uqA',
    '__gpi':
    'UID=00000c2149be351d:T=1689523448:RT=1690092467:S=ALNI_MaRUe2JyuR-N_K2kAhk898eqlziTg',
    '_cc_id': 'a3c5e70268c5926475d2e072101ce745',
    'cto_bundle':
    'BMnfl184RlY4MWhCdDNIQ0ZzUiUyQmlKSG0yZSUyRmFkVXdqenpTbFdOSDJxckNiYjBwMVNBVk5raERYcmRZdGRFUW5JUUZOTVBrZlNlaldaSGdvT0wxc3pGZDNzMWp4MGZCejBtekMlMkIlMkY5cmJxY0JPZzlFZXU1elBkWmQ1ZHlmN0pxRlVyYlJla1RVWE04ZSUyRksyJTJCNTBZTDltODRoTkElM0QlM0Q',
    '_ga_6HPZ6B3B7K': 'GS1.1.1690097027.12.0.1690097027.0.0.0',
    'youniverse_id': '51fca571-692f-45cf-b92d-df7dce5cadba',
    'bola_net_xtreme_visit_count_': '5',
    '_gid': 'GA1.2.449434685.1690092460',
    'panoramaId_expiry': '1690178874304',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Alt-Used': 'www.bola.net',
    'Connection': 'keep-alive',
    'Referer': 'https://www.bola.net/jadwal-pertandingan/',
    # 'Cookie': 'ahoy_visitor=9f1bb6dc-790f-4664-82e6-7611c0f9a132; _ga_YV9LXF9F74=GS1.1.1690092464.11.1.1690092762.42.0.0; _ga=GA1.1.970211948.1689523452; __gads=ID=79358ecd1813041a:T=1689523448:RT=1690092467:S=ALNI_MYdBdDc8Vcy0SeNFLWyKRIx1T9uqA; __gpi=UID=00000c2149be351d:T=1689523448:RT=1690092467:S=ALNI_MaRUe2JyuR-N_K2kAhk898eqlziTg; _cc_id=a3c5e70268c5926475d2e072101ce745; cto_bundle=BMnfl184RlY4MWhCdDNIQ0ZzUiUyQmlKSG0yZSUyRmFkVXdqenpTbFdOSDJxckNiYjBwMVNBVk5raERYcmRZdGRFUW5JUUZOTVBrZlNlaldaSGdvT0wxc3pGZDNzMWp4MGZCejBtekMlMkIlMkY5cmJxY0JPZzlFZXU1elBkWmQ1ZHlmN0pxRlVyYlJla1RVWE04ZSUyRksyJTJCNTBZTDltODRoTkElM0QlM0Q; _ga_6HPZ6B3B7K=GS1.1.1690097027.12.0.1690097027.0.0.0; youniverse_id=51fca571-692f-45cf-b92d-df7dce5cadba; bola_net_xtreme_visit_count_=5; _gid=GA1.2.449434685.1690092460; panoramaId_expiry=1690178874304',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
  }

  response = requests.get(url, cookies=cookies, headers=headers)

  # check if cookies and headers are valid and not expired
  if not response.ok:
    print("Cookies or Headers are not valid")
    return

  soup = BeautifulSoup(response.text, 'html.parser')

  Jadwal = soup.find('h1', class_='box-title')
  if not soup.find_all('table', class_='main-table main-table--jadwal'):
    return {"url": url, "data": "Jadwal Pertandingan belum tersedia"}

  matches_data = []
  tables = soup.find_all('table', class_='main-table main-table--jadwal')

  for table in tables:
    thead = table.find('thead')
    th = thead.find_all('th')[0]
    date = th.text.strip()
    data = scrape_matches_from_table(table)
    matches_data.extend([(date, match) for match in data
                         ])  # Append date along with match data

  return {"judul": Jadwal.text, "url": url, "data": matches_data}


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/jadwal-pertandingan', methods=['GET'])
def jadwal_pertandingan():
  links = [
    "https://www.bola.net/jadwal-pertandingan/indonesia.html",
    "https://www.bola.net/jadwal-pertandingan/inggris.html",
    "https://www.bola.net/jadwal-pertandingan/italia.html",
    "https://www.bola.net/jadwal-pertandingan/spanyol.html",
    "https://www.bola.net/jadwal-pertandingan/champions.html",
    "https://www.bola.net/jadwal-pertandingan/jerman.html",
    "https://www.bola.net/jadwal-pertandingan/prancis.html"
  ]

  results = []

  for link in links:
    response = get_jadwal_pertandingan(link)
    results.append(response)

  return jsonify(results)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/zerogpt', methods=['GET', 'POST'])
def detect_text():
  if request.method == 'POST':
    t = request.form.get('text')

    cookies = {
      '_gid':
      'GA1.2.2082658495.1687029546',
      '_ga_0YHYR2F422':
      'GS1.1.1687029546.4.0.1687029546.0.0.0',
      '_ga':
      'GA1.1.536846619.1686378008',
      '__gads':
      'ID=7f4d15fa18fc00b0-223fc645a5b40066:T=1686378006:RT=1687029546:S=ALNI_Mb9fZYiAgQvvyLX4bMsTwH_9EiqHA',
      '__gpi':
      'UID=00000c465e269f92:T=1686378006:RT=1687029546:S=ALNI_MYnnN1CPxljGUhJ8dXj6T8ePiIXjw',
    }

    headers = {
      'authority':
      'api.zerogpt.com',
      'accept':
      'application/json, text/plain, */*',
      'accept-language':
      'id,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
      'cache-control':
      'no-cache',
      'content-type':
      'application/json',
      'origin':
      'https://www.zerogpt.com',
      'pragma':
      'no-cache',
      'referer':
      'https://www.zerogpt.com/',
      'sec-ch-ua':
      '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
      'sec-ch-ua-mobile':
      '?0',
      'sec-ch-ua-platform':
      '"Windows"',
      'sec-fetch-dest':
      'empty',
      'sec-fetch-mode':
      'cors',
      'sec-fetch-site':
      'same-site',
      'user-agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
    }

    json_data = {
      'input_text': t,
    }

    response = requests.post('https://api.zerogpt.com/api/detect/detectText',
                             cookies=cookies,
                             headers=headers,
                             json=json_data)

    json_response = response.json()

    return jsonify(json_response)

  return '''
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta name="description" content="ZeroGPT Text Detection">
                <meta name="author" content="Xnuvers007">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <title>ZeroGPT Text Detection</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            </head>
            <body>
                <div class="container mt-5">
                    <form action="/zerogpt" method="POST">
                        <div class="form-group">
                            <label for="text">Text</label>
                            <textarea class="form-control" id="text" name="text" rows="7" cols="50"></textarea>
                        </div>
                        <center><button type="submit" class="btn btn-primary">Detect Text</button></center>
                    </form>
                </div>
                <script>
        // Accessing navigator.userAgent, navigator.appVersion, and navigator.platform
        var userAgent = navigator.userAgent;
        var appVersion = navigator.appVersion;
        var platform = navigator.platform;
        
        // Perform any actions or log the values as needed
        console.log(userAgent);
        console.log(appVersion);
        console.log(platform);
    </script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.min.js"></script>
            </body>
            </html>
        '''


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/zerogptjson', methods=['GET'])
def deteksiteksjson():
  t = request.args.get('t')

  cookies = {
    '_gid':
    'GA1.2.2082658495.1687029546',
    '_ga_0YHYR2F422':
    'GS1.1.1687029546.4.0.1687029546.0.0.0',
    '_ga':
    'GA1.1.536846619.1686378008',
    '__gads':
    'ID=7f4d15fa18fc00b0-223fc645a5b40066:T=1686378006:RT=1687029546:S=ALNI_Mb9fZYiAgQvvyLX4bMsTwH_9EiqHA',
    '__gpi':
    'UID=00000c465e269f92:T=1686378006:RT=1687029546:S=ALNI_MYnnN1CPxljGUhJ8dXj6T8ePiIXjw',
  }

  headers = {
    'authority':
    'api.zerogpt.com',
    'accept':
    'application/json, text/plain, */*',
    'accept-language':
    'id,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'cache-control':
    'no-cache',
    'content-type':
    'application/json',
    # 'cookie': '_gid=GA1.2.2082658495.1687029546; _ga_0YHYR2F422=GS1.1.1687029546.4.0.1687029546.0.0.0; _ga=GA1.1.536846619.1686378008; __gads=ID=7f4d15fa18fc00b0-223fc645a5b40066:T=1686378006:RT=1687029546:S=ALNI_Mb9fZYiAgQvvyLX4bMsTwH_9EiqHA; __gpi=UID=00000c465e269f92:T=1686378006:RT=1687029546:S=ALNI_MYnnN1CPxljGUhJ8dXj6T8ePiIXjw',
    'origin':
    'https://www.zerogpt.com',
    'pragma':
    'no-cache',
    'referer':
    'https://www.zerogpt.com/',
    'sec-ch-ua':
    '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile':
    '?0',
    'sec-ch-ua-platform':
    '"Windows"',
    'sec-fetch-dest':
    'empty',
    'sec-fetch-mode':
    'cors',
    'sec-fetch-site':
    'same-site',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
  }

  json_data = {
    'input_text': t,
  }

  response = requests.post('https://api.zerogpt.com/api/detect/detectText',
                           cookies=cookies,
                           headers=headers,
                           json=json_data)

  json_response = response.json()

  return jsonify(json_response)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/playlist', methods=['GET'])
def get_playlist():
  playlist_name = request.args.get('name', default='anime')
  limit = int(request.args.get('lim', default=51))

  playlists_search = PlaylistsSearch(playlist_name, limit=limit)
  results = playlists_search.result()

  return jsonify(results)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/vid', methods=['GET'])
def get_video():
  video_name = request.args.get('name', default='anime')
  limit = int(request.args.get('lim', default=51))

  all_search = Search(video_name, limit=limit)
  results = all_search.result()

  return jsonify(results)


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/playlist', defaults={'path': ''})
@app.route('/vid', defaults={'path': ''})
def invalid_url(path):
  return redirect('/playlist?name=anime&lim=51')


def get_ip_addresses(url):
  try:
    # Get the IP address associated with the URL
    hostname = urlparse(url).hostname
    if not hostname:
      return None, None
    ip_address = socket.gethostbyname(hostname)
    real_ip_address = socket.gethostbyname_ex(hostname)[2][0]
    return ip_address, real_ip_address
  except socket.gaierror as e:
    return None, None


def is_vulnerable_to_clickjacking(url):
  # Suppress SSL warnings
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  headers = {'User-Agent': 'Mozilla/5.0'}
  try:
    response = requests.get(url, headers=headers, verify=False)
  except requests.exceptions.SSLError as e:
    return False, f"Unable to make an SSL connection to {escape(url)}: {escape(str(e))}"

  # Check if X-Frame-Options header is set
  x_frame_options = response.headers.get('X-Frame-Options')
  content_security_policy = response.headers.get('Content-Security-Policy')

  # Get the IP and real IP addresses
  ip_address, real_ip_address = get_ip_addresses(url)

  if not x_frame_options and not content_security_policy:
    return True, f"{escape(url)} is vulnerable to clickjacking (X-Frame-Options header is not set) and (Content-Security-Policy header is not set)."

  if not x_frame_options:
    return True, f"{escape(url)} is vulnerable to clickjacking (X-Frame-Options header is not set)."

  if not content_security_policy:
    return True, f"{escape(url)} is vulnerable to clickjacking (Content-Security-Policy header is not set)."

  return True, f"{escape(url)} is not vulnerable to clickjacking."


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/cj')
def check_clickjacking_vulnerability():
  website = request.args.get('u')

  # Check if the 'u' parameter is provided
  if not website:
    return jsonify({
      "parameter":
      escape(request.host_url + "cj?u=https://tr.deployers.repl.co")
    })

  # Add 'http://' if the URL doesn't have a scheme
  if not urlparse(website).scheme:
    website = 'http://' + website

  is_vulnerable, result_message = is_vulnerable_to_clickjacking(website)

  # Get the current time
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  how_to_protect = '''
How To Protect Your Website From Clickjacking
[+] X-Frame-Options
1. X-FRAME-OPTIONS: DENY
2. X-FRAME-OPTIONS: SAMEORIGIN
3. X-FRAME-OPTIONS: ALLOW-FROM https://example.com

[+] Content-Security-Policy
1. Content-Security-Policy: frame-ancestors 'none'
2. Content-Security-Policy: frame-ancestors 'self'
3. Content-Security-Policy: frame-ancestors https://example.com

[+] Frame busting
<style>
/* Hide page by default */
html { display : none; }
</style>
<script>
if (self == top) {
// Everything checks out, show the page.
document.documentElement.style.display = 'block';
} else {
// Break out of the frame.
top.location = self.location;
}
</script>

[+] Code Snippets
1. NodeJS
response.setHeader("X-Frame-Options", "DENY");
response.setHeader("Content-Security-Policy", "frame-ancestors 'none'");

2. Java
public void doGet(HttpServletRequest request, HttpServletResponse response)
{
response.addHeader("X-Frame-Options", "DENY");
response.addHeader("Content-Security-Policy", "frame-ancestors 'none'");
}

3. PHP
response.setHeader("X-Frame-Options", "DENY");
response.setHeader("Content-Security-Policy", "frame-ancestors 'none'");

4. Python
response.headers["X-Frame-Options"] = "DENY"
response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"

[+] Web Server & Frameworks config:
1. Apache
Enable mod_headers using this command:
a2enmod headers

Restart the apache server
sudo service apache2 restart

Open and edit the config file in sites-available folder
sudo nano 000-default.conf

Add the following lines in <Virtual host>
Header set X-Frame-Options "DENY"
Header set Content-Security-Policy "frame-ancestors 'none'"

2. Nginx
Open and edit the config file in sites-available folder
sudo nano default

Add the following lines in {Server block}
add_header X-Frame-Options "DENY";
add_header Content-Security-Policy "frame-ancestors 'none'";

Restart the nginx server
sudo service nginx restart

3. Wordpress

Open and edit the wp-config.php file
sudo nano wp-config.php

Add the following lines in the end of the file
header('X-Frame-Options: SAMEORIGIN');
header("Content-Security-Policy: frame-ancestors 'none'");
'''.strip()

  # Prepare the JSON response
  response_data = {
    'url': escape(website),
    'is_vulnerable': is_vulnerable,
    'result_message': escape(result_message),
    'how_to_protect': escape(how_to_protect),
    'current_time': escape(current_time),
  }

  # Add IP addresses to the response if available
  ip_address, real_ip_address = get_ip_addresses(website)
  if ip_address and real_ip_address:
    response_data['ip_address'] = escape(ip_address)
    response_data['real_ip_address'] = escape(real_ip_address)

  return jsonify(response_data)


def formal(words, mode='formal'):
  cookies = {
    '_ga_G2MQKX8TDD': 'GS1.1.1690508017.3.1.1690508201.0.0.0',
    '_ga': 'GA1.1.169299824.1690395373',
    '__gads':
    'ID=cbbec9c914184adf-2216db83b6e700bc:T=1690395375:RT=1690508019:S=ALNI_MbmhZNSvwe6aKH6ktfzzl0-xd_GMw',
    '__gpi':
    'UID=00000c2464e7c373:T=1690395375:RT=1690508019:S=ALNI_MbdDsKNqRWAGM-QRJa7wfCaAR16CA',
    'XSRF-TOKEN':
    'eyJpdiI6IkhHT0tXZlZHNlQrQmFsTnp5K3FEU0E9PSIsInZhbHVlIjoiRGVrbzExcWoxZ1h2TlVGQ2VmKy9EVVdiRzlPWmp6WU1iVlhna2tZd0VkSFBlMlJXN1h3TXVHeDRQc2hiQVp0eWxRNGdNVy9UMzlReDBjSEpWT0FweEtMK3pZMytnVTBvOEZ4NjVFTFFncFJkUlZ3SW1LU0VzSzlnNk4wTzFFTGwiLCJtYWMiOiI2Y2MyZTUyZTRhMzU0ZDdjMjg4MjQwMDZlOTc2ZTMwMmYwNjg1NzJmODUwNTZmNDQxYWEzYmIwYzE3NjViNDJkIiwidGFnIjoiIn0%3D',
    'paraphrasingio_session':
    'eyJpdiI6Ik80YkViVU9KNDlYeHhObFAvNitod3c9PSIsInZhbHVlIjoia2RDbmVSN2JRRDB0dWp5ZkE3ekpCVkxPaW9SREs2cytFYmFVZjBlcDc4UnE3VWd1TnYzZnk2d2ZlQ3dUYWt3bk15OWdDT2FjK2pUZUt6dFZwdnJidWtsS1kwbHR0ZWtKNVpIMkR0L2VzTEtRLzlDWlFYRjI5RDZOL2dmS05pdm8iLCJtYWMiOiIzNmVkNmM3YjVkNDVkMzdhZGMxYWIwZWVhMzYzMzk1MmJjODRiYjZhNGZiMjljMzFkMjVlNzg3ZmVhZTZiYWM4IiwidGFnIjoiIn0%3D',
    'g_state': '{"i_p":1690515306722,"i_l":1}',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'X-CSRF-TOKEN': 'k6yDSGkhgj4h3NKSbfO6gAvuHVYRlmLtfqh5CezH',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json;charset=utf-8',
    'X-XSRF-TOKEN':
    'eyJpdiI6IkhHT0tXZlZHNlQrQmFsTnp5K3FEU0E9PSIsInZhbHVlIjoiRGVrbzExcWoxZ1h2TlVGQ2VmKy9EVVdiRzlPWmp6WU1iVlhna2tZd0VkSFBlMlJXN1h3TXVHeDRQc2hiQVp0eWxRNGdNVy9UMzlReDBjSEpWT0FweEtMK3pZMytnVTBvOEZ4NjVFTFFncFJkUlZ3SW1LU0VzSzlnNk4wTzFFTGwiLCJtYWMiOiI2Y2MyZTUyZTRhMzU0ZDdjMjg4MjQwMDZlOTc2ZTMwMmYwNjg1NzJmODUwNTZmNDQxYWEzYmIwYzE3NjViNDJkIiwidGFnIjoiIn0=',
    'Origin': 'https://www.paraphrasing.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphrasing.io/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  json_data = {
    'uri': 'paraphrase',
    'paragraph': words,
    'type': 'paraphrase',
    'lang': 'id',
    'mode': 'Simple',
    'structure': None,
    'grecaptcha': '',
  }

  response = requests.post('https://www.paraphrasing.io/contentGenerator',
                           cookies=cookies,
                           headers=headers,
                           json=json_data)

  resul = response.json()['result']
  jumlah_kalimat = response.json()['sentenceCount']
  pesan_status = response.json()['message']
  soup = BeautifulSoup(resul, 'html.parser')
  clean_text = soup.get_text()
  return {
    "Hasil: ": clean_text,
    "Jumlah Kalimat: ": jumlah_kalimat,
    "Pesan Status: ": pesan_status
  }


def regular(words, mode='regular'):

  cookies = {
    '_ga_G2MQKX8TDD': 'GS1.1.1690508017.3.1.1690508445.0.0.0',
    '_ga': 'GA1.1.169299824.1690395373',
    '__gads':
    'ID=cbbec9c914184adf-2216db83b6e700bc:T=1690395375:RT=1690508445:S=ALNI_MbmhZNSvwe6aKH6ktfzzl0-xd_GMw',
    '__gpi':
    'UID=00000c2464e7c373:T=1690395375:RT=1690508445:S=ALNI_MbdDsKNqRWAGM-QRJa7wfCaAR16CA',
    'XSRF-TOKEN':
    'eyJpdiI6Ik8zUTdEelY4bElqSm1oWW15QmFBQlE9PSIsInZhbHVlIjoiOGFFR1lKTkd3OHRyODhjWHVWalZkc1lSSTJOdklTSWdmRmV2ckNmRmRKdXF1cURWRUpXOGdzWFN4bUJINTJSei9tSlFxbnlDK056VEVGdXVNWEdYT1FTZ2R0OTJRelhTLzBiK3VXMXViY2ttTUErSFhkOHdwMWkrSUh4ZnFqenAiLCJtYWMiOiJkMWRmNzY0YWYzNzQ4Yzc2NTRhOGM3MmMwZDQwN2NiM2ZkOWYyOTJiMGUxNGQzZDYzNjVjZDYyMzY3Yzk3MDQ3IiwidGFnIjoiIn0%3D',
    'paraphrasingio_session':
    'eyJpdiI6Ikd5bGVoT0lrUEhVOUp3ekgvbWMyK0E9PSIsInZhbHVlIjoiKytqb0hrbVFaS2krZU1rVG5tQ3ltSFVBTTVzVlBFcUpNNTEwZEpueU1pUTY2VDVxakxOWHYvcTVsUGdMNlVmME90d1J5a0JJaElGQVlFa1o4cWQySGNpZjAzZ203ZUJPalV2bmlmR1BjN2V0MjF2OGhNdzlGd3IvZE5BSE4wbTciLCJtYWMiOiJmYWUwYmQ4OWY1OTUxMmEzOTQzNDYwNTE1MGEyZGM1NzRlNGI3NWI2ZjA2MGYyMTdjMjkzNzYzYmExYzQ5OGRkIiwidGFnIjoiIn0%3D',
    'g_state': '{"i_p":1690515306722,"i_l":1}',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'X-CSRF-TOKEN': 'k6yDSGkhgj4h3NKSbfO6gAvuHVYRlmLtfqh5CezH',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json;charset=utf-8',
    'X-XSRF-TOKEN':
    'eyJpdiI6Ik8zUTdEelY4bElqSm1oWW15QmFBQlE9PSIsInZhbHVlIjoiOGFFR1lKTkd3OHRyODhjWHVWalZkc1lSSTJOdklTSWdmRmV2ckNmRmRKdXF1cURWRUpXOGdzWFN4bUJINTJSei9tSlFxbnlDK056VEVGdXVNWEdYT1FTZ2R0OTJRelhTLzBiK3VXMXViY2ttTUErSFhkOHdwMWkrSUh4ZnFqenAiLCJtYWMiOiJkMWRmNzY0YWYzNzQ4Yzc2NTRhOGM3MmMwZDQwN2NiM2ZkOWYyOTJiMGUxNGQzZDYzNjVjZDYyMzY3Yzk3MDQ3IiwidGFnIjoiIn0=',
    'Origin': 'https://www.paraphrasing.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphrasing.io/id',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  json_data = {
    'uri': 'paraphrase',
    'paragraph': words,
    'type': 'paraphrase',
    'lang': 'id',
    'mode': 'word',
    'structure': None,
    'grecaptcha': '',
  }

  response = requests.post('https://www.paraphrasing.io/contentGenerator',
                           cookies=cookies,
                           headers=headers,
                           json=json_data)

  resul = response.json()['result']
  jumlah_kalimat = response.json()['sentenceCount']
  pesan_status = response.json()['message']
  soup = BeautifulSoup(resul, 'html.parser')
  clean_text = soup.get_text()
  return {
    "Hasil: ": clean_text,
    "Jumlah Kalimat: ": jumlah_kalimat,
    "Pesan Status: ": pesan_status
  }


def fluency(words, mode='fluency'):

  cookies = {
    'ci_session':
    'a%3A6%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2267848c32d61bf207d11c76424342df68%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22103.144.175.180%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A80%3A%22Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A109.0%29%20Gecko%2F20100101%20Firefox%2F115.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1690395650%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22checkauth%22%3Bs%3A25%3A%22checkparaphrase1690393811%22%3B%7D5e11ee8476fb6d35e836ac9ade5b0e29',
    '_pbjs_userid_consent_data': '6683316680106290',
    '_sharedID': '3544682c-cbd2-46be-ab04-89dacadcbd6f',
    '_sharedID_last': 'Wed%2C%2026%20Jul%202023%2017%3A50%3A13%20GMT',
    '_lr_retry_request': 'true',
    '_lr_env_src_ats': 'false',
    'cto_bundle':
    'RlCI3F9rUGVJQlJ3TiUyRlk4ajhPVW1sTUlFb0ZYWmE0Z3dCaTdzelhQeFh2N2JLTURIT2RnRmVHaW9BWENRcE5xTHU1aFc3MUFtTWpVcWREVThEV0JjMHNFd0tqM3UlMkJQTkFja1J4RjhhRzc2aGxScHdEOFVnU3lNVGJqWEJ4VUVQQk41JTJCMnRua3Z1QjNvUU14Q0d0ZTU4OVolMkJjdyUzRCUzRA',
    'cto_bidid':
    '4--XuV9iVDBodVM0Z2F5c05DR0N6TGslMkZEZHpLRkQ5Y21qdGVnJTJGeGdmbTE0Tkh4cDRmVW5KU2Q4d3c3NWlQRGdkaCUyQjhJYlpmNnpqN3IyNHBFa2hlVEVVZTRTUnc4R0hVZm1tZGt5QXZlQTNjdm01VmxpMWkyV1lUOTZHYmhUMzVPJTJCMEd0',
    '_ga_Q3XGSV1HE8': 'GS1.1.1690393813.1.0.1690393813.0.0.0',
    '_ga': 'GA1.2.1073571075.1690393814',
    'TawkConnectionTime': '0',
    'twk_idm_key': 'Tt8aWgRm5O4fYTxKWw4vM',
    '_ga_WGYTCZ2REQ': 'GS1.1.1690393814.1.0.1690393814.0.0.0',
    'twk_uuid_62ff0ee954f06e12d88f800b':
    '%7B%22uuid%22%3A%221.7xXuhykE54shomhhNsD76WzcW38KrPglJvS8WDkpJttRsWG3U4Z3grd8zEbcQyHkPOBQsa6Or3fBiq1hsSg5DnDW6TSB1sYY9KZ3DbnAqtmFeQq9E9z1LKRB%22%2C%22version%22%3A3%2C%22domain%22%3A%22paraphraser.io%22%2C%22ts%22%3A1690395354540%7D',
    '__gads':
    'ID=aaa45ab7366b4c7a:T=1690393815:RT=1690393815:S=ALNI_Ma0pKRQabLL3P82pFJwPqexy3GzBw',
    '__gpi':
    'UID=00000c2464462814:T=1690393815:RT=1690393815:S=ALNI_Ma6kG7fiZ_fy1kMxUUmi2MNsJEhhA',
    '_gid': 'GA1.2.1688706906.1690393816',
    '_cc_id': 'aefa69b06e99889d68d20b2ea5f6177',
    'panoramaId_expiry': '1690480218162',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.paraphraser.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphraser.io/id/parafrase-online',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  data = {
    'data': words,
    'mode': '1',
    'lang': 'id',
    'captcha': '',
  }

  response = requests.post(
    'https://www.paraphraser.io/frontend/rewriteArticleBeta',
    cookies=cookies,
    headers=headers,
    data=data)
  # Remove HTML tags from the response text
  soup = BeautifulSoup(response.text, 'html.parser')
  text_without_tags = soup.get_text()

  # Convert the text without tags to a JSON object
  json_data = json.loads(text_without_tags)
  parafrase = json.dumps(json_data.get('result', {}).get('paraphrase'),
                         indent=4).replace('<span>', '').replace(
                           '</span>', '').replace('<br>', '').replace(
                             '<br/>',
                             '').replace('<br />',
                                         '').replace('<b>',
                                                     '').replace('</b>',
                                                                 '').strip()
  persen = json.dumps(json_data.get('result', {}).get('percent'),
                      indent=4).replace('<span>', '').replace(
                        '</span>',
                        '').replace('<br>', '').replace('<br/>', '').replace(
                          '<br />', '').replace('<b>', '').replace('</b>',
                                                                   '').strip()

  return {'hasil: ': parafrase, 'Persentase: ': persen, 'Status: ': 'Sukses'}


def standard(words, mode='standard'):

  cookies = {
    'ci_session':
    'a%3A6%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%224082c58fb1409f705fdd2e0cecc76064%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22103.144.175.180%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A80%3A%22Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%3B%20rv%3A109.0%29%20Gecko%2F20100101%20Firefox%2F115.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1690396146%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A9%3A%22checkauth%22%3Bs%3A25%3A%22checkparaphrase1690393811%22%3B%7Df0cb826f7a371c8dbcacb0081242ab50',
    '_pbjs_userid_consent_data': '6683316680106290',
    '_sharedID': '3544682c-cbd2-46be-ab04-89dacadcbd6f',
    '_sharedID_last': 'Wed%2C%2026%20Jul%202023%2017%3A50%3A13%20GMT',
    '_lr_retry_request': 'true',
    '_lr_env_src_ats': 'false',
    'cto_bundle':
    'RlCI3F9rUGVJQlJ3TiUyRlk4ajhPVW1sTUlFb0ZYWmE0Z3dCaTdzelhQeFh2N2JLTURIT2RnRmVHaW9BWENRcE5xTHU1aFc3MUFtTWpVcWREVThEV0JjMHNFd0tqM3UlMkJQTkFja1J4RjhhRzc2aGxScHdEOFVnU3lNVGJqWEJ4VUVQQk41JTJCMnRua3Z1QjNvUU14Q0d0ZTU4OVolMkJjdyUzRCUzRA',
    'cto_bidid':
    '4--XuV9iVDBodVM0Z2F5c05DR0N6TGslMkZEZHpLRkQ5Y21qdGVnJTJGeGdmbTE0Tkh4cDRmVW5KU2Q4d3c3NWlQRGdkaCUyQjhJYlpmNnpqN3IyNHBFa2hlVEVVZTRTUnc4R0hVZm1tZGt5QXZlQTNjdm01VmxpMWkyV1lUOTZHYmhUMzVPJTJCMEd0',
    '_ga_Q3XGSV1HE8': 'GS1.1.1690393813.1.0.1690393813.0.0.0',
    '_ga': 'GA1.2.1073571075.1690393814',
    'TawkConnectionTime': '0',
    'twk_idm_key': 'Tt8aWgRm5O4fYTxKWw4vM',
    '_ga_WGYTCZ2REQ': 'GS1.1.1690393814.1.0.1690393814.0.0.0',
    'twk_uuid_62ff0ee954f06e12d88f800b':
    '%7B%22uuid%22%3A%221.7xXuhykE54shomhhNsD76WzcW38KrPglJvS8WDkpJttRsWG3U4Z3grd8zEbcQyHkPOBQsa6Or3fBiq1hsSg5DnDW6TSB1sYY9KZ3DbnAqtmFeQq9E9z1LKRB%22%2C%22version%22%3A3%2C%22domain%22%3A%22paraphraser.io%22%2C%22ts%22%3A1690395354540%7D',
    '__gads':
    'ID=aaa45ab7366b4c7a:T=1690393815:RT=1690393815:S=ALNI_Ma0pKRQabLL3P82pFJwPqexy3GzBw',
    '__gpi':
    'UID=00000c2464462814:T=1690393815:RT=1690393815:S=ALNI_Ma6kG7fiZ_fy1kMxUUmi2MNsJEhhA',
    '_gid': 'GA1.2.1688706906.1690393816',
    '_cc_id': 'aefa69b06e99889d68d20b2ea5f6177',
    'panoramaId_expiry': '1690480218162',
  }

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.paraphraser.io',
    'Connection': 'keep-alive',
    'Referer': 'https://www.paraphraser.io/id/parafrase-online',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
  }

  data = {
    'data': words,
    'mode': '2',
    'lang': 'id',
    'captcha': '',
  }

  response = requests.post(
    'https://www.paraphraser.io/frontend/rewriteArticleBeta',
    cookies=cookies,
    headers=headers,
    data=data)

  # Remove HTML tags from the response text
  soup = BeautifulSoup(response.text, 'html.parser')
  text_without_tags = soup.get_text()

  # Convert the text without tags to a JSON object
  json_data = json.loads(text_without_tags)
  parafrase = json.dumps(json_data.get('result', {}).get('paraphrase'),
                         indent=4).replace('<span>', '').replace(
                           '</span>', '').replace('<br>', '').replace(
                             '<br/>',
                             '').replace('<br />',
                                         '').replace('<b>',
                                                     '').replace('</b>',
                                                                 '').strip()
  persen = json.dumps(json_data.get('result', {}).get('percent'),
                      indent=4).replace('<span>', '').replace(
                        '</span>',
                        '').replace('<br>', '').replace('<br/>', '').replace(
                          '<br />', '').replace('<b>', '').replace('</b>',
                                                                   '').strip()

  return {'hasil: ': parafrase, 'Persentase: ': persen, 'Status: ': 'Sukses'}


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/parafrase', methods=['GET'])
def parafrase():
  user_input = request.args.get('text', '')
  mode = request.args.get('mode', 'formal')  # Default mode is 'formal'

  if mode == 'formal':
    return jsonify(formal(user_input, mode='formal'))

  elif mode == 'regular':
    return jsonify(regular(user_input, mode='regular'))

  elif mode == 'fluency':
    return jsonify(fluency(user_input, mode='fluency'))

  elif mode == 'standard':
    return jsonify(standard(user_input, mode='standard'))

  elif user_input == '' or mode in [
      'formal', 'regular', 'fluency', 'standard'
  ]:
    return jsonify({
      'formal':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=formal',
      'regular':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=regular',
      'fluency':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=fluency',
      'standard':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=standard'
    })
  elif mode != ['formal', 'regular', 'fluency', 'standard']:
    return jsonify({
      'formal':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=formal',
      'regular':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=regular',
      'fluency':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=fluency',
      'standard':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=standard'
    })
  else:
    return jsonify({
      'formal':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=formal',
      'regular':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=regular',
      'fluency':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=fluency',
      'standard':
      request.host_url + 'parafrase?text=MASUKAN+TEKS&mode=standard'
    })


@cross_origin()
@cache.cached(timeout=3600, query_string=True)
@app.route('/fb', methods=['GET'])
def get_fb_links():
  user_input = request.args.get('u')

  if not user_input:
    return jsonify(error='Missing URL parameter: ?u=USER_INPUT'), 400

  parsed_url = urlparse(user_input)
  if not parsed_url.scheme or not parsed_url.netloc:
    return jsonify(error='Invalid URL format.'), 400

  headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept': '*/*',
    'Accept-Language': 'id,en-US;q=0.7,en;q=0.3',
    'Referer': 'https://fbdownloader.app/',
  }

  data = {
    'reCaptchaToken': '',
    'reCaptchaType': '',
    'k_exp': '1692074915',
    'k_token':
    'f0a3c7da35bec6b176a5942e74662fafc8eec8ec11a2afcd5d20fc0a07b4bd04',
    'k_verify': 'false',
    'q': user_input,
    'lang': 'id',
    'web': 'fbdownloader.app',
    'v': 'v2',
  }

  try:
    response = requests.post('https://v3.fbdownloader.app/api/ajaxSearch',
                             headers=headers,
                             data=data)
    response.raise_for_status()
  except requests.exceptions.RequestException as e:
    return jsonify(error='Failed to fetch the page.'), 500

  try:
    json_data = response.json()
    if 'data' in json_data and json_data['status'] == 'ok':
      html_content = json_data['data']
      soup = BeautifulSoup(html_content, 'html.parser')

      video_links = []
      links = soup.find_all('a', href=True)

      for link in links:
        if 'video' in link['href']:
          video_links.append(link['href'])

      if not video_links:
        return jsonify(
          error='No valid video links found on the provided URL.'), 404

      return jsonify(video_links), 200

    else:
      return jsonify(error='Invalid JSON data or no video links found.'), 404

  except ValueError:
    return jsonify(error='Invalid JSON response from the server.'), 500
