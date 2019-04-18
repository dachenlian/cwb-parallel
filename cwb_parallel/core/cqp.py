from pathlib import Path
from random import randint
import time
import re
import pexpect


class Cqp:
    RESULTS_DIR = Path('/results').resolve()
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir()

    REGISTRY = '/cwb/registry'

    def __init__(self, query_cmd, corpus, alignment=True, usr_registry=None):
        self.query_cmd = query_cmd
        self.corpus = corpus
        self.usr_registry = usr_registry
        self.alignment = alignment
        self._result_path = None
        self._results = None
        self._src = None
        self._tgt = None
        if self.alignment:
            if self.corpus == 'tm':
                self.aligned_corpus = 'mm'
            elif self.corpus == 'mm':
                self.aligned_corpus = 'tm'
            else:
                self.aligned_corpus = None

    def __str__(self):
        return f'Cqp(query_cmd={self.query_cmd}, corpus={self.corpus}, alignment={self.alignment}, usr_registry={self.usr_registry})'

    def __len__(self):
        return len(self.results)

    @staticmethod
    def _clean(text):
        text = re.sub('(&nbsp;|<LI>|<P><B>.+</B>)', '', text)  # non-breaking space
        return text

    def _add_markup(self, text, tag):
        return re.sub(rf'({self.query_cmd})', rf'<{tag}>\1</{tag}>', text)

    def query(self):
        fpath = self.RESULTS_DIR / f'{randint(1, 100000000)}.txt'
        self._result_path = fpath
        commands = [
            'set AutoShow off;',
            'set PrintMode html;',
            f'{self.corpus.upper()};',
            'set Context 1 text;',
            f'show -cpos;',  # corpus position
            f"""'{self.query_cmd}';""",
            f"cat > '{fpath}';",
        ]
        if self.alignment:
            commands.insert(-3, f'show +{self.aligned_corpus};')

        q = pexpect.spawn(f'cqp -e -r {self.REGISTRY}', encoding='utf8')

        for c in commands:
            q.sendline(c)

        time.sleep(4)
        # print('First expect')
        # q.expect(commands[-1])  # match last line
        # q.expect(f'{self.corpus.upper()}>')  # then match prompt after 'cat' command to ensure cmd finished
        q.sendline('exit;')

        self._read_results()

    def _read_results(self):
        if not self._result_path.exists():
            print('Query not found.')
            return
        with self._result_path.open() as fp:
            r = []
            for line in filter(bool, (line.strip() for line in fp.readlines())):
                line = self._clean(line)
                r.append(line)

            r = r[1:-2]  # exclude <HR><UL>
            if self.alignment:
                self._src = r[::2]
                self._tgt = r[1::2]
        self._results = r

    @property
    def results(self):
        if not self._results and not self._result_path:
            self.query()
        return self._results

    @property
    def src(self):
        if not self.alignment:
            print('Non-parallel query does not have this attribute.')
            return
        if not self._results:
            self.query()
        return self._src

    @property
    def tgt(self):
        if not self.alignment:
            print('Non-parallel query does not have this attribute.')
            return
        if not self._results:
            self.query()
        return self._tgt
