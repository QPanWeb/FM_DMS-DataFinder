## $Filename$ 
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


""" Adapts the search interface to the lucene library. """


import urllib

from lucene import \
    SimpleFSDirectory, System, File, \
    Document, Field, StandardAnalyzer, IndexSearcher, Version, MultiFieldQueryParser, QueryParser
 
from datafinder.persistence.adapters.lucene import constants    
from datafinder.persistence.adapters.lucene.search.search_restriction_mapping import mapSearchRestriction
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.search.searcher import NullSearcher




__version__ = "$Revision-Id:$" 



class SearchLuceneAdapter(NullSearcher):
    """ Lucene-specific implementation of the search. """
    
    def __init__(self, configuration):
        """ 
        Constructor. 
        
        @param configuration: Lucene-specific configuration parameters.
        @type configuration: L{Configuration<datafinder.persistence.lucene.configuration.Configuration>}
        """
 
        NullSearcher.__init__(self)
        self._configuration = configuration

    def search(self, restrictions):
        """ @see: L{NullPrincipalSearcher<datafinder.persistence.search.searcher.NullSearcher>} """
        
        results = list()
        queryString = mapSearchRestriction(restrictions)
        if self._configuration.luceneIndexUri.startswith("file:///"):
            try:
                self._configuration.env.attachCurrentThread()
                indexDir = SimpleFSDirectory(File(self._configuration.luceneIndexUri.replace("file:///""", "")))
                analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
                searcher = IndexSearcher(indexDir)
                query = QueryParser(Version.LUCENE_CURRENT, "content", analyzer).parse(queryString)
                hits = searcher.search(query, constants.MAX_RESULTS)
                for hit in hits.scoreDocs:
                    doc = searcher.doc(hit.doc)
                    results.append("/%s" % urllib.unquote(doc.get(constants.FILEPATH_FIELD).encode("utf-8")))
                searcher.close()
            except Exception, error:
                errorMessage = "Cannot search items. Reason: '%s'" % error 
                raise PersistenceError(errorMessage)
        elif self._configuration.luceneIndexUri.startswith("http://") or self._configuration.luceneIndexUri.startswith("https://"):
            pass
        else:
            errorMessage = "Cannot search items. Reason: Invalid luceneIndexUri" 
            raise PersistenceError(errorMessage)
        return results