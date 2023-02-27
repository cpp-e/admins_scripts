#!/usr/bin/python

'''
users_du: will get how much each user is utilizing in a shared directory
usage:
users_du [path1] [path..n]

Examples:
To get utilization for current path:
users_du

To get utilization for specific path:
users_du /path/to/directory

To get utilization for specific paths:
users_du /full/path1 relative/path2 ../relative/path3
'''

import sys,os
isWin = False
if os.name == 'nt':
    import win32security
    isWin = True
else:
    import pwd

from stat import S_ISDIR,S_ISREG

def du(path):
    lstat = os.lstat(path)
    if S_ISREG(lstat.st_mode):
        uid = win32security.ConvertSidToStringSid(win32security.GetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION).GetSecurityDescriptorOwner()) if isWin else lstat.st_uid
        return {uid: lstat.st_size}
    out = {}
    dirs = [path]
    for p in dirs:
        for f in os.listdir(p):
            file = os.path.join(p, f)
            filestat = os.lstat(file)
            if S_ISDIR(filestat.st_mode):
                dirs.append(file)
            elif S_ISREG(filestat.st_mode):
                uid = win32security.ConvertSidToStringSid(win32security.GetFileSecurity(file, win32security.OWNER_SECURITY_INFORMATION).GetSecurityDescriptorOwner()) if isWin else lstat.st_uid
                if not uid in out:
                    out[uid] = filestat.st_size
                else:
                    out[uid] += filestat.st_size
    return out

paths = ['.'] if len(sys.argv) == 1 else sys.argv[1:]

units = ['', 'K', 'M', 'G', 'T', 'P']
for path in paths:
    out = du(path)
    print(f'{path}:')
    for uid in out:
        try:
            user = '{user[1]}\\{user[0]}'.format(user=win32security.LookupAccountSid(None, win32security.ConvertStringSidToSid(uid))) if isWin else pwd.getpwuid(user).pw_name
        except:
            user = uid
        unit = 0
        size = out[uid]
        while size > 1000:
            size /= 1024.
            unit += 1
        print(f'{size:.2f}{units[unit]}\t{user}')
    print()