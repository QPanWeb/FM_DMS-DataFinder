# $Filename$ 
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
Test cases for the data store handler.
"""


import unittest
from xml.parsers.expat import ExpatError

from datafinder.core.configuration.datastores import handler, constants
from datafinder.core.configuration.gen import datastores
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class DataStoreHandlerTestsCase(unittest.TestCase):
    """ Test cases for the data store handler. """
    #pylint: disable=R0904
    
    def setUp(self):
        """ Creates object under test. """
        
        self._parseStringMock = SimpleMock()
        datastores.parseString = self._parseStringMock
        self._createFileStorerMock = SimpleMock()
        handler.createFileStorer = self._createFileStorerMock
        self._fileStorerMock = SimpleMock()
        self._datastoreHandler = handler.DataStoreHandler(self._fileStorerMock)
    
    def testCreate(self):
        """ Tests the creation of the data store configuration area. """
        
        self._datastoreHandler.create(dataUri="uri")
        self.assertEquals(len(self._datastoreHandler.datastores), 1)
        self.assertEquals(self._datastoreHandler.datastores[0].url, "uri")
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._datastoreHandler.create, dataUri="uri")
        
    def testLoad(self):
        """ Tests the initialization of the data store handler. """
        
        self._fileStorerMock.methodNameResultMap = {"exists": (True, None), "readData": (SimpleMock(""), None)}
        self._parseStringMock.value = datastores.datastores([datastores.default(name="name1", storeType=constants.DEFAULT_STORE),
                                                             datastores.default(name="name2", storeType=constants.DEFAULT_STORE)])
        self._datastoreHandler.load()
        self.assertEquals(len(self._datastoreHandler.datastores), 2)
    
        self._fileStorerMock.methodNameResultMap = {"exists": (False, None)}
        self.assertRaises(ConfigurationError, self._datastoreHandler.load)
        
        self._fileStorerMock.methodNameResultMap = {"exists": (None, PersistenceError(""))}
        self.assertRaises(ConfigurationError, self._datastoreHandler.load)
        
        self._fileStorerMock.methodNameResultMap = {"exists": (True, None), "readData": (None, PersistenceError(""))}
        self.assertRaises(ConfigurationError, self._datastoreHandler.load)
        
        self._fileStorerMock.methodNameResultMap = {"exists": (True, None), "readData": (SimpleMock(""), None)}
        self._parseStringMock.error = ExpatError("")
        self.assertRaises(ConfigurationError, self._datastoreHandler.load)
        
        self._fileStorerMock.methodNameResultMap = {"exists": (True, None), "readData": (SimpleMock(""), None)}
        self._parseStringMock.error = ValueError("")
        self.assertRaises(ConfigurationError, self._datastoreHandler.load)
        
    def testStore(self):
        """ Tests the storage of the data store configuration. """
        
        self._datastoreHandler.store()
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._datastoreHandler.store)
        
    def testDataStoreCreation(self):
        """ Tests the data store factory method. """
        
        datastore = self._datastoreHandler.createDataStore()
        self.assertFalse(self._datastoreHandler.hasDataStore(datastore.name))
        self.assertNotEquals(datastore.name, None)
        self.assertEquals(datastore.storeType, constants.DEFAULT_STORE)
        
        datastore = self._datastoreHandler.createDataStore("name", None, 
                                                           "iconName", "url", True, "owner")
        self.assertEquals(datastore.name, "name")
        self.assertEquals(datastore.iconName, "iconName")
        self.assertEquals(datastore.storeType, constants.DEFAULT_STORE)
        self.assertEquals(datastore.url, "url")
        self.assertEquals(datastore.isDefault, True)
        self.assertEquals(datastore.owner, "owner")
        
        datastore = self._datastoreHandler.createDataStore("name", constants.FTP_STORE, 
                                                           "iconName", "url", True, "owner")
        self.assertEquals(datastore.name, "name")
        self.assertEquals(datastore.iconName, "iconName")
        self.assertEquals(datastore.storeType, constants.FTP_STORE)
        self.assertEquals(datastore.url, "url")
        self.assertEquals(datastore.isDefault, True)
        self.assertEquals(datastore.owner, "owner")
        
        self.assertRaises(ConfigurationError, self._datastoreHandler.createDataStore, storeType="unknown")

    def testImport(self):
        """ Tests the import of data store configurations. """
        
        self._createFileStorerMock.value = SimpleMock(SimpleMock())
        self._parseStringMock.value = datastores.datastores([datastores.default(name="name1", storeType=constants.DEFAULT_STORE),
                                                             datastores.default(name="name2", storeType=constants.DEFAULT_STORE)])
        self._datastoreHandler.importDataStores("/local/file/path")
        self.assertEquals(len(self._datastoreHandler.datastores), 2)
        
        self._parseStringMock.error = ExpatError("")
        self.assertRaises(ConfigurationError, self._datastoreHandler.importDataStores, "/local/file/path")
        self.assertEquals(len(self._datastoreHandler.datastores), 2)
        
        self._createFileStorerMock.value = SimpleMock(error=PersistenceError(""))
        self.assertRaises(ConfigurationError, self._datastoreHandler.importDataStores, "/local/file/path")
        self.assertEquals(len(self._datastoreHandler.datastores), 2)
        
        self._createFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._datastoreHandler.importDataStores, "/local/file/path")
        self.assertEquals(len(self._datastoreHandler.datastores), 2)
        
    def testExport(self):
        """ Tests the export of data store configurations. """
        
        self._createFileStorerMock.value = SimpleMock()
        self._datastoreHandler.exportDataStores("/local/file/path")
    
        self._createFileStorerMock.value = SimpleMock(error=PersistenceError(""))
        self.assertRaises(ConfigurationError, self._datastoreHandler.exportDataStores, "/local/file/path")
        
        self._createFileStorerMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._datastoreHandler.exportDataStores, "/local/file/path")
        
    def testDataStoreHandling(self):
        """  Tests the management of data store configurations. """
        
        dataStore = self._datastoreHandler.createDataStore()
        self.assertFalse(self._datastoreHandler.hasDataStore(dataStore.name))
        self.assertEquals(self._datastoreHandler.getDataStore(dataStore.name), None)
        self._datastoreHandler.addDataStore(dataStore)
        self.assertTrue(self._datastoreHandler.hasDataStore(dataStore.name))
        self.assertEquals(self._datastoreHandler.getDataStore(dataStore.name), dataStore)
        self.assertEquals(len(self._datastoreHandler.defaultDatastores), 0)
        anotherDataStore = self._datastoreHandler.createDataStore()
        anotherDataStore.isDefault = True
        self._datastoreHandler.addDataStore(anotherDataStore)
        self.assertEquals(len(self._datastoreHandler.datastores), 2)
        self.assertEquals(len(self._datastoreHandler.defaultDatastores), 1)
        
        self._datastoreHandler.removeDataStore(dataStore.name)
        self._datastoreHandler.removeDataStore(dataStore.name)
        self.assertEquals(len(self._datastoreHandler.datastores), 1)
        self._datastoreHandler.removeDataStore(anotherDataStore.name)
        self.assertEquals(len(self._datastoreHandler.datastores), 0)
        
        self._datastoreHandler.setDataStores([dataStore, anotherDataStore])
        self.assertEquals(len(self._datastoreHandler.datastores), 2)
    
    def testDataStoreGetter(self): 
        """ Tests the read-only properties of the handler allowing access to the data store configurations. """
        # Fine for testing: pylint: disable=W0212
        
        datastores_ = {"tsm": SimpleMock(storeType=constants.TSM_CONNECTOR_STORE, isMigrated=False),
                      "file": SimpleMock(storeType=constants.FILE_STORE, isMigrated=False),
                      "ftp": SimpleMock(storeType=constants.FTP_STORE, isMigrated=False),
                      "gridftp": SimpleMock(storeType=constants.GRIDFTP_STORE, isMigrated=False),
                      "default": SimpleMock(storeType=constants.DEFAULT_STORE, isMigrated=False),
                      "webdav": SimpleMock(storeType=constants.WEBDAV_STORE, isMigrated=False),
                      "offline": SimpleMock(storeType=constants.OFFLINE_STORE, isMigrated=False),
                      "s3": SimpleMock(storeType = constants.S3_STORE, isMigrated=False),
                      "svn": SimpleMock(storeType = constants.SUBVERSION_STORE, isMigrated=False),
                      "svn_migrated": SimpleMock(storeType = constants.SUBVERSION_STORE, isMigrated=True)}
        self._datastoreHandler._datastores = datastores_
        
        self.assertEquals(len(self._datastoreHandler.datastores), 10)
        self.assertEquals(len(self._datastoreHandler.archiveDatastores), 1)
        self.assertEquals(len(self._datastoreHandler.onlineDatastores), 7)
        self.assertEquals(len(self._datastoreHandler.offlineDatastores), 1)
        self.assertEquals(len(self._datastoreHandler.externalDatastores), 7)
