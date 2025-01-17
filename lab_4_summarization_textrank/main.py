"""
Lab 4
Summarize text using TextRank algorithm
"""
import re
from typing import Union, Any, Type

from lab_3_keywords_textrank.main import TextEncoder, \
    TextPreprocessor, TFIDFAdapter

PreprocessedSentence = tuple[str, ...]
EncodedSentence = tuple[int, ...]


def check_type(user_var: Any, expected_type: Union[Type, tuple[Type, ...]]) -> None:
    """
    Checks whether type of user_var is expected_type,
    if not - raises ValueError
    """
    if expected_type == int and isinstance(user_var, int) and isinstance(user_var, bool):
        raise ValueError
    if not isinstance(user_var, expected_type):
        raise ValueError


def check_collection(user_var: Any,
                     expected_elements_type: Type,
                     *expected_collection_type: Type,
                     can_be_empty: bool = False) -> None:
    """
    Checks whether type of user_var is at least one of expected_collection_type,
    checks whether type of elements in user_var are expected_elements_type,
    if not - raises ValueError
    if expected_elements_type is None, doesn't check elements
    """
    if can_be_empty is False and not user_var:
        raise ValueError
    if not isinstance(user_var, expected_collection_type):
        raise ValueError
    for i in user_var:
        check_type(i, expected_elements_type)


class Sentence:
    """
    An abstraction over the real-world sentences
    """

    def __init__(self, text: str, position: int) -> None:
        """
        Constructs all the necessary attributes
        """

        check_type(text, str)
        check_type(position, int)
        self._text = text
        self._position = position
        self._preprocessed: tuple[str, ...] = ()
        self._encoded: tuple[int, ...] = ()

    def get_position(self) -> int:
        """
        Returns the attribute
        :return: the position of the sentence in the text
        """
        return self._position

    def set_text(self, text: str) -> None:
        """
        Sets the attribute
        :param text: the text
        :return: None
        """
        check_type(text, str)
        self._text = text

    def get_text(self) -> str:
        """
        Returns the attribute
        :return: the text
        """
        return self._text

    def set_preprocessed(self, preprocessed_sentence: PreprocessedSentence) -> None:
        """
        Sets the attribute
        :param preprocessed_sentence: the preprocessed sentence (a sequence of tokens)
        :return: None
        """
        check_collection(preprocessed_sentence, str, tuple, can_be_empty=True)
        self._preprocessed = preprocessed_sentence

    def get_preprocessed(self) -> PreprocessedSentence:
        """
        Returns the attribute
        :return: the preprocessed sentence (a sequence of tokens)
        """
        return self._preprocessed

    def set_encoded(self, encoded_sentence: EncodedSentence) -> None:
        """
        Sets the attribute
        :param encoded_sentence: the encoded sentence (a sequence of numbers)
        :return: None
        """
        check_collection(encoded_sentence, int, tuple, can_be_empty=True)
        self._encoded = encoded_sentence

    def get_encoded(self) -> EncodedSentence:
        """
        Returns the attribute
        :return: the encoded sentence (a sequence of numbers)
        """
        return self._encoded


