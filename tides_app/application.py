import os
from flask import Flask, send_from_directory
from tides import process_from_web


# EB looks for an 'application' callable by default.
application = Flask(__name__, static_url_path='')


page = """<!doctype html>
<html>
<head>
<title>Tide - Chelsea</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
</head>
<body bgcolor="white">
<p align="center">
<img src="data:image/png;base64, {image}" style="width: 100%" alt="tide"/>
</p>
<button onclick="location.reload(true);" style="font-size:32px">Refresh <i class="fa fa-refresh"></i></button>
</body>
</html>"""


@application.route('/')
def process():
    base64_content = process_from_web('Chelsea', show_plot=False, save_to_file=True, all_five_days=False,
                      save_plot_png=True, return_base64=True)
    return page.format(image=base64_content.decode("utf-8"))


@application.route('/plot.png')
def root():
    return send_from_directory(application.root_path, 'plot.png')


def main():

    # Remove in production
    # application.debug = True
    application.run(host="0.0.0.0")


if __name__ == "__main__":

    main()
