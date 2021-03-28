#! /usr/bin/env python3

import argparse
import os
import gnupg
from datetime import datetime
from pathlib import Path, PurePath
from py7zr import FILTER_LZMA2, SevenZipFile


def valdir(*args):
    try:
        assert args[0].FILETOBACKUP[0].exists()
        args[0].BACKUPLOCATION[0].mkdir(parents=True, exist_ok=True)
        existingbackups = [ x for x in args[0].BACKUPLOCATION[0].iterdir()
        if x.is_file() and x.suffix == '.7z' and x.name.startswith('backup-')]

    except OSError as e:
        print(e.errno)

    return existingbackups


def enformaxbackups(backups,*args):
    oldtonew = list(sorted(backups, key=lambda f: f.name))

    while len(oldtonew) >= args[0].instances:
        backupdel = oldtonew.pop(0)
        backupdel.unlink()
    
    return True


def create7z(*args):
    filters = [{'id': FILTER_LZMA2}]
    backupname = f'backup-{datetime.now().strftime("%Y%m%d%H%M%S")}-{args[0].FILETOBACKUP[0].name}.7z'
    zipfile = SevenZipFile(str(args[0].BACKUPLOCATION[0] / backupname), mode='w', filters=filters)
    try:
        if args[0].FILETOBACKUP[0].is_file():
            zipfile.write(args[0].FILETOBACKUP[0].absolute(), arcname=args[0].FILETOBACKUP[0].name)
            
        elif args[0].FILETOBACKUP[0].is_dir():
            for file in args[0].FILETOBACKUP[0].rglob('*'):
                if file.is_file():
                    zipfile.write(file.absolute(),arcname=str(file.relative_to(args[0].FILETOBACKUP[0])))

    except Exception as e:
        print(e)

    zipfile.close()
    return backupname


def encryptfile(filename,*args):
    try:
        gpg = gnupg.GPG(gpgbinary='gpg2')
        with open(f'{args[0].BACKUPLOCATION[0].resolve()}/{filename}', "r+b") as f:
            encyptedfiles = gpg.encrypt_file(f, recipients=args[0].fingerprint[0], always_trust=True, sign=args[0].fingerprint[0])
            f.seek(0)
            f.write(encyptedfiles.data)
            f.truncate()
        os.rename(f'{args[0].BACKUPLOCATION[0].resolve()}/{filename}',f'{args[0].BACKUPLOCATION[0].resolve()}/{filename}.gpg')


    except ValueError as e:
        print(f'{e.errno}\nFiles Not encrypted')
        pass


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Backup Files and encrypt them with gpg", usage='%(prog)s [options] [Backup File or Directory] [Backup Location]')
        optionalarguments = parser.add_argument_group('optionalarguments', 'List of Optional Arguments')
        primaryuse = parser.add_argument_group('Backup Use')
        primaryuse.add_argument('FILETOBACKUP', type=Path, nargs=1, help='Path of the file to backup')
        primaryuse.add_argument('BACKUPLOCATION', type=Path, nargs=1, help='Path of the location to save backup')
        optionalarguments.add_argument('-e', '--encrypt', action='store_true')
        optionalarguments.add_argument('-f', '--fingerprint',nargs=1,help='Fingerprint to encrypt with', required=True if parser.parse_args().encrypt else False)
        optionalarguments.add_argument('-i','--instances',nargs=1, default=5, help='Number of backupfiles to check for and delete oldest backups over amount')
               
        args = parser.parse_args()
        enformaxbackups(valdir(args),args)
        filename = create7z(args)

        if args.encrypt:
            encryptfile(filename, args)
    
    except argparse.ArgumentError as e:
        print(e)
