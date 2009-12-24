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
from zope.publisher.browser import TestRequest
from zope.security.management import queryInteraction
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile

from zojax.mailtemplate.base import MailTemplateBase


class ErrorMailTemplate(MailTemplateBase):
    
    contentType = u'text/html'
    template = ViewPageTemplateFile('template.pt')

    def __init__(self, context, err):
        self.error = err

        request = None
        interaction = queryInteraction()
        if interaction is not None:
            for request in interaction.participations:
                if request is not None:
                    break

        if request is None:
            request = TestRequest()

        super(ErrorMailTemplate, self).__init__(context, request)

    @property
    def subject(self):
        value = self.error['value']
        portal = getSite()
        title = getattr(portal, 'title', portal.__name__) or portal.__name__
        if title is None:
            title = '[top]'
        return u'Exception "%s": %s: %s'%(
            title, self.error['type'],
            len(value)<100 and value or value[:100] + '...')