class SentencePreprocessor(TextPreprocessor):
    """
    Class for sentence preprocessing
    """

    def __init__(self, stop_words: tuple[str, ...], punctuation: tuple[str, ...]) -> None:
        """
        Constructs all the necessary attributes
        """
        check_collection(stop_words, str, tuple, can_be_empty=True)
        check_collection(punctuation, str, tuple, can_be_empty=True)
        super().__init__(stop_words, punctuation)
        self._stop_words = stop_words
        self._punctuation = punctuation

    def _split_by_sentence(self, text: str) -> tuple[Sentence, ...]:
        """
        Splits the provided text by sentence
        :param text: the raw text
        :return: a sequence of sentences
        """
        check_type(text, str)
        split_text = re.split(r'(?<=[.!?])\s+(?=[A-ZА-Я])', text.replace('\n', ' ').replace('  ', ' '))
        sentences_list = []
        for i, sentence in enumerate(split_text):
            my_sentence = Sentence(sentence, i)
            sentences_list.append(my_sentence)
        return tuple(sentences_list)

    def _preprocess_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Enriches the instances of sentences with their preprocessed versions
        :param sentences: a list of sentences
        :return:
        """
        check_collection(sentences, Sentence, tuple, can_be_empty=True)    # can_be_empty?
        for sentence in sentences:
            preprocessed = self.preprocess_text(sentence.get_text())
            sentence.set_preprocessed(preprocessed)

    def get_sentences(self, text: str) -> tuple[Sentence, ...]:
        """
        Extracts the sentences from the given text & preprocesses them
        :param text: the raw text
        :return:
        """
        check_type(text, str)
        split_text = self._split_by_sentence(text)
        self._preprocess_sentences(split_text)
        return split_text


class SentenceEncoder(TextEncoder):
    """
    A class to encode string sequence into matching integer sequence
    """
    def __init__(self, index: int = 1000) -> None:
        """
        Constructs all the necessary attributes
        """
        super().__init__()
        self._index = index

    def _learn_indices(self, tokens: tuple[str, ...]) -> None:
        """
        Fills attributes mapping words and integer equivalents to each other
        :param tokens: a sequence of string tokens
        :return:
        """
        check_collection(tokens, str, tuple, can_be_empty=True)    # can_be_empty?
        my_tokens = (token for token in tokens if token not in self._word2id)
        for ind, token in enumerate(my_tokens, start=self._index + len(self._word2id)):
            self._word2id[token] = ind
            self._id2word[ind] = token

    def encode_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Enriches the instances of sentences with their encoded versions
        :param sentences: a sequence of sentences
        :return: a list of sentences with their preprocessed versions
        """
        check_collection(sentences, Sentence, tuple, can_be_empty=True)
        for sentence in sentences:
            self._learn_indices(sentence.get_preprocessed())
            sentence.set_encoded(tuple(self._word2id[word] for word in sentence.get_preprocessed()))


def calculate_similarity(sequence: Union[list, tuple], other_sequence: Union[list, tuple]) -> float:
    """
    Calculates similarity between two sequences using Jaccard index
    :param sequence: a sequence of items
    :param other_sequence: a sequence of items
    :return: similarity score
    """
    check_type(sequence, (list, tuple))
    check_type(other_sequence, (list, tuple))
    if not sequence or not other_sequence:
        return 0.
    set_sequence = set(sequence)
    set_other_sequence = set(other_sequence)
    general_elements = set_sequence & set_other_sequence
    unique_elements = set_sequence | set_other_sequence
    return len(general_elements) / len(unique_elements)


