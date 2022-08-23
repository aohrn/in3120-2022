import re
from .expressioncomposer import ExpressionComposer
from typing import List, Dict, Optional, Any


class ShallowCaseExtractor:
    """
    Extracts strings from a buffer that are likely to be proper nouns of some kind: Names of people,
    locations, movies, whatever. The extraction is shallow and purely based on syntax cues in the form
    of case and punctuation: Strings that are capitalized are likely to be proper nouns, unless they start
    a new sentence. The extraction heuristic is slightly more refined than that, but not much.

    This is a sensible heuristic for many Western languages, except possibly German. Since the extraction
    is fundamentally based on case heuristics, applying it to text that has been case-normalized will result
    in zero matches. Applying it to languages that do not use whitespace to separate words, or applying it to
    languages that use case-less alphabets, will also not result in any matches.

    Buffers to be processed are assumed to be plain text, void of any markup. All markup such as HTML is assumed
    stripped away externally before this extraction heuristic is applied.
    """

    def __init__(self):
        grammar1 = {
            # E.g., empty lines between paragraphs or between a heading and a paragraph.
            "sep0": "\\n\\s*\\n",
            # Flow-breaking punctuation without context considerations. The inverted question
            # and exclamation marks might result in empty chunks, but that's benign.
            "sep1": "[¿?!¡:]\\s*",
            # Flow-breaking punctuation with context considerations. So not "Dr. Smith", "3.14", etc.
            # Negative look-behinds in Python must be fixed-width, so we have to group them accordingly.
            "sep2a": "(?<!\\bDr|Mr|Ms)",
            "sep2b": "(?<!\\bMrs|Rev)",
            "sep2c": "(?<!\\bProf)",
            "sep2": "{sep2a}{sep2b}{sep2c}\\.\\s+",
            # For consistency, also match the last period so that this gets stripped away. Generates
            # a trailing empty chunk, but that's benign.
            "sep3": "\\.\\s*\\Z",
            # Our top-level goal: A simple sentence boundary detector, that also deals with some malformed input.
            # Splitting stuff into sentences and also removing the flow-breaking punctuation enables us to
            # simplify the extraction grammar's context checks.
            "root": "{sep0}|{sep1}|{sep2}|{sep3}",
        }
        grammar2 = {
            # Basic case definitions. Deal with various accented symbols. Python's regular expression engine
            # does not support \p{Lu} or \p{Ll}, so list symbols explicitly.
            # TODO: These symbol sets can be made more restrictive if we see that it picks up a lot of noise.
            # TODO: These symbol sets can also be extended to include, e.g., Greek and Russian.
            "ucase": {
                "expression": "A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞĀĂĄĆĈĊČĎĐĒĔĖĘĚĜĞĠĢĤĦĨĪĬĮİĲĴĶĹĻĽĿŁŃŅŇŊŌŎŐŒŔŖŘŚŜŞŠŢŤŦŨŪŬŮŰŲŴŶŸŹŻŽ",
                "decorate": False,
            },
            "lcase": {
                "expression": "a-zªµºßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿāăąćĉċčďđēĕėęěĝğġģĥħĩīĭįıĳĵķĸĺļľŀłńņňŉŋōŏőœŕŗřśŝşšţťŧũūŭůűųŵŷźżž",
                "decorate": False,
            },
            # A word that initiates or is part of a proper noun. Contains a mix of uppercased and
            # lowercased symbols. This covers "Apple" and "iPhone", but not "apple" or "APPLE".
            # A single space between words will suffice, assuming that we sanitize the input buffer before
            # processing it.
            # TODO: This pattern can be made more restrictive if we see that it picks up a lot of noise.
            "cword0": "\\b[{ucase}]+[{lcase}][{ucase}{lcase}]*\\b",
            "cword1": "\\b[{lcase}]+[{ucase}][{ucase}{lcase}]*\\b",
            "cword": "{cword0}|{cword1}",
            # A lowercased "filler" word that is allowed to appear inside an interesting sequence, but not
            # start or end it. For example, as in "Lord of the Rings" or "Otto von Porat".
            "fword": "\\bof|the|and|von|der|de\\b",
            # An integer. Some proper nouns end with these, e.g., "Windows 95".
            "iword": "\\b\\d+\\b",
            # A honorific. As in, e.g., "Dr. Smith". See also the sentence boundary logic in the
            # chunker's grammar. We could merge the grammars if we wanted to share this logic.
            "hword": "\\bMr|Mrs|Ms|Dr|Prof|Rev\\b",
            # A proper noun-ish sequence to be extracted, not considering context. We allow some optional filler
            # words, and allow a trailing integer.
            "pseq0": "(?:{hword}\\.?\\s?)",
            "pseq1": "{cword}(?:[\\s\\-]{cword})*",
            "pseq2": "(?:(?:[\\s\\-]{fword}){{1,2}})(?:[\\s\\-]{cword})+",
            "pseq3": "(?:[\\s\\-]{iword})",
            "pseq": "{pseq0}?{pseq1}{pseq2}?{pseq3}?",
            # Define forbidden context: Does it look like we are starting a new sentence?
            # We assume that the chunker does sentence boundary detection and strips away flow-breaking
            # punctuation. This allows us to simplify the context check below. Note that look-behinds
            # have fixed-width requirements.
            "ctx0": "(?<!\\A)",
            "ctx1": '(?<!\\A")',
            "ctx": "{ctx0}{ctx1}",
            # Our top-level goal: A syntactically interesting sequence that doesn't violate the context requirements.
            "root": "{ctx}{pseq}",
        }
        grammar3 = {
            # Days of the week are not considered interesting matches.
            "mon": "\\bMon(?:day)?\\b",
            "tue": "\\bTue(?:sday)?\\b",
            "wed": "\\bWed(?:nesday)?\\b",
            "thu": "\\bThu(?:rsday)?\\b",
            "fri": "\\bFri(?:day)?\\b",
            "sat": "\\bSat(?:urday)?\\b",
            "sun": "\\bSun(?:day)?\\b",
            "day": "{mon}|{tue}|{wed}|{thu}|{fri}|{sat}|{sun}",
            # Names of months are not considered interesting matches.
            "jan": "\\bJan(?:uary)?\\b",
            "feb": "\\bFeb(?:ruary)?\\b",
            "mar": "\\bMar(?:ch)?\\b",
            "apr": "\\bApr(?:il)?\\b",
            "may": "\\bMay\\b",
            "jun": "\\bJun(?:e)?\\b",
            "jul": "\\bJul(?:y)?\\b",
            "aug": "\\bAug(?:ust)?\\b",
            "sep": "\\bSep(?:tember)?\\b",
            "oct": "\\bOct(?:ober)?\\b",
            "nov": "\\bNov(?:ember)?\\b",
            "dec": "\\bDec(?:ember)?\\b",
            "month": "{jan}|{feb}|{mar}|{apr}|{may}|{jun}|{jul}|{aug}|{sep}|{oct}|{nov}|{dec}",
            # Dates are not considered interesting matches.
            "date": "{month}\\s\\d\\d",
            # Our top-level goal: Stuff we want filtered out.
            # Don't decorate, to ensure that the flags are at the start of the expression.
            "root": {"decorate": False, "expression": "(?i)^(?:{day}|{month}|{date})$"},
        }
        self._chunker = re.compile(ExpressionComposer.from_grammar(grammar1, "root"))  # Splits buffers into chunks.
        self._matcher = re.compile(
            ExpressionComposer.from_grammar(grammar2, "root")
        )  # Extracts candidate matches from a chunk.
        self._cleaner = re.compile(ExpressionComposer.from_grammar(grammar3, "root"))  # Filters away known bad matches.

    def _chunkify_buffer(self, buffer: str, options: Dict[str, Any]) -> List[str]:
        """
        Not all buffers are well-formatted. For example, there might be consecutive newlines that indicate
        logical paragraph breaks or that separates a title from a "real" paragraph. Therefore, heuristically
        break the buffer up into one or more chunks, so that we can process each chunk individually and don't
        end up with messy cross-chunk matches.
        """
        chunks = self._chunker.split(buffer)
        return chunks

    def _preprocess_chunk(self, chunk: str, options: Dict[str, Any]) -> str:
        """
        Pre-processing the chunk allows us to simplify our extraction grammar, e.g., by normalizing spaces.
        This also enables us to in some cases work around limitations in Python's regular expression engine,
        e.g., since look-behind expressions have to be fixed-width.
        """
        chunk = chunk.strip()
        chunk = re.sub("\\s+", " ", chunk)
        return chunk

    def _postprocess_matches(self, matches: List[str], chunk: str, options: Dict[str, Any]) -> List[str]:
        """
        The extraction grammar is just a plain old regular expression, albeit a complex one. No real smarts or
        deeper understanding going on, apart from any smarts put into developing the grammar. As such, the matches
        might need to be post-processed somehow to improve quality.
        """
        # E.g., if we're fed a short title where almost everything is capitalized, we might get weird results
        # and would probably be better off not emitting any matches at all.
        if sum(len(match) for match in matches) > options.get("coverage_threshold", 0.7) * len(chunk):
            return []

        # Filter out known bad matches.
        matches = [match for match in matches if not self._cleaner.match(match)]

        # The surviving matches, if any.
        return matches

    def extract(self, buffer: str, options: Dict[str, Any] = {}) -> List[str]:
        """
        Extracts matches from the input buffer, and returns these.
        """
        chunks = self._chunkify_buffer(str(buffer or ""), options)
        chunks = [self._preprocess_chunk(chunk, options) for chunk in chunks]
        matches = [self._postprocess_matches(self._matcher.findall(chunk) or [], chunk, options) for chunk in chunks]
        matches = [match for sublist in matches for match in sublist]
        return matches
