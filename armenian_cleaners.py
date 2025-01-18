"""Set of default text cleaners"""
# TODO: pick the cleaner for languages dynamically

import re

from anyascii import anyascii

from TTS.tts.utils.text.chinese_mandarin.numbers import replace_numbers_to_characters_in_text

from .english.abbreviations import abbreviations_en
from .english.number_norm import normalize_numbers as en_normalize_numbers
from .english.time_norm import expand_time_english
from .french.abbreviations import abbreviations_fr

# Regular expression matching whitespace:
_whitespace_re = re.compile(r"\s+")


def expand_abbreviations(text, lang="en"):
    if lang == "en":
        _abbreviations = abbreviations_en
    elif lang == "fr":
        _abbreviations = abbreviations_fr
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text


def lowercase(text):
    return text.lower()


def collapse_whitespace(text):
    return re.sub(_whitespace_re, " ", text).strip()


def convert_to_ascii(text):
    return anyascii(text)


def remove_aux_symbols(text):
    text = re.sub(r"[\<\>\(\)\[\]\"]+", "", text)
    return text


def replace_symbols(text, lang="en"):
    """Replace symbols based on the lenguage tag.

    Args:
      text:
       Input text.
      lang:
        Lenguage identifier. ex: "en", "fr", "pt", "ca".

    Returns:
      The modified text
      example:
        input args:
            text: "si l'avi cau, diguem-ho"
            lang: "ca"
        Output:
            text: "si lavi cau, diguemho"
    """
    text = text.replace(";", ",")
    text = text.replace("-", " ") if lang != "ca" else text.replace("-", "")
    text = text.replace(":", ",")
    if lang == "en":
        text = text.replace("&", " and ")
    elif lang == "fr":
        text = text.replace("&", " et ")
    elif lang == "pt":
        text = text.replace("&", " e ")
    elif lang == "ca":
        text = text.replace("&", " i ")
        text = text.replace("'", "")
    return text


def basic_cleaners(text):
    """Basic pipeline that lowercases and collapses whitespace without transliteration."""
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def transliteration_cleaners(text):
    """Pipeline for non-English text that transliterates to ASCII."""
    # text = convert_to_ascii(text)
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def basic_german_cleaners(text):
    """Pipeline for German text"""
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


# TODO: elaborate it
def basic_turkish_cleaners(text):
    """Pipeline for Turkish text"""
    text = text.replace("I", "ı")
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def english_cleaners(text):
    """Pipeline for English text, including number and abbreviation expansion."""
    # text = convert_to_ascii(text)
    text = lowercase(text)
    text = expand_time_english(text)
    text = en_normalize_numbers(text)
    text = expand_abbreviations(text)
    text = replace_symbols(text)
    text = remove_aux_symbols(text)
    text = collapse_whitespace(text)
    return text


def phoneme_cleaners(text):
    """Pipeline for phonemes mode, including number and abbreviation expansion."""
    text = en_normalize_numbers(text)
    text = expand_abbreviations(text)
    text = replace_symbols(text)
    text = remove_aux_symbols(text)
    text = collapse_whitespace(text)
    return text

_armenian_numbers = re.compile(r'(\d+)')
# Regular expression for Armenian numbers

# Armenian alphabet and some common punctuation
_armenian_alphabet = set('աբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփքևօֆԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔԵՎՕՖ')
_armenian_punctuations = set('։՝՜՞:,.!?')


def _armenian_num2words(number):
    """Convert a number to its Armenian word representation."""
    if not 0 <= number <= 999999999999:
        return "Number out of range (0-999,999,999,999)"

    units = ["", "մեկ", "երկու", "երեք", "չորս", "հինգ", "վեց", "յոթ", "ութ", "ինը"]
    teens = ["տաս", "տասնմեկ", "տասներկու", "տասներեք", "տասնչորս", "տասնհինգ", "տասնվեց", "տասնյոթ", "տասնութ", "տասնինը"]
    tens = ["", "", "քսան", "երեսուն", "քառասուն", "հիսուն", "վաթսուն", "յոթանասուն", "ութսուն", "իննսուն"]
    scales = ["", "հազար", "միլիոն", "միլիարդ"]

    def convert_group(n, scale):
        if n == 0:
            return ""

        result = []

        if n >= 100:
            result.append(units[n // 100])
            result.append("հարյուր")
            n %= 100

        if n >= 20:
            result.append(tens[n // 10])
            if n % 10 != 0:
                result.append(units[n % 10])
        elif n >= 10:
            result.append(teens[n - 10])
        elif n > 0:
            result.append(units[n])

        if scale > 0 and len(result) > 0:
            result.append(scales[scale])

        return " ".join(result)

    if number == 0:
        return "զրո"

    result = []
    for i in range(4):
        group = (number // (1000 ** i)) % 1000
        if group != 0:
            result.insert(0, convert_group(group, i))

    return " ".join(result).strip()


def _normalize_numbers(text):
    """Convert numbers to words in Armenian."""

    def _num_to_word(match):
        number = int(match.group(0))
        return _armenian_num2words(number)

    return re.sub(_armenian_numbers, _num_to_word, text)


def _remove_non_armenian_characters(text):
    """Remove characters that are not Armenian letters or common punctuation."""
    return ''.join(
        char for char in text if char in _armenian_alphabet or char in _armenian_punctuations or char.isspace())


def _normalize_punctuation(text):
    """Normalize some punctuation."""
    text = text.replace('՝', ',')  # Replace Armenian comma with standard comma
    text = text.replace('։', ':')  # Replace Armenian full stop with colon
    text = text.replace('—', '-')  # Replace em dash with hyphen
    return text


def armenian_cleaners(text):
    """Pipeline for Armenian text cleaning."""
    text = text.lower()
    text = _normalize_numbers(text)
    text = _remove_non_armenian_characters(text)
    text = _normalize_punctuation(text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def french_cleaners(text):
    """Pipeline for French text. There is no need to expand numbers, phonemizer already does that"""
    text = expand_abbreviations(text, lang="fr")
    text = lowercase(text)
    text = replace_symbols(text, lang="fr")
    text = remove_aux_symbols(text)
    text = collapse_whitespace(text)
    return text


def portuguese_cleaners(text):
    """Basic pipeline for Portuguese text. There is no need to expand abbreviation and
    numbers, phonemizer already does that"""
    text = lowercase(text)
    text = replace_symbols(text, lang="pt")
    text = remove_aux_symbols(text)
    text = collapse_whitespace(text)
    return text


def chinese_mandarin_cleaners(text: str) -> str:
    """Basic pipeline for chinese"""
    text = replace_numbers_to_characters_in_text(text)
    return text


def multilingual_cleaners(text):
    """Pipeline for multilingual text"""
    text = lowercase(text)
    text = replace_symbols(text, lang=None)
    text = remove_aux_symbols(text)
    text = collapse_whitespace(text)
    return text


def no_cleaners(text):
    # remove newline characters
    text = text.replace("\n", "")
    return text