class SimilarityMatrix:
    """
    A class to represent relations between sentences
    """
    def __init__(self) -> None:
        """
        Constructs necessary attributes
        """
        self._vertices = []
        self._matrix: list[list[float]] = []

    def get_vertices(self) -> tuple[Sentence, ...]:
        """
        Returns a sequence of all vertices present in the graph
        :return: a sequence of vertices
        """
        return tuple(self._vertices)

    def calculate_inout_score(self, vertex: Sentence) -> int:
        """
        Retrieves a number of vertices that are similar (i.e. have similarity score > 0) to the input one
        :param vertex
        :return:
        """
        check_type(vertex, Sentence)
        if vertex not in self._vertices:
            raise ValueError
        return sum(i > 0 for i in self._matrix[self._vertices.index(vertex)])

    def add_edge(self, vertex1: Sentence, vertex2: Sentence) -> None:
        """
        Adds or overwrites an edge in the graph between the specified vertices
        :param vertex1:
        :param vertex2:
        :return:
        """
        if vertex1 == vertex2:
            raise ValueError
        for vertex in vertex1, vertex2:
            check_type(vertex, Sentence)
            if vertex not in self._vertices:
                self._vertices.append(vertex)
                self._matrix.append([])

        for edges_list in self._matrix:
            if len(edges_list) < len(self._vertices):
                edges_list.extend([0 for _ in range(len(self._vertices) - len(edges_list))])

        idx1 = self._vertices.index(vertex1)
        idx2 = self._vertices.index(vertex2)
        similarity = calculate_similarity(vertex1.get_encoded(), vertex2.get_encoded())
        self._matrix[idx1][idx2] = similarity
        self._matrix[idx2][idx1] = similarity

    def get_similarity_score(self, sentence: Sentence, other_sentence: Sentence) -> float:
        """
        Gets the similarity score for two sentences from the matrix
        :param sentence
        :param other_sentence
        :return: the similarity score
        """
        if sentence not in self._vertices or other_sentence not in self._vertices:
            raise ValueError
        idx1 = self._vertices.index(sentence)
        idx2 = self._vertices.index(other_sentence)
        return self._matrix[idx1][idx2]

    def fill_from_sentences(self, sentences: tuple[Sentence, ...]) -> None:
        """
        Updates graph instance with vertices and edges extracted from sentences
        :param sentences
        :return:
        """
        check_collection(sentences, Sentence, tuple)
        for sentence1 in sentences:
            for sentence2 in sentences:
                if sentence1.get_encoded() != sentence2.get_encoded():
                    self.add_edge(sentence1, sentence2)


class TextRankSummarizer:
    """
    TextRank for summarization
    """
    def __init__(self, graph: SimilarityMatrix) -> None:
        """
        Constructs all the necessary attributes
        :param graph: the filled instance of the similarity matrix
        """
        check_type(graph, SimilarityMatrix)
        self._graph: SimilarityMatrix = graph
        self._damping_factor = 0.85
        self._convergence_threshold = 0.0001
        self._max_iter = 50
        self._scores: dict[Sentence, float] = {}

    def update_vertex_score(
            self, vertex: Sentence, incidental_vertices: list[Sentence], scores: dict[Sentence, float]
    ) -> None:
        """
        Changes vertex significance score using algorithm-specific formula
        :param vertex: a sentence
        :param incidental_vertices: vertices with similarity score > 0 for vertex
        :param scores: current vertices scores
        :return:
        """
        check_type(vertex, Sentence)
        check_collection(incidental_vertices, Sentence, list, can_be_empty=True)
        check_type(scores, dict)
        summa = sum((1 / self._graph.calculate_inout_score(inc_vertex)) * scores[inc_vertex]
                    for inc_vertex in incidental_vertices)
        self._scores[vertex] = summa * self._damping_factor + (1 - self._damping_factor)

    def train(self) -> None:
        """
        Iteratively computes significance scores for vertices
        """
        vertices = self._graph.get_vertices()
        for vertex in vertices:
            self._scores[vertex] = 1.0

        for iteration in range(self._max_iter):
            prev_score = self._scores.copy()
            for scored_vertex in vertices:
                similar_vertices = [vertex for vertex in vertices
                                    if self._graph.get_similarity_score(scored_vertex, vertex) > 0]
                self.update_vertex_score(scored_vertex, similar_vertices, prev_score)
            abs_score_diff = [abs(i - j) for i, j in zip(prev_score.values(), self._scores.values())]

            if sum(abs_score_diff) <= self._convergence_threshold:  # convergence condition
                print("Converging at iteration " + str(iteration) + "...")
                break

    def get_top_sentences(self, n_sentences: int) -> tuple[Sentence, ...]:
        """
        Retrieves top n most important sentences in the encoded text
        :param n_sentences: number of sentence to retrieve
        :return: a sequence of sentences
        """
        check_type(n_sentences, int)
        return tuple(sorted(self._scores, key=lambda sent: self._scores[sent], reverse=True))[:n_sentences]

    def make_summary(self, n_sentences: int) -> str:
        """
        Constructs summary from the most important sentences
        :param n_sentences: number of sentences to include in the summary
        :return: summary
        """
        check_type(n_sentences, int)
        sorted_sent = sorted(self.get_top_sentences(n_sentences), key=lambda x: x.get_position())
        return '\n'.join(sent.get_text() for sent in sorted_sent)


