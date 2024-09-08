from pbc2.util import command

def ipcheck(**kwargs):
    # This command only returns the value of ifconfig

    return command.execute_shell_command(["ifconfig"])