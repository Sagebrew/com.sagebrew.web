from logging import getLogger

from django.core.management.base import BaseCommand

import nltk

logger = getLogger("loggly_logs")


class Command(BaseCommand):
    args = 'None.'

    def populate_nltk(self):
        nltk_data = [
            'maxent_ne_chunker', 'abc', 'alpino', 'biocreative_ppi',
            'brown', 'brown_tei', 'cess_cat', 'cess_esp', 'chat80',
            'city_database', 'cmudict', 'comparative_sentences',
            'comtrans', 'conll2000', 'conll2002', 'conll2007',
            'crubadan', 'dependency_treebank', 'europarl_raw',
            'floresta', 'framenet_v15', 'gazetteers', 'genesis',
            'gutenberg', 'ieer', 'inaugural', 'indian', 'jeita',
            'kimmo', 'knbc', 'lin_thesaurus', 'mac_morpho', 'machado',
            'masc_tagged', 'movie_reviews', 'mte_teip5', 'names',
            'nombank.1.0', 'nonbreaking_prefixes', 'nps_chat', 'omw',
            'opinion_lexicon', 'panlex_swadesh', 'paradigms', 'pe08',
            'pil', 'pl196x', 'ppattach', 'problem_reports', 'product_reviews_1',
            'product_reviews_2', 'propbank', 'pros_cons', 'ptb', 'qc',
            'reuters', 'rte', 'semcor', 'senseval', 'sentence_polarity',
            'sentiwordnet', 'shakespeare', 'sinica_treebank', 'smultron',
            'state_union', 'stopwords', 'subjectivity', 'swadesh',
            'switchboard', 'timit', 'toolbox', 'treebank', 'twitter_samples',
            'udhr', 'udhr2', 'unicode_samples', 'universal_treebanks_v20',
            'verbnet', 'webtext', 'wordnet', 'wordnet_ic', 'words', 'ycoe',
            'basque_grammars', 'book_grammars', 'large_grammars',
            'sample_grammars', 'spanish_grammars', 'tagsets', 'perluniprops',
            'bllip_wsj_no_aux', 'moses_sample', 'word2vec_sample',
            'vader_lexicon', 'rslp', 'snowball_data',
            'averaged_perceptron_tagger', 'hmm_treebank_pos_tagger',
            'maxent_treebank_pos_tagger', 'universal_tagset', 'punkt'
        ]
        try:
            nltk.download(nltk_data, halt_on_error=False, quiet=True)
        except Exception as e:
            logger.exception(e)

    def handle(self, *args, **options):
        logger.critical("Started nltk Population")
        self.populate_nltk()
        logger.critical("Populated nltk successfully")
