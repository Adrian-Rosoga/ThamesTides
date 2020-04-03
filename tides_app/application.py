import os
from flask import Flask, send_from_directory
from tides import process_from_web


# EB looks for an 'application' callable by default.
application = Flask(__name__, static_url_path='')


page = """<HTML>
<HEAD>
<TITLE>Tide - Chelsea</TITLE>
</HEAD>
<BODY BGCOLOR="BLACK">
<P ALIGN="CENTER">
<IMG SRC="plot.png" STYLE="WIDTH: 100%" ALT="NO IMAGE!" WIDTHX="840" HEIGHTX="420">
</P>
</BODY>
</HTML>"""


@application.route('/')
def process():
    process_from_web('Chelsea', show_plot=False, save_to_file=True, all_five_days=False)
    return page


@application.route('/plot.png')
def root():
    return send_from_directory(application.root_path, 'plot.png')


def main():

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host="0.0.0.0")


if __name__ == "__main__":

    main()