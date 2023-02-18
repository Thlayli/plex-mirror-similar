import collections
from tqdm import tqdm
from plexapi.mixins import EditFieldMixin, SimilarArtistMixin
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import PlexApiException
import requests
import argparse

# start user variables section

server_name = 'xxxxxxxx'
token = 'xxxxxxxxxxxxxxxxxxxx'
library_number = ##

# a list of find-replace pairs, e.g. [['old_one','new_one'],['old_two','new_two]]
tags_to_rename = []

# end user variables section

parser = argparse.ArgumentParser()
parser.add_argument('-range', nargs='?', default='',  help='date range or start date')
parser.add_argument('-search', nargs='?', default='', help='artist or album search string')
parser.add_argument('-unlink', nargs='?', default='', help='artist to remove from all similar lists')
args = parser.parse_args()
date_range = args.range
search_string = args.search
artist_to_remove = args.unlink

account = MyPlexAccount(token)
plex = account.resource(server_name).connect()
library = plex.library.sectionByID(library_number)
plex_filters = {"title": search_string, "addedAt>>": date_range} if date_range != '' else {"title": search_string}
duplicate_artists = collections.OrderedDict()
selected_artists = collections.OrderedDict()
similar_as_artist = collections.OrderedDict()
referenced_artists = set()

try:

  # get list of duplicate artist names to skip
  for artist in tqdm(library.search(sort="titleSort:asc",filters={"collection": "Duplicate Name"},libtype='artist'), desc="Checking for Duplicate Names"):
    duplicate_artists.setdefault(artist.key,artist.title)
  tqdm.write(str(len(duplicate_artists))+" duplicate-named artists")

  # check recently added artists and albums
  for artist in tqdm(library.search(sort="titleSort:asc",filters=plex_filters,libtype='artist'), desc="Looking for Artists"):
    selected_artists.setdefault(artist.key,artist.title)
    
  for album in tqdm(library.search(sort="artist.titleSort:asc",filters=plex_filters,libtype='album'), desc="Looking for Albums"):
    selected_artists.setdefault(album.parentKey,album.parentTitle)

  for (artist_key,artist_title) in tqdm(selected_artists.items(), desc="Reading tags"):

    try:
      full_item = library.fetchItem(artist_key)

      # coll_list = str(full_item.collections)
      # if len(full_item.collections) > 0:
        # for collection in full_item.collections:
          # if 'Duplicate-Name' in str(collection):
      if not artist_key in duplicate_artists:
            
        # tqdm.write(full_item.title)
        referenced_artists.add(full_item.title)
        for sa in full_item.similar:
          # tqdm.write('-'+str(sa.tag))
          tag = sa.tag.replace("Similar:/library/sections/"+library_number+":","")
          # for ts in library.search(sa.tag):
            # tqdm.write('--'+ts.title)
          if not tag in [v for (k,v) in duplicate_artists.items()]:
            similar_as_artist.setdefault(tag, [])
            similar_as_artist[tag].append(full_item.title.lower())
      # else:
        # tqdm.write('Skipping '+artist_title)
        
    except Exception as err:
        tqdm.write('Error: '+str(err))
        continue

    # except Exception as err:
      # tqdm.write('Skipping '+artist_title)
      # continue
  
  if search_string == '' and date_range == '':
    active_similar = {key: value for (key, value) in sorted(similar_as_artist.items()) if key in referenced_artists}
    print(len(active_similar),'library artists match',len(set(similar_as_artist)),'listed similar artists')
  else:
    active_similar = {key: value for (key, value) in sorted(similar_as_artist.items())}
    print('Filter active: trying all',len(similar_as_artist),'listed similar artists')

  

  changed = 0

  for (k,v) in tqdm(active_similar.items(), desc="Changing tags"):
    
    # tqdm.write(str(k))
    
    try:
    
      artists = library.search(k)
      for artist in artists:
        if artist.title.lower() == k.lower():
          full_item = library.fetchItem(artist.key)
          original = set([similar.tag.lower() for similar in full_item.similar])
          combined = list(set(list(original - set(v)) + v))
        
          # oops - used to remove spammed artists
          if artist_to_remove != '' and artist_to_remove.lower() in original:
            tqdm.write("Removing '"+artist_to_remove+"' from "+str(artist.title))
            full_item.removeSimilarArtist(artist_to_remove.lower())
            
          # replace certain tags
          for pair in tags_to_rename:
            if pair[0].lower() in original:
              tqdm.write("Removing '"+pair[0]+"' from "+str(artist.title))
              changed = changed+1
              full_item.removeSimilarArtist(pair[0].lower())
            if not pair[0].lower() in combined:
              combined.append(pair[1])
          
          # print(combined)
          
          if not len(set([similar.tag.lower() for similar in full_item.similar])) == len(combined):
            # tqdm.write(str(full_item.similar)+' | '+str(combined))
            if(len(list(set(v)-original))) > 0:
              tqdm.write('Adding ' + str(list(set(v)-original)) + ' to '+k)
              changed = changed+1
              # full_item.editTags("similar", combined, 1)
              # full_item.reload()
            
    except requests.exceptions.RequestException as e:
      tqdm.write('Error: '+str(err))
      
  print(changed,'artists changed')
  
except requests.exceptions.RequestException as err:
  tqdm.write('Error: '+str(err))
