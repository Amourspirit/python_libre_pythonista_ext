from __future__ import annotations
from typing import cast, TYPE_CHECKING



def main():
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger
    log = OxtLogger(log_name="Webview")
    log.debug("Starting webview")
    try:
        import webview
        window = webview.create_window('Woah dude!', 'https://pywebview.flowrl.com')
        webview.start()
    except Exception as e:
        log.exception(f"Error: {e}")


if __name__ == "__main__":
    main()
