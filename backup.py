#! /usr/bin/env python3.6

import os
import gnupg
from datetime import datetime
from pathlib import Path, PurePath
from py7zr import FILTER_LZMA2, SevenZipFile


BACKUPFILE = '/home/slacks/test'
BACKUPDIR = '/home/slacks/backups'
BACKUPAMOUNT = 5
filetobackup = Path(BACKUPFILE)
directorytobackto = Path(BACKUPDIR)


def valdir():
    try:
        assert filetobackup.exists()
        directorytobackto.mkdir(parents=True, exist_ok=True)
        existingbackups = [ x for x in directorytobackto.iterdir()
        if x.is_file() and x.suffix == '.7z' and x.name.startswith('backup-')]

    except OSError as e:
        print(e.errno)

    return existingbackups


def enformaxbackups(backups=valdir()):
    oldtonew = list(sorted(backups, key=lambda f: f.name))

    while len(oldtonew) >= BACKUPAMOUNT:
        backupdel = oldtonew.pop(0)
        backupdel.unlink()
    
    return True


def create7z():
    filters = [{'id': FILTER_LZMA2}]
    backupname = f'backup-{datetime.now().strftime("%Y%m%d%H%M%S")}-{filetobackup.name}.7z'
    zipfile = SevenZipFile(str(directorytobackto / backupname), mode='w', filters=filters)
    try:
        if filetobackup.is_file():
            zipfile.write(filetobackup.absolute(), arcname=filetobackup.name)
            
        elif filetobackup.is_dir():
            for file in filetobackup.rglob('*'):
                if file.is_file():
                    zipfile.write(file.absolute(),arcname=str(file.relative_to(filetobackup)))

    except Exception as e:
        print(e)

    zipfile.close()
    encryptfile(backupname)


def encryptfile(filename):
    fingerprint = 'DE5AE8073361E11B6ED3B629014E4BA24373BA83'
    try:
        gpg = gnupg.GPG(gpgbinary='gpg2')
        with open(f'{directorytobackto.resolve()}/{filename}', "r+b") as f:
            encyptedfiles = gpg.encrypt_file(f, recipients=fingerprint, always_trust=True, sign=fingerprint)
            f.seek(0)
            f.write(encyptedfiles.data)
            f.truncate()
        os.rename(f'{directorytobackto.resolve()}/{filename}',f'{directorytobackto.resolve()}/{filename}.gpg')


    except ValueError as e:
        print(f'{e.errno}\nFiles Not encrypted')
        pass






if __name__ == '__main__':
    BACKUPFILE = '/home/slacks/test'
    BACKUPDIR = '/home/slacks/backups'
    BACKUPAMOUNT = 5
    filetobackup = Path(BACKUPFILE)
    directorytobackto = Path(BACKUPDIR)
    enformaxbackups()
    create7z()