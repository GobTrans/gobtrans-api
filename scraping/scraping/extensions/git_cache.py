from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.conf import settings

import os, subprocess

class GitCache(object):
    def __init__(self):
        if settings.getbool('GIT_CACHE_ENABLED'):
            cachedir = settings['HTTPCACHE_DIR']
            if os.path.exists(cachedir):
                self.work_tree = cachedir
            else:
                self.work_tree = os.path.join(os.path.dirname(settings['PROJECT_ROOT']), '.scrapy', cachedir)

            self.basecmd = [
                'git',
                '--git-dir=%s' % os.path.join(self.work_tree, '.git'),
                '--work-tree=%s' % self.work_tree,
            ]

            dispatcher.connect(self.engine_started, signal=signals.engine_started)
            dispatcher.connect(self.engine_stopped, signal=signals.engine_stopped)

    def engine_started(self):
        subprocess.check_call(
            self.basecmd + ['fetch']
        )
        subprocess.check_call(
            self.basecmd + ['reset', '--hard', 'origin/master']
        )

    def engine_stopped(self):
        subprocess.check_call(
            self.basecmd + ['add', '-A']
        )
        subprocess.check_call(
            self.basecmd + ['commit', '-m', 'GitCache: updating', '--allow-empty']
        )
        subprocess.check_call(
            self.basecmd + ['fetch']
        )
        subprocess.check_call(
            self.basecmd + ['merge', 'origin/master']
        )
        subprocess.check_call(
            self.basecmd + ['push', 'origin', 'master']
        )

