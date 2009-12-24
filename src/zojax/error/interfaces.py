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
from zope import interface, schema
from zojax.widget.list.field import SimpleList


class IErrorConfiglet(interface.Interface):
    """ error utility configlet """

    keep_extries = schema.Int(
        title = u'Numver of exceptions to keep',
        default = 20,
        required = True)

    copy_to_zlog = schema.Bool(
        title = u'Copy exceptions to the event log',
        default = False,
        required = True)

    ignored_exceptions = schema.Text(
        title = u'Ignored exception types',
        default = u'',
        missing_value = u'',
        required = False)

    mail_addresses = SimpleList(
        title = u'Send errors to mail',
        description = u'Enter emails, each email on new line.',
        default = [],
        missing_value = [],
        required = False)
