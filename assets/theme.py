"""Shared palette and type stacks for the generated profile SVGs.

Both the hero and the streak strip import from here so a colour change lands in
one place and the two graphics can never drift apart.

Backgrounds match GitHub's canvas so the graphics read as part of the page
rather than as cards pasted on top of it.
"""

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "box": "#161b22",
        "line": "#30363d",
        "wire": "#3d444d",
        "text": "#e6edf3",
        "muted": "#7d8590",
        "faint": "#484f58",
        "accent": "#d99a4e",
        "accent_soft": "#3a2e1d",
    },
    "light": {
        "bg": "#ffffff",
        "box": "#f6f8fa",
        "line": "#d0d7de",
        "wire": "#c2c8cf",
        "text": "#1f2328",
        "muted": "#656d76",
        "faint": "#8c959f",
        "accent": "#a86616",
        "accent_soft": "#fdf3e5",
    },
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# Left and right text margins, shared by both graphics so their rules line up.
MARGIN_L, MARGIN_R = 56, 944
