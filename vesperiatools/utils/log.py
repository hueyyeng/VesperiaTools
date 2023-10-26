from typing import TextIO

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTextEdit


class OutLog:
    def __init__(self, edit: QTextEdit, out: TextIO, color: QColor = None):
        """Redirect stdout to QTextEdit widget.

        Parameters
        ----------
        edit : QTextEdit
            The text widget.
        out : TextIO
            Alternate stream (can be the original sys.stdout).
        color : QtGui.QColor or None
            QColor object (i.e. color stderr a different color).

        """
        self.edit = edit
        self.out = out
        self.color = color

    def write(self, text: str):
        """Write stdout print values to QTextEdit widget.

        Parameters
        ----------
        text : str
            Print values from stdout.

        """
        text_color = self.edit.textColor()
        if self.color:
            self.edit.setTextColor(self.color)

        self.edit.insertPlainText(text)
        self.edit.setTextColor(text_color)
        self.out.write(text)

    def flush(self):
        """Flush Outlog when process terminates.

        This prevent Exit Code 120 from happening so the process
        can be finished with Exit Code 0.

        """
        self.out.flush()
