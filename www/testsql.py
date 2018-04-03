#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import orm
from models import User,Blog,Comment
import asyncio
import sys
async def test(loop):
    await orm.create_pool(loop=loop, user='www-data', password='www-data', db='awesome')
    u=User(name='test44',email='test44@test.com',passwd='test',image='about:blank')
    await u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
if loop.is_closed():
    sys.exit(0)