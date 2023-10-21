from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit


class OutLog():
    def __init__(self, edit: QTextEdit, out=None, color=None):
        """Redirect stdout to QTextEdit widget.

        Parameters
        ----------
        edit : QTextEdit
            QTextEdit object.
        out : object or None
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
        if self.color:
            text_color = self.edit.textColor()
            self.edit.setTextColor(text_color)

        if self.out:
            self.out.write(text)

        self.edit.moveCursor(QTextCursor.End)
        self.edit.insertPlainText(text)

    def flush(self):
        """Flush Outlog when process terminates.

        This prevent Exit Code 120 from happening so the process
        can be finished with Exit Code 0.

        """
        self.out.flush()