class NoRelevantTextsError(Exception):
    pass


class IncorrectQueryError(Exception):
    pass


class Buddy:
    """
    (Almost) All-knowing entity
    """

    def __init__(
            self,
            paths_to_texts: list[str],
            stop_words: tuple[str, ...],
            punctuation: tuple[str, ...],
            idf_values: dict[str, float],
    ):
        """
        Constructs all the necessary attributes
        :param paths_to_texts: paths to the texts from which to learn
        :param stop_words: a sequence of stop words
        :param punctuation: a sequence of punctuation symbols
        :param idf_values: pre-computed IDF values
        """
        check_collection(paths_to_texts, str, list)
        check_collection(stop_words, str, tuple)
        check_collection(punctuation, str, tuple)
        check_type(idf_values, dict)
        self._stop_words = stop_words
        self._punctuation = punctuation
        self._idf_values = idf_values
        self._text_preprocessor = TextPreprocessor(self._stop_words, self._punctuation)
        self._sentence_encoder = SentenceEncoder()
        self._sentence_preprocessor = SentencePreprocessor(self._stop_words, self._punctuation)
        self._paths_to_texts = paths_to_texts
        self._knowledge_database = {}

        for path in self._paths_to_texts:
            self.add_text_to_database(path)

    def add_text_to_database(self, path_to_text: str) -> None:
        """
        Adds the given text to the existing database
        :param path_to_text
        :return:
        """
        check_type(path_to_text, str)
        with open(path_to_text, 'r', encoding='utf-8') as file:
            text = file.read()

            sentences = self._sentence_preprocessor.get_sentences(text)
            self._sentence_encoder.encode_sentences(sentences)
            tokens = self._text_preprocessor.preprocess_text(text)

            tfidf = TFIDFAdapter(tokens, self._idf_values)
            tfidf.train()
            keywords = tfidf.get_top_keywords(100)

            matrix = SimilarityMatrix()
            matrix.fill_from_sentences(sentences)
            summarizer = TextRankSummarizer(matrix)
            summarizer.train()
            summary = summarizer.make_summary(5)

            self._knowledge_database[path_to_text] = {'sentences': sentences, 'keywords': keywords, 'summary': summary}

    def _find_texts_close_to_keywords(self, keywords: tuple[str, ...], n_texts: int) -> tuple[str, ...]:
        """
        Finds texts that are similar (i.e. contain the same keywords) to the given keywords
        :param keywords: a sequence of keywords
        :param n_texts: number of texts to find
        :return: the texts' ids
        """
        check_collection(keywords,  str, tuple)
        check_type(n_texts, int)
        similarity = {k: calculate_similarity(v['keywords'], keywords) for k, v in self._knowledge_database.items()}
        if not any(similarity.values()):
            raise NoRelevantTextsError('Texts that are related to the query were not found. Try another query.')
        return tuple(sorted(sorted(similarity, reverse=True), key=lambda key: similarity[key], reverse=True)[:n_texts])

    def reply(self, query: str, n_summaries: int = 3) -> str:
        """
        Replies to the query
        :param query: the query
        :param n_summaries: the number of summaries to include in the answer
        :return: the answer
        """
        if not query or not isinstance(query, str):
            raise IncorrectQueryError('Incorrect query. Use string as input.')
        check_type(n_summaries, int)
        if n_summaries > len(self._knowledge_database):
            raise ValueError
        keywords = self._sentence_preprocessor.preprocess_text(query)
        close_texts = self._find_texts_close_to_keywords(keywords, n_summaries)
        return 'Ответ:\n' + '\n\n'.join(self._knowledge_database[text]["summary"] for text in close_texts)
