import subprocess

def execute_shell_command(command) -> str:
    try:
        execution = subprocess.run(command, stdout=subprocess.PIPE)
        output = execution.stdout.decode("utf-8")
        return str(output)
    except Exception as e:
        return "Command execution failed:\n{}".format(str(e))