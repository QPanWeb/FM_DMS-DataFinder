#
# $Filename$$
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
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
Provides QStandardItem implementations for principals and access levels.
"""


from PyQt4.QtGui import QIcon, QStandardItem, QComboBox

from datafinder.core.item.privileges.principal import USER_PRINCIPAL_TYPE
from datafinder.core.item.privileges.privilege import ACCESS_LEVELS


__version__ = "$Revision-Id$" 


class PrincipalItem(QStandardItem):
    """ Principal-specific item. """

    _groupIcon = None
    _userIcon = None
    
    def __init__(self, principal):
        """ Constructor.
        
        @param principal: The associated principal.
        @type principal: L{<Principal>datafinder.core.principal.Principal}
        """
        
        QStandardItem.__init__(self, principal.displayName)
        self._initIcons()
        
        self.principal = principal

        if principal.type == USER_PRINCIPAL_TYPE:
            self.setIcon(self._userIcon)
        else:
            self.setIcon(self._groupIcon)
        self.setEditable(False)
        self.setToolTip(self.principal.type.displayName)
        
    def _initIcons(self):
        """ Initializes the icons. """
        
        if self._groupIcon is None:
            self._groupIcon = QIcon(":/icons/icons/users24.png")
        if self._userIcon is None:
            self._userIcon = QIcon(":/icons/icons/user24.png")


class AccessLevelItem(QStandardItem):
    """ Access level item. """

    accessLevels = [accessLevel for accessLevel in ACCESS_LEVELS]

    def __init__(self, level, isReadOnly=False):
        """ Constructor.
        
        @param level: The associated access level constant.
        @type level: L{_AccessLevel<datafinder.core.item.
            privileges.privilege._AccessLevel>}
        @param isReadOnly: Flag indicating whether the value 
            should be changeable.
        @type isReadOnly: C{bool}
        """
        
        QStandardItem.__init__(self, "")
        self._level = None
        self.setEditable(not isReadOnly)
        self.level = level

    def createEditor(self, parent):
        """ Returns the correctly initialized editor for the item value. 
        
        @param parent: Parent widget of the created editor widget.
        @type parent: L{QWidget<PyQt4.QtGui.QWidget>}
        
        @return: Currently a combination box.
        @rtype: L{QComboBox<PyQt4.QtGui.QComboBox>}
        """
        
        editor = QComboBox(parent)
        currentName = unicode(self.text())
        index = 0
        for number, level in enumerate(self.accessLevels):
            editor.addItem(level.displayName)
            if level.displayName == currentName:
                index = number
        editor.setCurrentIndex(index)
        editor.setEditable(False)
        return editor

    def _getLevel(self):
        return self._level

    def _setLevel(self, newLevel):
        if self._level != newLevel:
            self._level = newLevel
            self.setText(newLevel.displayName)
            self.setToolTip(newLevel.description)
    level = property(_getLevel, _setLevel)
