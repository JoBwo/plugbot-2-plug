from pbc2.util import command


def ping(destination=None, **kwargs):
    if destination is None:
        destination = "8.8.8.8"

    cmd = ["ping", destination]

    # We evaluate additional kwargs

    if "count" in kwargs:
        cmd.append("-c")
        cmd.append(str(kwargs["count"]))
    else:
        cmd.append("-c")
        cmd.append("1")

    if "ttl" in kwargs:
        cmd.append("-m")
        cmd.append(str(kwargs["ttl"]))

    if "size" in kwargs:
        cmd.append("-s")
        cmd.append(str(kwargs["size"]))

    if "tos" in kwargs:
        cmd.append("-z")
        cmd.append(str(kwargs["tos"]))

    return command.execute_shell_command(cmd)
