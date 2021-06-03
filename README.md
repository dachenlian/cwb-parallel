# How to verticalize a corpus

After using [`CKIP-transformers`](https://github.com/ckiplab/ckip-transformers) to segment, POS tag, and do NER (via `cwb_utils/process_raw.py`), use `verticalize.py` to output into CWB format.

```bash
python cwb_utils/verticalize.py --output_path path/to/output.vrt \
    --tok_path path/to/segmented.json \
    --pos_path path/to/pos.json \
    --entity_path path/to/entity.json 
```