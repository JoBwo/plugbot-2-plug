from pbc2.util import command

def nmap_sn(**kwargs):

    if not "subnet" in kwargs:
        return "KwArg 'subnet' missing."

    cmd = ["nmap", "-sn", kwargs["subnet"]]

    return command.execute_shell_command(cmd)