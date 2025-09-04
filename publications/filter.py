import json
import os
import glob
import re


def load_json_files(directory="data"):
    """Load all JSON files from the specified directory."""
    json_files = glob.glob(os.path.join(directory, "**/*.json"))
    data = []

    for file in sorted(json_files):
        try:
            with open(file, 'r') as f:
                file_data = json.load(f)
                data.extend(file_data['items'])
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

    return data

def load_exclude_list(filepath):
    """Load a list of DOIs to exclude from the specified file."""
    try:
        with open(filepath, 'r') as f:
            exclude_list = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        return exclude_list
    except Exception as e:
        print(f"Error loading exclude list from {filepath}: {str(e)}")
        return set()

def is_author_match(author, target_first="Nikolay", target_middle="S", target_last="Markov"):
    """Check if the author matches the target name components."""
    if 'given' not in author or 'family' not in author:
        return False

    # Get author's name components
    given = author['given'].lower()
    family = author['family'].lower()

    # Check last name first (faster rejection)
    if family != target_last.lower():
        return False

    # Check first name
    if not given.startswith(target_first.lower()):
        return False

    # If middle initial is specified, check for it
    if target_middle and target_middle.lower() not in given.lower():
        return False

    return True

def format_publication_date(pub_date):
    """Format the publication date in a readable format."""
    if not pub_date:
        return "No date"

    if isinstance(pub_date, dict) and 'date-parts' in pub_date:
        parts = pub_date['date-parts'][0]
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1]:02d}-{parts[2]:02d}"
        elif len(parts) == 2:
            return f"{parts[0]}-{parts[1]:02d}"
        elif len(parts) == 1:
            return f"{parts[0]}"

    return str(pub_date)

def format_authors(authors):
    """Format the list of authors."""
    if not authors:
        return "No authors listed"

    author_strings = []
    for author in authors:
        if 'given' in author and 'family' in author:
            initials = ''.join([name[0] for name in author['given'].split()])
            author_strings.append(f"{author['family']} {initials}")
        elif 'family' in author:
            author_strings.append(author['family'])

    return ", ".join(author_strings)

def get_journal(item):
    """Extract the journal name"""
    if item['type'] == 'journal-article':
        return item['container-title'][0]
    if item['type'] == 'posted-content':
        if 'biorxiv' in item['resource']['primary']['URL']:
            return 'bioRxiv'
        if 'medrxiv' in item['resource']['primary']['URL']:
            return 'medRxiv'
    raise ValueError(f"Cannot extract journal")

EXCEPTIONS = [
    'covid-19',
    'aspergillus',
    'm-csf/m-csfr',
    'sars-cov-2',
    'cx3cr1',
    'ace2',
    'icu',
    'il-6',
    'chatgpt',
    'isrib',
    '1b'
]

def format_title(title):
    title = re.sub(r'/(\w+)>(?=([A-Za-z]))', r'/\1> ', title)
    title = re.sub(r'(?<=[A-Za-z])<(\w+)>', r' <\1>', title)
    result = []
    for i, word in enumerate(title.split()):
        if i == 0:
            result.append(word)
        else:
            if word == 'Cell' and result[-1] == 'UCSC':
                result.append(word)
            elif word == 'Browser:' and result[-2] == 'UCSC':
                result.append(word)
            elif word == 'T':
                result.append(word)
            elif word == 'A' and result[-1] == 'influenza':
                result.append(word)
            else:
                exception = False
                for ex in EXCEPTIONS:
                    if ex in word.lower():
                        result.append(word)
                        exception = True
                        break
                if not exception:
                    result.append(word.lower())
    title = ' '.join(result)
    title = re.sub(r'<i>(.+)</i>', r'_\1_', title)
    title = re.sub(r'<sup>(.+)</sup>', r'#super[\1]', title)
    return title

def convert_item(item):
    """Convert a publication item to a simplified dictionary format."""
    return {
        "title": format_title(item['title'][0]),
        "journal": get_journal(item),
        "date": format_publication_date(item.get('published')),
        "authors": format_authors(item.get('author', [])),
        "doi": item.get('DOI', 'No DOI'),
        "url": item.get('URL', 'No URL'),
        "type": item.get("type", "No type"),
        "raw": item  # Include the raw item for reference
    }

def filter_publications(data, target_first="Nikolay", target_middle="S", target_last="Markov", to_exclude=None):
    """Filter publications by target author and print details."""
    found_publications = []
    if to_exclude is None:
        to_exclude = set()

    for item in data:
        if 'author' not in item:
            continue

        for author in item['author']:
            if is_author_match(author, target_first, target_middle, target_last) and item.get('DOI') not in to_exclude:
                # Extract publication details
                found_publications.append(convert_item(item))

                # Break once we find a match in the current item
                break
        if len(found_publications) > 0:
            # break
            pass
    return found_publications

def dedup_publications_by_relation(publications):
    preprints_to_exclude = set()
    for pub in publications:
        if 'relation' in pub['raw'] and 'has-preprint' in pub['raw']['relation']:
            preprints_to_exclude.add(pub['raw']['relation']['has-preprint'][0]['id'])
    result = [pub for pub in publications if pub['doi'] not in preprints_to_exclude]
    return result

def dedup_publications_by_title(publications):
    """Deduplicate publications based on title word overlap."""
    result = []
    titles = {}
    for pub in publications:
        title_words = set(re.findall(r'\w+', pub['title'].lower()))
        titles[pub['doi']] = title_words

    to_remove = set()
    for i, pub1 in enumerate(publications):
        for pub2 in publications[i + 1:]:
            if pub1['doi'] != pub2['doi']:
                words1 = titles[pub1['doi']]
                words2 = titles[pub2['doi']]
                overlap = words1.intersection(words2)
                overlap_ratio = len(overlap) / min(len(words1), len(words2))
                if overlap_ratio > 0.8:
                    print(f"Duplicate detected: {pub1['title']} ({pub1['journal']}, {pub2['journal']}) with overlap {overlap_ratio:.2f}")
                    if pub1['type'] == 'journal-article':
                        to_remove.add(pub2['doi'])
                    else:
                        to_remove.add(pub1['doi'])
                    break
        if pub1['doi'] not in to_remove:
            result.append(pub1)
    return result


def main():
    print("Loading publication data...")
    data = load_json_files()
    print(f"Loaded {len(data)} publication records.")

    to_exclude = load_exclude_list("exclude.txt")
    print(f"Loaded {len(to_exclude)} DOIs to exclude.")

    target_first = "Nikolay"
    target_middle = "S"
    target_last = "Markov"

    print(f"Filtering publications for author: {target_first} {target_middle} {target_last}")
    pubs = filter_publications(data, target_first, target_middle, target_last, to_exclude)
    print(f"Found {len(pubs)} publications for {target_first} {target_middle} {target_last}")
    dedup_pubs = dedup_publications_by_relation(pubs)
    print(f'Removed {len(pubs) - len(dedup_pubs)} duplicate publications based on relations.')
    pubs = dedup_pubs
    dedup_pubs = dedup_publications_by_title(pubs)
    print(f'Removed {len(pubs) - len(dedup_pubs)} duplicate publications based on title similarity.')
    print(f"{len(dedup_pubs)} publications remain after deduplication.")
    json.dump(dedup_pubs, open("filtered_publications.json", "w"), indent=2)
    # for pub in dedup_pubs:
    #     print('-' * 80)
    #     print(pub['title'])

if __name__ == "__main__":
    main()
