# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#met:
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


"""
Login dialog (including a line for URL-input).
"""


from qt import PYSIGNAL, SLOT, SIGNAL

from datafinder.gui.gen import FullLoginDialog


__version__ = "$Revision-Id:$" 


class LoginDialog(FullLoginDialog.FullLoginDialogForm):

    """
    Login-dialog providing url, username, and password.
    """
    def __init__(self, preferences, parent=None, showurl=True):
        FullLoginDialog.FullLoginDialogForm.__init__(self, modal=True, parent=parent)
        self.connect(self.okPushButton, PYSIGNAL("quit"), SLOT("reject()"))

        # reset URL-combobox:
        self.davserverComboBox.clear()

        # Show or hide URL-combobox:
        self.showUrl(showurl)
        self._preferences = preferences

        self.connect(self.davserverComboBox, SIGNAL("textChanged(const QString&)"), self._uriChangedSlot)
        self.presetUrlList()
        
    def _uriChangedSlot(self, newUri):
        """ Handles the change of the selected URI. """
        
        newUri = unicode(newUri)
        configuration = self._preferences.getConnection(newUri)
        if not configuration is None:
            self.presetUsername(configuration.username)
            self.presetPassword(configuration.password)

    def setAuthenticationRequired(self, authenticationRequired):
        """ Sets the user name and password line edit in accordance to required authentication. """

        self.usernameLineEdit.setEnabled(authenticationRequired)
        self.passwordLineEdit.setEnabled(authenticationRequired)
        self.savePasswordCheckBox.setEnabled(authenticationRequired)

    def showUrl(self, show):
        """
        Make URL-comboxbox visible/invisible.

        @param show: flag
        @type show: boolean
        """

        self.davserverComboBox.setHidden(not(show))
        self.davserverTextLabel.setHidden(not(show))
        self.adjustSize()

    def presetUrl(self, url):
        """
        Initialize URL-input-field.

        @param url: URL of (WebDAV-)server
        @type url: string
        """

        self.davserverComboBox.clear()
        self.davserverComboBox.insertItem(url)
        self.usernameLineEdit.setFocus()

    def presetUrlList(self):
        """
        Initialize URL-input-list/combobox.
        """

        self.davserverComboBox.clear()
        for uri in self._preferences.connectionUris:
            if not uri is None:
                self.davserverComboBox.insertItem(uri)
        self.usernameLineEdit.setFocus()

    def presetUsername(self, user):
        """
        Initialize username-input-field.

        @param user: username
        @type user: string
        """

        self.usernameLineEdit.setText(user or "")
        self.passwordLineEdit.setFocus()

    def presetPassword(self, password):
        """
        Initialize password-input-field.

        @param password: password of user
        @type password: string
        """

        self.passwordLineEdit.setText(password or "")
        self.savePasswordCheckBox.setChecked(not password is None)
        self.passwordLineEdit.setFocus()

    def setSavePassword(self, booleanValue):
        """
        Set "save-password?"-checkbox.

        @param booleanValue: flag
        @type booleanValue: boolean
        """

        self.savePasswordCheckBox.setChecked(booleanValue)

    def getSavePassword(self):
        """
        Check state of "save-password"-checkbox.

        @return: flag if password will be saved
        @rtype: boolean
        """

        return self.savePasswordCheckBox.isChecked()

    def loginOkSlot(self):
        """
        Slot for ok-button.
        A Qt-SIGNAL "updateWebdavServerView" is emitted (url, username,
        password as parameters).
        """

        webdavUrl = unicode(self.davserverComboBox.currentText()).strip()
        webdavUser = unicode(self.usernameLineEdit.text())
        webdavPassword = unicode(self.passwordLineEdit.text())

        self.okPushButton.emit(PYSIGNAL("quit"), ())
        self.okPushButton.emit(PYSIGNAL("updateWebdavServerView"), (webdavUrl, webdavUser, webdavPassword))
