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

def read_journal_abbreviations(filepath):
    """List of journal abbreviations from https://github.com/kaiifu/Journal-Abbreviation"""
    result = {}
    for line in open(filepath, 'rb'):
        parts = line.decode('latin1').strip().split('\t')
        if len(parts) == 2:
            full, abbr = parts
            result[full.strip(' \n"')] = abbr.strip(' \n"')
    return result

def is_author_match(author, target_first="Nikolay", target_middle="S", target_last="Markov"):
    """Check if the author matches the target name components."""
    if 'given' not in author or 'family' not in author:
        return False

    # Get author's name components
    given = author['given'].lower()
    family = author['family'].lower()
    given = re.sub(r'[^a-z]', '', given)
    family = re.sub(r'[^a-z]', '', family)

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
    n_first = 0
    for author in authors:
        if 'sequence' in author and author['sequence'] == 'first':
            n_first += 1

    for author in authors:
        given = author.get('given', '')
        family = author.get('family', '')
        name = author.get('name', '')
        suffix = ''
        if family.endswith('*'):
            family = family[:-1]
            author['sequence'] = 'first'
            n_first = 2
        if family.endswith('†'):
            family = family[:-1]
            suffix = '#super[†]'
        if given and family:
            initials = ''.join([name[0] for name in given.split()])
            author_strings.append(f"{family} {initials}")
        elif family:
            author_strings.append(family)
        elif name:
            author_strings.append(name)
        if 'sequence' in author and author['sequence'] == 'first' and n_first > 1:
            author_strings[-1] += '\\*'
        if suffix:
            author_strings[-1] += suffix
        if 'truncate' in author and author['truncate']:
            break

    return ", ".join(author_strings)

def format_journal(item):
    """Extract the journal name"""
    name = None
    if item['type'] == 'journal-article':
        name = item['container-title'][0]
    if item['type'] == 'posted-content':
        if 'biorxiv' in item['resource']['primary']['URL']:
            name = 'bioRxiv'
        if 'medrxiv' in item['resource']['primary']['URL']:
            name = 'medRxiv'
    if name is None:
        raise ValueError(f"Cannot extract journal")
    name = name.replace('&amp;', '&')
    issue = item.get('issue', '')
    volume = item.get('volume', '')
    pages = item.get('page', '')
    if '-' in pages:
        pages = pages.split('-')
        if pages[0] == pages[1]:
            pages = pages[0]
        else:
            pages = '-'.join(pages)
    if volume and issue and pages:
        return name, f'{volume}({issue}):{pages}'
    if volume and issue:
        return name, f'{volume}({issue})'
    if volume and pages:
        return name, f'{volume}:{pages}'
    if volume:
        return name, volume
    return name, ''

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

def apply_override(item, override):
    """Apply overrides to a publication item."""
    if not override:
        return item
    for key, value in override.items():
        if key == 'author':
            for author in value:
                for item_author in item['author']:
                    if 'given' in author and 'given' in item_author:
                        if item_author['given'] == author['given'] and item_author['family'] == author['family']:
                            item_author.update(author)
                            break
                    if 'name' in author and 'name' in item_author:
                        if item_author['name'] == author['name']:
                            item_author.update(author)
                            break
    return item

def convert_item(item, journal_abbrevs):
    """Convert a publication item to a simplified dictionary format."""
    journal, details = format_journal(item)
    return {
        "title": format_title(item['title'][0]),
        "journal": journal_abbrevs.get(journal, journal),
        "details": details,
        "date": format_publication_date(item.get('published')),
        "year": str(item['published']['date-parts'][0][0]),
        "authors": format_authors(item.get('author', [])),
        "doi": item.get('DOI', 'No DOI'),
        "url": item.get('URL', 'No URL'),
        "type": item.get("type", "No type"),
        "raw": item  # Include the raw item for reference
    }

def filter_publications(data, target_first="Nikolay", target_middle="S", target_last="Markov", to_exclude=None, overrides=None, abbrevs=None):
    """Filter publications by target author and print details."""
    found_publications = []
    if to_exclude is None:
        to_exclude = set()
    if overrides is None:
        overrides = []
    override_dict = {item['DOI']: item for item in overrides}
    if abbrevs is None:
        abbrevs = {}

    for item in data:
        if 'author' not in item:
            continue

        for author in item['author']:
            if is_author_match(author, target_first, target_middle, target_last) and item.get('DOI') not in to_exclude:
                item = apply_override(item, override_dict.get(item['DOI']))
                # Extract publication details
                found_publications.append(convert_item(item, abbrevs))

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

def split_sort(publications):
    """Split publications into journal articles and others, sort by date."""
    journal_articles = [pub for pub in publications if pub['type'] == 'journal-article']
    other_articles = [pub for pub in publications if pub['type'] != 'journal-article']

    journal_articles.sort(key=lambda x: x['date'], reverse=True)
    i = 0
    for article in journal_articles:
        article['rank'] = len(journal_articles) - i
        i += 1
    other_articles.sort(key=lambda x: x['date'], reverse=True)
    for article in other_articles:
        article['rank'] = 2 * len(journal_articles) + len(other_articles) - i
        i += 1

    return {
        'preprints': other_articles,
        'articles': journal_articles
    }


def main():
    print("Loading publication data...")
    data = load_json_files()
    print(f"Loaded {len(data)} publication records.")

    to_exclude = load_exclude_list("exclude.txt")
    print(f"Loaded {len(to_exclude)} DOIs to exclude.")

    overrides = json.load(open("overrides.json", "r"))
    print(f"Loaded {len(overrides)} overrides.")

    journal_abbrevs = read_journal_abbreviations("Journal-Abbreviation.txt")
    print(f"Loaded {len(journal_abbrevs)} journal abbreviations.")

    target_first = "Nikolay"
    target_middle = "S"
    target_last = "Markov"

    print(f"Filtering publications for author: {target_first} {target_middle} {target_last}")
    pubs = filter_publications(
        data,
        target_first,
        target_middle,
        target_last,
        to_exclude,
        overrides,
        journal_abbrevs
    )
    print(f"Found {len(pubs)} publications for {target_first} {target_middle} {target_last}")
    dedup_pubs = dedup_publications_by_relation(pubs)
    print(f'Removed {len(pubs) - len(dedup_pubs)} duplicate publications based on relations.')
    pubs = dedup_pubs
    dedup_pubs = dedup_publications_by_title(pubs)
    print(f'Removed {len(pubs) - len(dedup_pubs)} duplicate publications based on title similarity.')
    print(f"{len(dedup_pubs)} publications remain after deduplication.")

    data = split_sort(dedup_pubs)
    json.dump(data, open("filtered_publications.json", "w"), indent=2)
    # for pub in dedup_pubs:
    #     print('-' * 80)
    #     print(pub['title'])

if __name__ == "__main__":
    main()
