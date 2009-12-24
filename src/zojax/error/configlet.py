##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
import time
from random import random
from rwproperty import getproperty, setproperty

from zope import interface
from zope.proxy import sameProxiedObjects
from zope.component import getUtility
from zope.component.interfaces import IComponentLookup
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import getSite, setSite
from zope.error.interfaces import IErrorReportingUtility
from zope.error.error import RootErrorReportingUtility, \
    cleanup_lock, getFormattedException, getPrintable

from interfaces import IErrorConfiglet
from template import ErrorMailTemplate


class ErrorConfiglet(object):
    interface.implements(IErrorConfiglet)

    @getproperty
    def keep_entries(self):
        return getUtility(
            IErrorReportingUtility).getProperties()['keep_entries']

    @getproperty
    def copy_to_zlog(self):
        return getUtility(
            IErrorReportingUtility).getProperties()['copy_to_zlog']

    @getproperty
    def ignored_exceptions(self):
        return u'\n'.join(getUtility(
                IErrorReportingUtility).getProperties()['ignored_exceptions'])

    @setproperty
    def keep_entries(self, value):
        util = getUtility(IErrorReportingUtility)
        props = util.getProperties()
        props['keep_entries'] = value
        return util.setProperties(**props)

    @setproperty
    def copy_to_zlog(self, value):
        util = getUtility(IErrorReportingUtility)
        props = util.getProperties()
        props['copy_to_zlog'] = value
        return util.setProperties(**props)

    @setproperty
    def ignored_exceptions(self, value):
        util = getUtility(IErrorReportingUtility)
        props = util.getProperties()
        props['ignored_exceptions'] = [s.strip() for s in value.split()]
        return util.setProperties(**props)

    def isAvailable(self):
        if super(ErrorConfiglet, self).isAvailable():
            sm = IComponentLookup(getUtility(IErrorReportingUtility))
            if sameProxiedObjects(sm, getSite().getSiteManager()):
                return True

        return False


# monkey patch
def raising(self, info, request=None):
    now = time.time()
    try:
        strtype = unicode(getattr(info[0], '__name__', info[0]))
        if strtype in self._ignored_exceptions:
            return

        tb_text = None
        tb_html = None
        if not isinstance(info[2], basestring):
            tb_text = getFormattedException(info)
            tb_html = getFormattedException(info, True)
        else:
            tb_text = getPrintable(info[2])

        url = None
        username = None
        req_html = None
        if request:
            # TODO: Temporary fix, which Steve should undo. URL is
            #      just too HTTPRequest-specific.
            if hasattr(request, 'URL'):
                url = request.URL
            username = self._getUsername(request)
            req_html = self._getRequestAsHTML(request)

        strv = getPrintable(info[1])

        log = self._getLog()
        entry_id = str(now) + str(random()) # Low chance of collision

        log.append({
                'type': strtype,
                'value': strv,
                'time': time.ctime(now),
                'id': entry_id,
                'tb_text': tb_text,
                'tb_html': tb_html,
                'username': username,
                'url': url,
                'req_html': req_html,
                })

        context = self.__parent__
        while not ISite.providedBy(context) or context is None:
            context = getattr(context, '__parent__', None)

        if context is not None:
            site = getSite()
            setSite(context)
            configlet = getUtility(IErrorConfiglet)
            emails = configlet.mail_addresses
            setSite(site)

            if emails:
                try:
                    template = ErrorMailTemplate(configlet, log[-1])
                    template.send(emails)
                except:
                    pass

        cleanup_lock.acquire()
        try:
            if len(log) >= self.keep_entries:
                del log[:-self.keep_entries]
        finally:
            cleanup_lock.release()

        if self.copy_to_zlog:
            self._do_copy_to_zlog(now, strtype, str(url), info)
    finally:
        info = None


RootErrorReportingUtility.raising = raising
