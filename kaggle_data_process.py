# %%
import ijson
import time
import csv
import numpy as np
from decimal import Decimal

# %%
start = time.process_time()

# Initialize counters and list for filtered results
PAPER = []
count = 0
filtered_count = 0

with open('dblp.v12.json', "rb") as f, open("dblp_graph_conference.csv", "w", newline="") as csvfile:
    fieldnames = ['id', 'title', 'year', 'author_name', 'author_org', 'author_id', 'n_citation', 'doc_type',
                  'reference_count', 'references', 'venue_id', 'venue_name', 'venue_type', 'doi', 'keyword',
                  'volume', 'issue', 'publisher', 'weight', 'indexed_keyword', 'inverted_index']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through each item in the JSON file
    for i, element in enumerate(ijson.items(f, "item")):
        # Check for 'doc_type' and 'keyword' conditions
        if element.get('doc_type') == 'Conference':
            fos = element.get('fos', [])
            # Convert keywords to lowercase for case-insensitive matching
            keywords = [f.get('name', '').lower() for f in fos]
            if 'graph' in keywords:
                paper = {}
                paper['id'] = element['id']
                paper['title'] = element['title']

                year = element.get('year')
                paper['year'] = year if year else np.nan

                author = element.get('authors')
                if author:
                    author_name = [a.get('name', np.nan) for a in author]
                    author_org = [a.get('org', np.nan) for a in author]
                    author_id = [a.get('id', np.nan) for a in author]
                    paper['author_name'] = ';'.join(map(str, author_name))
                    paper['author_org'] = ';'.join(map(str, author_org))
                    paper['author_id'] = ';'.join(map(str, author_id))
                else:
                    paper['author_name'] = paper['author_org'] = paper['author_id'] = np.nan

                paper['n_citation'] = element.get('n_citation', np.nan)
                paper['doc_type'] = element.get('doc_type', np.nan)

                references = element.get('references')
                if references:
                    paper['reference_count'] = len(references)
                    paper['references'] = ';'.join(map(str, references))
                else:
                    paper['reference_count'] = paper['references'] = np.nan

                venue = element.get('venue', {})
                paper['venue_id'] = venue.get('id', np.nan)
                paper['venue_name'] = venue.get('raw', np.nan)
                paper['venue_type'] = venue.get('type', np.nan)

                paper['doi'] = f"https://doi.org/{element.get('doi')}" if element.get('doi') else np.nan

                if fos:
                    paper['keyword'] = ';'.join(str(f.get('name', np.nan)) for f in fos)
                    paper['weight'] = ';'.join(str(f.get('w', np.nan)) for f in fos)
                else:
                    paper['keyword'] = paper['weight'] = np.nan

                indexed_abstract = element.get('indexed_abstract', {}).get('InvertedIndex', {})
                paper['indexed_keyword'] = ';'.join(map(str, indexed_abstract.keys()))
                paper['inverted_index'] = ';'.join(map(str, indexed_abstract.values()))

                paper['publisher'] = element.get('publisher', np.nan)
                paper['volume'] = element.get('volume', np.nan)
                paper['issue'] = element.get('issue', np.nan)

                # Write the filtered row to CSV
                writer.writerow(paper)
                filtered_count += 1

                # Optional progress indicator
                if filtered_count % 100 == 0:
                    print(f"{filtered_count} papers written to CSV")

print(f"Total records processed: {count}, Filtered records: {filtered_count}, Time taken: {round((time.process_time() - start), 2)}s")


