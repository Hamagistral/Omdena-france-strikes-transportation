# a PATCH for app_osm.ipynb
# created by Viktor Ivanenko
# Streets names only selector
class Streets_names_only_selector:
  streets = []
  for string in updated_directions.get('instructions'):
      string_splited = string.split(', ')
      for splt in string_splited:
          if splt.isnumeric() == False:
              streets.append(splt)
              break

  updated_directions['short_streets'] = streets

  print('\n', updated_directions['short_streets'])
