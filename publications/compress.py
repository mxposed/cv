import json
import os
import glob
import io

import zstandard as zstd


def read_data(input) -> list[object]:
    """Read data from `pubs.jsonl.zst` (input) if it exists

    The order relies on the sorted call in the `main`
    """
    if not os.path.exists(input):
        return []
    result = []
    dctx = zstd.ZstdDecompressor()
    with open(input, "rb") as f:
        with dctx.stream_reader(f) as reader:
            text_stream = io.TextIOWrapper(reader, encoding='utf-8')
            for line in text_stream:
                result.append(json.loads(line))
    return result


def write_data(chunks: list[object], file: str):
    cctx = zstd.ZstdCompressor(level=19)
    with open(file, "wb") as f:
        with cctx.stream_writer(f) as writer:
            for doc in chunks:
                writer.write((json.dumps(doc) + "\n").encode())


def main(source="data", output="pubs.jsonl.zst"):
    json_files = glob.glob(os.path.join(source, "**/*.json"))
    chunks = read_data(output)
    to_delete = []
    for file in sorted(json_files):
        try:
            with open(file, 'r') as f:
                file_data = json.load(f)
                chunks.append(file_data)
                to_delete.append(file)
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")
    write_data(chunks, output)
    for file in to_delete:
        os.unlink(file)


if __name__ == '__main__':
    main()
