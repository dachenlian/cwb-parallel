from argparse import ArgumentParser, Namespace
from itertools import islice
import json
from pathlib import Path
from typing import List, Tuple, Union, Optional

from bs4 import BeautifulSoup as bs
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
from ckip_transformers.nlp.util import NerToken
import opencc
from tqdm import tqdm


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        'output_path',
        help='Path to processed files',
        type=Path
    )
    parser.add_argument(
        '--input_path',
        help='Text to be processed.',
        type=Path,
        default=None
    )
    parser.add_argument(
        '--tasks',
        help='Select tasks to run in pipeline',
        choices=['ws', 'pos', 'ner'],
        nargs='+'
    )
    parser.add_argument(
        '--tokenized_file',
        help='Load already tokenized file for downstream task (POS tagging)',
        type=Path,
        default=None
    )
    parser.add_argument(
        '--split_file_chunks',
        help='Run inference piecemeal to ensure memory is not used completely',
        default=250_000
    )
    parser.add_argument(
        '--to_traditional',
        help='Convert to Traditional Chinese before inference',
        action='store_true'
    )
    parser.add_argument(
        '--tokenizer_model_level',
        help='Choose which model to use for tokenization (1: albert-tiny, 2: albert-base, 3: bert-base)',
        choices=[1, 2, 3],
        default=1
    )
    parser.add_argument(
        '--pos_model_level',
        help='Choose which model to use for POS tagging (1: albert-tiny, 2: albert-base, 3: bert-base)',
        choices=[1, 2, 3],
        default=1
    )
    parser.add_argument(
        '--ner_model_level',
        help='Choose which model to use for NER (1: albert-tiny, 2: albert-base, 3: bert-base)',
        choices=[1, 2, 3],
        type=int,
        default=1
    )
    parser.add_argument(
        '--batch_size',
        help='Size of batch to be input into transformer models',
        type=int,
        default=256
    )
    parser.add_argument(
        '--max_length',
        help='Size of batch to be input into transformer models',
        type=int,
        default=509
    )
    parser.add_argument(
        '--device',
        help='Run models on device',
        type=int,
        choices=[0, -1],
        default=0
    )

    args = parser.parse_args()

    return args


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def save_output(out_path: Path, obj: Union[List[str], List[NerToken]]) -> None:
    with out_path.open('w') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

    print(f'Object saved to {out_path.resolve()}')


def run_pipeline(out_path_base: Path, sents: Optional[List[str]] = None, word_sentence_list: Optional[List[List[str]]] = None, batch_size=64, max_length=509) -> None:
    if sents:
        tqdm_total = -(-len(sents) // args.split_file_chunks)
    elif word_sentence_list:
        tqdm_total = -(-len(word_sentence_list) // args.split_file_chunks)

    if 'ws' in args.tasks:
        if word_sentence_list:
            print('Tokenized sentences already provided. Skipping tokenization.')
        else:
            print('Running tokenization...')
            ws = CkipWordSegmenter(level=args.ws_model_level, device=args.device)
            word_sentence_list = ws(sents, batch_size=batch_size, max_length=max_length, use_delim=True)
            save_output(out_path_base.joinpath('segmented.json'), word_sentence_list)
    
    if 'pos' in args.tasks:
        counter = 0
        print('Running POS tagging...')
        pos = CkipPosTagger(level=args.pos_model_level, device=args.device)

        for c in tqdm(chunk(word_sentence_list, args.split_file_chunks), total=tqdm_total, desc="Chunk"):
            pos_sentence_list = pos(c, batch_size=batch_size, max_length=max_length, use_delim=True)
            save_output(out_path_base.joinpath(f'pos_{counter}.json'), pos_sentence_list)
            counter += 1

        del word_sentence_list
        del pos_sentence_list

    if 'ner' in args.tasks:
        counter = 0
        print('Running NER...')
        ner = CkipNerChunker(level=args.ner_model_level, device=args.device)

        for c in tqdm(chunk(sents, args.split_file_chunks), total=tqdm_total, desc="Chunk"):
            entity_sentence_list = ner(c, batch_size=batch_size, max_length=max_length, use_delim=True)
            save_output(out_path_base.joinpath(f'entity_{counter}.json'), entity_sentence_list)
            counter += 1
    


if __name__ == '__main__':
    args = parse_args()
    args.output_path.mkdir(exist_ok=True)

    if args.tokenized_file:
        with args.tokenized_file.open() as f:
            tokens = json.load(f)
        run_pipeline(word_sentence_list=tokens, batch_size=args.batch_size, max_length=args.max_length, out_path_base=args.output_path)
    else:
        with args.input_path.open() as f:
            xml = bs(f, 'lxml')

        texts = xml.findAll('text')
        sent_list = [t.text.replace('\n', '') for t in texts]
        if args.to_traditional:
            converter = opencc.OpenCC('s2t.json')
            sent_list = [converter.convert(t) for t in sent_list]

        del xml
        del texts

        run_pipeline(sents=sent_list, batch_size=args.batch_size, max_length=args.max_length, out_path_base=args.output_path)
