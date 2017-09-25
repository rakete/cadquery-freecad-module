"""Adds the ability to open files from disk to the CadQuery FreeCAD module"""
# (c) 2014-2016 Jeremy Wright Apache 2.0 License
import os
import sys
import FreeCAD, FreeCADGui
from PySide import QtGui
import module_locator
import Settings

from pyqode.core.api import Mode
from pyqode.qt import QtCore

class AltGrKeymapMode(Mode):
    def __init__(self, codeedit):
        super(AltGrKeymapMode, self).__init__()
        self.codeedit = codeedit

    def on_state_changed(self, state):
        super(AltGrKeymapMode, self).on_state_changed(state)
        if state:
            self.editor.key_pressed.connect(self._on_key_pressed)
        else:
            self.editor.key_pressed.disconnect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        #FreeCAD.Console.PrintMessage(str(int(event.key())) + "\n")

        if( int(event.modifiers()) & 1073741824 ):
            cursor = self.codeedit.textCursor()

            if( event.key() == QtCore.Qt.Key_Up ):
                cursor.movePosition(QtGui.QTextCursor.Up)

            if( event.key() == QtCore.Qt.Key_Down ):
                cursor.movePosition(QtGui.QTextCursor.Down)

            if( event.key() == QtCore.Qt.Key_Left ):
                cursor.movePosition(QtGui.QTextCursor.Left)

            if( event.key() == QtCore.Qt.Key_Right ):
                cursor.movePosition(QtGui.QTextCursor.Right)

            if( event.key() == QtCore.Qt.Key_End ):
                cursor.movePosition(QtGui.QTextCursor.EndOfLine)

            if( event.key() == QtCore.Qt.Key_Backspace ):
                self.codeedit.textCursor().deletePreviousChar()

            # - does not work, I never get an event when I press AltGr+M = Delete
            # I do get an event when I press AltGr+Delete though
            if( event.key() == QtCore.Qt.Key_Delete ):
                self.codeedit.textCursor().deleteChar()

            self.codeedit.setTextCursor(cursor)


#Distinguish python built-in open function from the one declared here
if open.__module__ == '__builtin__':
    pythonopen = open


def AutoExecute(self):
    """We should be able to pass the Gui.Commands.CadQueryExecuteScript function directly to the file_reloaded
       connect function, but that causes a segfault in FreeCAD. This function is a work-around for that. This
       function is passed to file_reloaded signal and in turn calls the CadQueryExecuteScript.Activated function."""
    try:
        import CadQuery.Gui.Command
        CadQuery.Gui.Command.CadQueryExecuteScript().Activated()
    except:
        import Gui.Command
        Gui.Command.CadQueryExecuteScript().Activated()

def open(filename):
    #All of the Gui.* calls in the Python console break after opening if we don't do this
    FreeCADGui.doCommand("import FreeCADGui as Gui")

    # Make sure that we enforce a specific version (2.7) of the Python interpreter
    ver = hex(sys.hexversion)
    interpreter = "python%s.%s" % (ver[2], ver[4])  # => 'python2.7'

    # If the user doesn't have Python 2.7, warn them
    if interpreter != 'python2.7':
        msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Please install Python 2.7",
            None,
            QtGui.QApplication.UnicodeUTF8)
        FreeCAD.Console.PrintError(msg + "\r\n")

    # The extra version numbers won't work on Windows
    if sys.platform.startswith('win'):
        interpreter = 'python'

    # Set up so that we can import from our embedded packages
    module_base_path = module_locator.module_path()
    libs_dir_path = os.path.join(module_base_path, 'Libs')

    from pyqode.core.modes import FileWatcherMode
    from pyqode.core.modes import RightMarginMode
    from pyqode.python.widgets import PyCodeEdit

    # Make sure we get the right libs under the FreeCAD installation
    fc_base_path = os.path.dirname(os.path.dirname(module_base_path))
    fc_lib_path = os.path.join(fc_base_path, 'lib')

    #Getting the main window will allow us to find the children we need to work with
    mw = FreeCADGui.getMainWindow()

    # Grab just the file name from the path/file that's being executed
    docname = os.path.basename(filename)

    # Set up the text area for our CQ code
    server_path = os.path.join(module_base_path, 'cq_server.py')

    # Windows needs some extra help with paths
    if sys.platform.startswith('win'):
        codePane = PyCodeEdit(server_script=server_path, interpreter=interpreter
                              , args=['-s', fc_lib_path, libs_dir_path])
    else:
        codePane = PyCodeEdit(server_script=server_path, interpreter=interpreter
                              , args=['-s', libs_dir_path])

    codePane.modes.append(AltGrKeymapMode(codePane))

    # Allow easy use of an external editor
    if Settings.use_external_editor:
        codePane.modes.append(FileWatcherMode())
        codePane.modes.get(FileWatcherMode).file_reloaded.connect(AutoExecute)
        codePane.modes.get(FileWatcherMode).auto_reload = True

    # Set the margin to be at 119 characters instead of 79
    codePane.modes.get(RightMarginMode).position = Settings.max_line_length

    codePane.setObjectName("cqCodePane_" + os.path.splitext(os.path.basename(filename))[0])

    mdi = mw.findChild(QtGui.QMdiArea)
    # add a widget to the mdi area
    sub = mdi.addSubWindow(codePane)
    sub.setWindowTitle(docname)
    sub.setWindowIcon(QtGui.QIcon(':/icons/applications-python.svg'))
    sub.show()
    mw.update()

    #Pull the text of the CQ script file into our code pane
    codePane.file.open(filename)

    msg = QtGui.QApplication.translate(
            "cqCodeWidget",
            "Opened ",
            None,
            QtGui.QApplication.UnicodeUTF8)
    FreeCAD.Console.PrintMessage(msg + filename + "\r\n")

    return
