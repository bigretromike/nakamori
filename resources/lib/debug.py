#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cProfile
import pstats
import xbmc
import sys
import nakamoritools as nt

has_pydev = False
has_line_profiler = False
try:
    # noinspection PyUnresolvedReferences
    import line_profiler as line_profiler
    has_line_profiler = True
except ImportError:
    pass


def profile_this(func):
    """
    This can be used to profile any function.
    Usage:
    @profile_this
    def function_to_profile(arg, arg2):
        pass
    """

    def profiled_func(*args, **kwargs):
        """
        a small wrapper
        """
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            stream = nt.StringIO()
            sort_by = 'time'
            ps = pstats.Stats(profile, stream=stream).sort_stats(sort_by)
            ps.print_stats()
            xbmc.log('Profiled Function: ' + func.__name__ + '\n' + stream.getvalue(), xbmc.LOGWARNING)
    return profiled_func


def debug_init():
    """
    start debugger is there is needed one
    also dump argv if spamLog
    :return:
    """
    if nt.addon.getSetting('remote_debug') == 'true':
        try:
            import web_pdb
            web_pdb.set_trace()
        except Exception as ex:
            nt.error('Unable to start debugger, disabling', str(ex))
            nt.addon.setSetting('remote_debug', 'false')
    if nt.addon.getSetting('spamLog') == "true":
        nt.dump_dictionary(sys.argv, 'sys.argv')
