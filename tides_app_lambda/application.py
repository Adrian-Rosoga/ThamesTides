import sys
from tides import process_from_web


page = '''<!DOCTYPE html>
<HTML>
<HEAD>
<TITLE>Tide - Chelsea</TITLE>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
</HEAD>
<BODY>
<P ALIGN="CENTER">
<img src="data:image/png;base64, {image}" STYLE="WIDTH: 100%" alt="Tide" />
</P>
<button style="font-size:32px">Refresh <i class="fa fa-refresh"></i></button>
</BODY>
</HTML>'''


def handler(event, context):

    base64_content = process_from_web('Chelsea', show_plot=False, save_to_file=True,
                                      all_five_days=False, save_plot_png=False, return_base64=True)

    return page.format(image=base64_content.decode("utf-8"))


if __name__ == '__main__':

    handler()
