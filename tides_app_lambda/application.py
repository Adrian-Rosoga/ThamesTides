from tides import process_from_web


page = '''<!doctype html>
<html>
<head>
<title>Tide - Chelsea</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
</head>
<body>
<p align="center">
</p>
<img src="data:image/png;base64, {image}" style="width: 100%" alt="tide"/>
<button onclick="location.reload(true);" style="font-size:32px">Refresh <i class="fa fa-refresh"></i></button>
</body>
</html>'''


def handler(event, context):

    base64_content = process_from_web('Chelsea', show_plot=False, save_to_file=True,
                                      all_five_days=False, save_plot_png=False, return_base64=True)

    return page.format(image=base64_content.decode("utf-8"))


if __name__ == '__main__':

    handler()
