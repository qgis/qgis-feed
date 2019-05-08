# coding=utf-8
""""QGIS News app signals

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2019-05-08'
__copyright__ = 'Copyright 2019, ItOpen'

def setup_group(sender, **kwargs):
    """Create qgisfeedentry_authors group and assign permissions"""

    from django.contrib.auth.models import User, Group, Permission
    group, is_new = Group.objects.get_or_create(name='qgisfeedentry_authors')
    if is_new:
        for perm in ('view_qgisfeedentry', 'add_qgisfeedentry'):
            group.permissions.add(Permission.objects.get(codename=perm))

    for staff_user in User.objects.filter(is_staff=True, is_superuser=False):
        group.user_set.add(staff_user)

