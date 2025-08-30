import json
import os
import glob

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
            author_strings.append(f"{author['given']} {author['family']}")
        elif 'family' in author:
            author_strings.append(author['family'])

    return ", ".join(author_strings)

def filter_publications(data, target_first="Nikolay", target_middle="S", target_last="Markov"):
    """Filter publications by target author and print details."""
    found_publications = 0

    for item in data:
        if 'author' not in item:
            continue

        for author in item['author']:
            if is_author_match(author, target_first, target_middle, target_last):
                found_publications += 1

                # Extract publication details
                title = item.get('title', ['No title'])[0] if isinstance(item.get('title'), list) else item.get('title', 'No title')
                journal = item.get('container-title', ['No journal'])[0] if isinstance(item.get('container-title'), list) else item.get('container-title', 'No journal')
                pub_date = format_publication_date(item.get('published'))
                authors = format_authors(item.get('author', []))
                doi = item.get('DOI', 'No DOI')
                url = item.get('URL', 'No URL')

                # Print publication details
                print("\n" + "="*80)
                # print(f"Publication {found_publications}:")
                print(f"Title: {title}")
                print(f'Type: {item.get("type", "No type")}')
                print(f"Journal: {journal}")
                # print(f"Date: {pub_date}")
                # print(f"Authors: {authors}")
                print(f"DOI: {doi}")
                # print(f"URL: {url}")
                # print(json.dumps(item, indent=2))
                print("="*80)

                # Break once we find a match in the current item
                break

    if found_publications == 0:
        print(f"No publications found for {target_first} {target_middle} {target_last}")
    else:
        print(f"\nFound {found_publications} publications for {target_first} {target_middle} {target_last}")

def main():
    print("Loading publication data...")
    data = load_json_files()
    print(f"Loaded {len(data)} publication records.")

    target_first = "Nikolay"
    target_middle = "S"
    target_last = "Markov"

    print(f"Filtering publications for author: {target_first} {target_middle} {target_last}")
    filter_publications(data, target_first, target_middle, target_last)

if __name__ == "__main__":
    main()
