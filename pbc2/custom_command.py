from pbc2.util import command

def custom_command(**kwargs):

    if not "command" in kwargs:
        return "KwArgs 'command' not present."

    return command.execute_shell_command(kwargs["command"].split(" "))