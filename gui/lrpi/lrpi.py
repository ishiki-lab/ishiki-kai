#!/usr/bin/env python3

import webview, threading

class Api():
    pass

if __name__ == '__main__':
    # t = threading.Thread(target=load_html)
    # t.start()

    api = Api()
    webview.config.gui = "qt"
    webview.create_window('Lushroom Pi', 'www/index.html',
                          js_api=api, width=400, height =600, min_size=(400, 600), confirm_quit=True,
                          text_select=True, resizable=False, debug=False)
