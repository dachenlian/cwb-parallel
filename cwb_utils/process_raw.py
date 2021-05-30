from argparse import ArgumentParser, Namespace
import json
from pathlib import Path
from typing import List, Tuple, Union

from bs4 import BeautifulSoup as bs
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
from ckip_transformers.nlp.util import NerToken
import opencc


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        'input_path',
        help='Text to be processed.',
        type=Path,
    )
    parser.add_argument(
        'output_path',
        help='Path to processed files',
        type=Path
    )
    parser.add_argument(
        '--to_traditional',
        help='Convert to Traditional Chinese before inference',
        action='store_true'
    )
    parser.add_argument(
        '--model_level',
        help='Choose which model to use for inference (1: albert-tiny, 2: albert-base, 3: bert-base)',
        choices=[1, 2, 3],
        default=2
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


def save_output(out_path: Path, obj: Union[List[str], List[NerToken]]) -> None:
    with out_path.open('w') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

    print(f'Object saved to {out_path.resolve()}')


def run_pipeline(sents: List[str], out_path_base: Path, batch_size=64, max_length=509) -> Tuple[List[str], List[str], List[str]]:
    word_sentence_list = ws(sents, batch_size=batch_size, max_length=max_length, use_delim=True)
    save_output(out_path_base.joinpath('_segmented.json'), word_sentence_list)

    pos_sentence_list = pos(word_sentence_list, batch_size=batch_size, max_length=max_length, use_delim=True)
    save_output(out_path_base.joinpath('_pos.json'), pos_sentence_list)

    del word_sentence_list
    del pos_sentence_list

    entity_sentence_list = ner(sents, batch_size=batch_size, max_length=max_length, use_delim=True)
    save_output(out_path_base.joinpath('_entity.json'), entity_sentence_list)
    
    return word_sentence_list, pos_sentence_list, entity_sentence_list


if __name__ == '__main__':
    args = parse_args()

    ws = CkipWordSegmenter(level=args.model_level, device=args.device)
    pos = CkipPosTagger(level=args.model_level, device=args.device)
    ner = CkipNerChunker(level=args.model_level, device=args.device)

    with args.input_path.open() as f:
        xml = bs(f, 'lxml')

    texts = xml.findAll('text')
    sent_list = [t.text.replace('\n', '') for t in texts]
    if args.to_traditional:
        converter = opencc.OpenCC('s2t.json')
        sent_list = [converter.convert(t) for t in sent_list]

    del xml
    del texts

    w, p, e = run_pipeline(sent_list, batch_size=args.batch_size, max_length=args.max_length, out_path_base=args.output_path)
