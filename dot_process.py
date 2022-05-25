import subprocess
import re


def handle_dot_err_msg(err_msg: str) -> dict:
    """Handle error messages from graphviz dot program."""
    lost_edge_pattern = r"Error: lost (.*) (.*) edge"
    if match := re.findall(lost_edge_pattern, err_msg):
        return {"error_type": "lost_edge", "result": match}
    else:
        return {}


cmd = "dot -Tps bla.txt -o bla.png"

cp = subprocess.run(cmd.split(" "), capture_output=True)

# if cp.returncode:
#     print(cp.stderr)

# err_msg = str(cp.stderr)
err_msg = cp.stderr.decode("utf-8")

# print(err_msg)

# for line in err_msg.split("\n"):
#     print(line)


d = handle_dot_err_msg(err_msg)
print(d)
