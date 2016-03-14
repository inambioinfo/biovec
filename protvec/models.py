from gensim.models import word2vec
from Bio import SeqIO


def split_ngrams(seq, n):
    """
    'AGAMQSASM' => [['AGA', 'MQS', 'ASM'], ['GAM','QSA'], ['AMQ', 'SAS']]
    """
    a, b, c = list(zip(*[iter(seq)]*n)), list(zip(*[iter(seq[1:])]*n)), list(zip(*[iter(seq[2:])]*n))
    str_ngrams = []
    for ngrams in [a,b,c]:
        x = []
        for ngram in ngrams:
            x.append("".join(ngram))
        str_ngrams.append(x)
    return str_ngrams


def generate_corpusfile(fname, n, out):
    f = open(out, "w")
    for r in SeqIO.parse(fname, "fasta"):
        ngram_patterns = split_ngrams(r.seq, n)
        for ngram_pattern in ngram_patterns:
            f.write(" ".join(ngram_pattern) + "\n")

    f.close()


class ProtVec(word2vec.Word2Vec):

    def __init__(self, fname=None, corpus=None, n=3, size=100, out="corpus.txt",  sg=1, window=5, min_count=2, workers=3):
        """
        Either fname or corpus is required.

        fname: fasta file
        corpus: corpus object implemented by gensim
        n: the number of n-gram
        out: corpus output file path
        min_count: least appearance count in corpus. if the n-gram appear k times which is below min_count, the model does not remember the n-gram
        """

        self.n = n
        self.size = size
        self.fname = fname

        if corpus is None:
            if fname is None:
                raise Exception("Either fname or corpus is needed!")
            generate_corpusfile(fname, n, out)
            corpus = word2vec.Text8Corpus(out)

        word2vec.Word2Vec.__init__(self, corpus, size=size, sg=sg, window=window, min_count=min_count, workers=workers)

    def to_vecs(self, seq):
        """
        convert sequence to three n-length vectors
        e.g. 'AGAMQSASM' => [ array([  ... * 100 ], array([  ... * 100 ], array([  ... * 100 ] ]
        """
        ngram_patterns = split_ngrams(seq, self.n)
        
        protvecs = []
        for ngrams in ngram_patterns:
            # need to deal with error like query does not exist in the model
            for ngram in ngrams:
                print(ngram)
            protvecs.append(sum([self[ngram] for ngram in ngrams]))
        return protvecs