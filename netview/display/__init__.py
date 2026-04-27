from rich.style import Style

STATE_UP = Style(color="green", bold=True)
STATE_DOWN = Style(color="red")
STATE_UNK = Style(color="yellow")

TYPE_COLORS = {
    "ethernet": Style(color="cyan"),
    "wireless": Style(color="bright_blue"),
    "loopback": Style(color="bright_black"),
    "other": Style(color="white"),
}

COL_HEADER = Style(bold=True)
COL_DIM = Style(color="bright_black")
LABEL = Style(color="bright_black")
VALUE = Style(color="default")
