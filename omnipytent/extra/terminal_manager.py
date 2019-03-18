from omnipytent import task, TERMINAL_PANEL


@task.options
def terminal_manager(ctx):
    try:
        terminals = ctx.cache.terminals
    except AttributeError:
        terminals = ctx.cache.terminals = []

    @ctx.key
    def key(term):
        # TODO: make this also work with vim8
        return term.buffer.vars['term_title']

    terminals[:] = [terminal for terminal in terminals if terminal.alive]

    for term in terminals:
        yield term


@terminal_manager.subtask('new')
def __add_terminal(ctx, command='bash'):
    cache = ctx.task_file.get_task_cache(terminal_manager)
    try:
        terminals = cache.terminals
    except AttributeError:
        terminals = cache.terminals = []
    terminals.append(TERMINAL_PANEL(command))
