#
# Created: 26.11.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: icon_provider.py 4479 2010-03-02 21:55:09Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements an icon provider for the repository related icon data. 
"""


import sys

from PyQt4.QtGui import QFileIconProvider, QIcon, QPixmap, QPainter
from PyQt4.QtCore import QRectF

from datafinder.core.configuration.datamodel.constants import DEFAULT_DATATYPE_ICONNAME
from datafinder.core.configuration.datastores.constants import DEFAULT_STORE_ICONNAME
from datafinder.core.item.data_persister.constants import ITEM_STATE_ARCHIVED, \
                                                          ITEM_STATE_ARCHIVED_MEMBER, ITEM_STATE_ARCHIVED_READONLY, \
                                                          ITEM_STATE_MIGRATED, ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE, \
                                                          ITEM_STATE_INACCESSIBLE


__version__ = "$LastChangedRevision: 4479 $"


class IconProvider(object):
    """ Provides icons for repository items or icon names. """
    
    def __init__(self, iconHandler):
        """ Constructor. """
        
        self._iconHandler = iconHandler
        self._loadedIcons = dict()
        self._decoratedLinkIcons = dict()
        self._decoratedNotRetrievableDataIcons = dict()
        self._decoratedArchiveIcons = dict()
        self._decoratedUnavailableIcons = dict()
        
        qtIconProvider = QFileIconProvider()
        self._defaultDriveIcon = qtIconProvider.icon(QFileIconProvider.Drive)
        self._defaultFolderIcon = qtIconProvider.icon(QFileIconProvider.Folder)
        self._defaultFileIcon = qtIconProvider.icon(QFileIconProvider.File)
        self._defaultDataTypeIcon = QIcon(":/icons/icons/dataType16.png")
        self._defaultDataStoreIcon = QIcon(":/icons/icons/dataStore16.png")
        
    def iconForDataType(self, dataType):
        """ Retrieves an icon for the icon name. """

        icon = None
        if not dataType is None:
            icon = self._determineIcon(dataType.iconName, self._defaultDataTypeIcon)
        return icon
            
    def iconForDataStore(self, dataStore):
        """ Retrieves an icon for the given data store instance. """
        
        icon = None
        if not dataStore is None:
            icon = self._determineIcon(dataStore.iconName, self._defaultDataStoreIcon)
        return icon
        
    def _determineIcon(self, iconName, defaultIcon=None):
        """ Determines the icon identified by the given name. """
            
        icon = None
        if iconName in self._loadedIcons:
            icon = self._loadedIcons[iconName]
        else:
            registeredIcon = self._iconHandler.getIcon(iconName)
            if registeredIcon is None and not defaultIcon is None:
                icon = defaultIcon
                self._loadedIcons[iconName] = defaultIcon
            elif not registeredIcon is None:
                icon = QIcon(registeredIcon.smallIconLocalPath)
                self._loadedIcons[iconName] = icon
        return icon
        
    def iconForItem(self, item):
        """ Retrieves an icon for the item. """
        
        icon = None
        if not item.iconName is None:
            icon = self._determineIcon(item.iconName)
        icon = icon or self._defaultIcon(item)
        return self._handleItemDecoration(item, icon)
        
    def _handleItemDecoration(self, item, icon):
        """ Checks whether a specific icon decoration is required and returns the modified icon. """
        
        iconId = id(icon)
        if item.state in [ITEM_STATE_ARCHIVED, ITEM_STATE_ARCHIVED_MEMBER, ITEM_STATE_ARCHIVED_READONLY]:
            if iconId in self._decoratedArchiveIcons:
                icon = self._decoratedArchiveIcons[iconId]
            else:
                icon = self._decorateIcon(icon, ":/icons/icons/archive16.png")
                self._decoratedArchiveIcons[iconId] = icon
        elif item.state in [ITEM_STATE_MIGRATED, ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE]:
            if iconId in self._decoratedUnavailableIcons:
                icon = self._decoratedUnavailableIcons[iconId]
            else:
                icon = self._decorateIcon(icon, ":/icons/icons/migrated16.png")
                self._decoratedUnavailableIcons[iconId] = icon
        elif item.state in [ITEM_STATE_INACCESSIBLE]:
            if iconId in self._decoratedNotRetrievableDataIcons:
                icon = self._decoratedNotRetrievableDataIcons[iconId]
            else:
                icon = self._decorateIcon(icon, ":/icons/icons/cd16.png")
                self._decoratedNotRetrievableDataIcons[iconId] = icon
        elif item.isLink:
            if iconId in self._decoratedLinkIcons:
                icon = self._decoratedLinkIcons[iconId]
            else:
                icon = self._decorateIcon(icon, ":/icons/icons/link16.png")
                self._decoratedLinkIcons[iconId] = icon
        return icon
            
    def _defaultIcon(self, item):
        """ Determines a default icon for the given item. """
        
        if item.isLink and not item.linkTarget is None:
            item = item.linkTarget
            
        if item.name.endswith(":") and sys.platform == "win32":
            icon = self._defaultDriveIcon
        elif item.isCollection:
            if item.isManaged:
                icon = self._defaultDataTypeIcon
            else:
                icon = self._defaultFolderIcon
        else:
            icon = self._defaultFileIcon
        return icon

    @staticmethod
    def _decorateIcon(originalIcon, iconPath):
        """ Decorates the icon with the icon identified by C{iconPath}. """

        originalPm = originalIcon.pixmap(16)
        painter = QPainter(originalPm)
        pm = QPixmap(iconPath)
        targetRect = QRectF(0.0, 8.0, 8.0, 8.0)
        sourceRect = QRectF(0.0, 0.0, 16, 16)
        painter.drawPixmap(targetRect, pm, sourceRect)
        painter.end()
        return QIcon(originalPm)
