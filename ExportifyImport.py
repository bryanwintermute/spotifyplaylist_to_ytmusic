import csv

def exportify_parse(file_path):
  tracks = []

  with open(file_path, encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=",", quotechar='"')

    next(reader) # Skip the headers

    for row in reader:
      tracks.append("{}".format(row[0]))

  return tracks
