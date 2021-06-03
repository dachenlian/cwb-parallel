from argparse import ArgumentParser, Namespace
import json
import logging
from pathlib import Path
from typing import Tuple, List, Iterator

from tqdm import tqdm


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        '--output_path',
        help='Write file to output path',
        type=Path,
        default=None,
    )
    parser.add_argument(
        '--tok_path',
        help='Path to tokenized JSON file',
        type=Path,
        default=None,
    )
    parser.add_argument(
        '--pos_path',
        help='Path to POS JSON file',
        type=Path,
        default=None,
    )
    parser.add_argument(
        '--entity_path',
        help='Path to entity JSON file',
        type=Path,
        default=None,
    )
    parser.add_argument(
        '--test',
        help='Process first 100 segments to see if everything is okay',
        action='store_true'
    )

    return parser.parse_args()


def load(args: Namespace) -> Tuple[List[str], List[str], List[str]]:

    logging.info("Loading files...")
    
    with args.tok_path.open() as f1, args.pos_path.open() as f2, args.entity_path.open() as f3:
        toks = json.load(f1)
        pos = json.load(f2)
        entity = json.load(f3)

    logging.info("Loading complete.")

    assert len(toks) == len(pos) == len(entity), "All files must be the same length."

    if args.test:
        logging.info("Testing verticalization...")
        toks = toks[:100]
        pos = pos[:100]
        entity = entity[:100]

    return toks, pos, entity
    

def get_entity(entity_iter: Iterator[List[Tuple[str, str, Tuple[int, int]]]]) -> Tuple[str, int, int]:
    current_entity = next(entity_iter, None)
    if current_entity:
        entity_name = current_entity[1].lower()
        entity_indices = current_entity[2]
        entity_start = entity_indices[0]
        entity_end = entity_indices[1]
    else:
        entity_name = ""
        entity_start = entity_end = -1

    return entity_name, entity_start, entity_end


def main():
    args = parse_args()

    all_toks, all_pos, all_entity = load(args)
    total = len(all_toks)

    with args.output_path.open('w') as f:

        for idx, (toks, pos, entity) in enumerate(tqdm(zip(all_toks, all_pos, all_entity), total=total), 1):
            print(f'<text id="{idx}">', file=f)
            ptr = 0

            entity_iter = iter(entity)
            entity_name, entity_start, entity_end = get_entity(entity_iter)

            for t, p in zip(toks, pos):
                if p == 'WHITESPACE':
                    ptr += 1
                    continue
                if ptr == entity_start:
                    print(f"<{entity_name}>", file=f)
                print(f"{t}\t{p}", file=f)
                ptr += len(t)
                if ptr == entity_end:
                    print(f"</{entity_name}>", file=f)
                    entity_name, entity_start, entity_end = get_entity(entity_iter)
            print(f'</text>', file=f)


if __name__ == '__main__':
    main()