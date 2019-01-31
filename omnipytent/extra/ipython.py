def add_ipython_capabilities(terminal):
    def send_raw(text):
        rows = text.splitlines()
        while rows and (not rows[0] or rows[0].isspace()):
            rows.pop(0)
        terminal.write('\x0f%s\x04\x1b\n' % '\n'.join(rows))
    terminal.send_raw = send_raw
