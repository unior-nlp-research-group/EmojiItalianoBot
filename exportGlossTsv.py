# Run from GAE remote API:
# comment the 2 import emoji_unicode lines in emojiUtil
# run:
# 	remote_api_shell.py -s emojitalianobot.appspot.com
# 	import exportGlossTsv
#

from google.appengine.ext import ndb
from google.appengine.ext.ndb import metadata
import csv
from gloss import Gloss


def exportToCsv(query, csvFileName):
    with open(csvFileName, 'wb') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        first_row = True
        rows = 0

        for e in query:
            #print e
            # Write column labels as first row
            row_dict = e.to_dict()
            if first_row:
                first_row = False
                keys = sorted(row_dict.keys())
                csvWriter.writerow(keys)
            values = []
            v_str = None
            for k in keys:
                v_row = row_dict[k]
                v_str = str(v_row)
                #try:
                #    v_str = v_row.encode('utf-8') if v_row is str else str(v_row)
                #except UnicodeEncodeError:
                #    v_str = '--'
                values.append(v_str)
            #print('adding:' + str(values))
            csvWriter.writerow(values)
            rows += 1
            if rows == 2:
                break

        print 'Finished saving ' + str(rows) + ' rows.'


exportToCsv(query = Gloss.query(), csvFileName='data/Gloss_Table.tsv')
#.order(Gloss.source_emoji)