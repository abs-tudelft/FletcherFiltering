import subprocess
from typing import Sequence, Union
from os import PathLike
import re

def ProcessRunner(printer, proc_args: Sequence[Union[bytes, str, PathLike]], *args, **kwargs):
    if 'stdout' in kwargs:
        del kwargs['stdout']

    process = subprocess.Popen(proc_args, *args, **kwargs, stdout=subprocess.PIPE, universal_newlines=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            printer(output.strip())
    rc = process.poll()

    printer("Process exited with code: {}".format(rc))
    return rc


def VivadoHLSProcessRunner(printer, proc_args: Sequence[Union[bytes, str, PathLike]], *args, **kwargs):
    if 'stdout' in kwargs:
        del kwargs['stdout']

    printed_levels = ['ERROR', 'WARNING']

    printed_modules = ['COSIM', 'HLS', 'COMMON']

    test_output = False

    sim_result = None

    line_regex = re.compile(r"(?P<level>[A-Z]+): \[(?P<module>[A-Z]+) (?P<code>[0-9-]+)\] (?P<message>.*)")
    result_regex = re.compile(r"\*\*\* C/RTL co-simulation finished: (?P<result>[A-Za-z0-9]+) \*\*\*")

    process = subprocess.Popen(proc_args, *args, **kwargs, stdout=subprocess.PIPE, universal_newlines=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            matches = line_regex.match(output)
            if matches:
                groupdict = matches.groupdict()

                if groupdict['module'].upper() in printed_modules or groupdict['level'].upper() in printed_levels:
                    printer("{level}: [{module} {code}] {message}".format(**matches.groupdict()))

                if groupdict['module'].upper() == 'COSIM' or groupdict['level'].upper() == 'INFO':
                    result_matches = result_regex.match(groupdict['message'])
                    if result_matches:
                        sim_result = result_matches.group('result').strip()
            elif "== Start ==" in output:
                test_output = True
                printer(output.strip())
            elif "== End ==" in output:
                test_output = False
                printer(output.strip())
            elif test_output:
                printer(output.strip())

    rc = process.poll()

    printer("Process exited with code: {}".format(rc))
    return rc, sim_result

