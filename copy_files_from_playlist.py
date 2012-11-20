#!/usr/bin/env python
import csv
import getpass
import os
import shutil
import sys


import os, stat

def get_boot_volume():
    dirlist = "/Volumes"
    files = os.listdir(dirlist)
    for folder in files:
        cur_item = os.path.join(dirlist, folder)
        ret = os.lstat(cur_item)[stat.ST_MODE]
        if stat.S_ISLNK(ret):
            return "%s/" % cur_item


class Track(object):
    """A track object"""

    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop('title')
        self.artist = kwargs.pop('artist')
        self._location = kwargs.pop('location')
        self.library_folder = os.path.join(get_boot_volume(), 'Users', getpass.getuser(), 'Music/iTunes/iTunes Music')

    def __repr__(self):
        return "<Track: %s - %s>" % (self.artist, self.title)

    @property
    def source_location(self):
        """Convert the weird colon seperated location into a real file location"""
        return '/' + '/'.join(['Volumes'] + self._location.split(':'))

    def track_path_part(self):
        return self.source_location.replace(self.library_folder + '/', '')

    def destination_location(self, destination_folder):
        return os.path.join(destination_folder, self.track_path_part())

    def source_file_exists(self):
        return os.path.exists(self.source_location)

    def destination_file_exists(self, destination_folder):
        return os.path.exists(self.destination_location(destination_folder))

    def artist_directory_part(self):
        return self.track_path_part().split('/')[0]

    def album_directory_part(self):
        return self.track_path_part().split('/')[1]


class TrackCopier(object):

    def __init__(self, tracks, dest_folder):
        self.tracks = tracks
        self.dest = dest_folder

    def copy(self, simulate=False):
        if simulate:
            self.simulate()
        else:
            copied = 0
            print "Processing %s tracks" % len(self.tracks)
            for track in self.tracks:
                if track.source_file_exists():
                    # Artist directory
                    artist_path = os.path.join(dest, track.artist_directory_part())
                    if not os.path.exists(artist_path):
                        print "Creating folder: %s" % artist_path
                        os.mkdir(artist_path)

                    # Album directory
                    album_path = os.path.join(dest, artist_path, track.album_directory_part())
                    if not os.path.exists(album_path):
                        print "Creating folder: %s" % album_path
                        os.mkdir(album_path)

                    # File
                    if not os.path.exists(track.destination_location(dest)):
                        print "Copying track %s" % track.source_location
                        shutil.copy(track.source_location, track.destination_location(dest))
                        copied += 1
            print "Tracks copied: %s" % copied

    def simulate(self):
        for track in self.tracks:
            if not track.source_file_exists():
                continue

            if not track.destination_file_exists(self.dest):
                print "Would copy file from %s to %s" % (track.source_location, track.destination_location(self.dest))


def main(*args, **kwargs):
    tracks = []
    with open(kwargs.pop('playlist'), 'rU') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            tracks.append(
                Track(
                    title=row['Name'],
                    artist=row['Artist'],
                    location=row['Location']
                )
            )

    copier = TrackCopier(tracks, kwargs.pop('dest'))
    copier.copy()


if __name__ == '__main__':
    try:
        playlist = os.path.expanduser(sys.argv[1])
    except IndexError:
        sys.stderr.write("Playlist file required\n")
        sys.exit(1)

    try:
        dest = os.path.expanduser(sys.argv[2])
    except IndexError:
        sys.stderr.write("Destination directory required\n")
        sys.exit(1)
    main(playlist=playlist, dest=dest)
        