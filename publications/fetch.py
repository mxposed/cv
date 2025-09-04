import habanero
import json
import os
import time
from datetime import datetime


def load_last_indexed_date():
    try:
        with open('last_indexed_date.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "2019-06-01"  # Default start date


def save_last_indexed_date(indexed_date):
    with open('last_indexed_date.txt', 'w') as f:
        f.write(indexed_date)


def save_results(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    subfolder = f'data/{timestamp[-1]}{timestamp[-5]}'
    os.makedirs(subfolder, exist_ok=True)
    filename = os.path.join(subfolder, f'chunk_{timestamp}.json')
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    cr = habanero.Crossref(mailto='nikolai.markov@icloud.com', ua_string='publication-tracker', timeout=30)

    last_indexed_date = load_last_indexed_date()
    print(f"Starting from indexed date: {last_indexed_date}")

    exception_count = 0
    max_exceptions = 5

    all_results = []

    while exception_count < max_exceptions:
        try:
            # print(f"Fetching results with cursor: {cursor_mark}, from date: {last_indexed_date}")
            print('.', end='', flush=True)

            response = cr.works(
                query_author='markov',
                # cursor=cursor_mark,
                limit=100,
                # cursor_max=100,  # Maximum number of results to return
                select=[
                    'type', 'author', 'DOI', 'URL', 'created', 'publisher',
                    'container-title', 'issue', 'published', 'short-container-title',
                    'title', 'volume', 'indexed', 'resource', 'page', 'relation'
                ],
                filter={
                    'from-index-date': last_indexed_date,
                    'from-pub-date': '2019-06-01'
                },
                sort='indexed',
                order='asc'
            )

            # Process results
            if 'message' in response and 'items' in response['message']:
                items = response['message']['items']

                if not items:
                    print("No more results found.")
                    break

                # Process and save items
                # print(f"Retrieved {len(items)} items")
                all_results.extend(items)

                # Save the batch
                save_results({
                    'last_indexed_date': last_indexed_date,
                    'query_author': 'markov',
                    'filter_from_pub_date': '2019-06-01',
                    'limit': 100,
                    'items': items
                })

                # Update last indexed date from the last item
                if items:
                    last_item = items[-1]
                    if 'indexed' in last_item and 'date-time' in last_item['indexed']:
                        # Extract just the date part from the datetime
                        date_time = last_item['indexed']['date-time']
                        if date_time.endswith('Z'):
                            date_time = date_time[:-1]
                        print(f"Last indexed date in this batch: {date_time}")
                        last_indexed_date = date_time
                        save_last_indexed_date(date_time)

                # Get next cursor mark
                if len(items) < 100:
                    print("Fetched less than limit, assuming end of results.")
                    break
            else:
                print("No valid items in response")
                exception_count += 1

            time.sleep(2)  # Be polite and avoid hitting rate limits

        except Exception as e:
            exception_count += 1
            error_type = type(e).__name__
            print(f"Exception {exception_count}/{max_exceptions}: {error_type} - {str(e)}")

            if exception_count >= max_exceptions:
                print("Maximum number of exceptions reached. Stopping.")
                break

            # Sleep and retry
            sleep_time = 5  # seconds
            print(f"Sleeping for {sleep_time} seconds before retry...")
            time.sleep(sleep_time)

    print(f"Finished. Last indexed date: {last_indexed_date}")


if __name__ == "__main__":
    main()
