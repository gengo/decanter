import re

from bottle import request
from babel import support, Locale

from .config import Config

# Format of http.request.header.Accept-Language.
# refs: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
REQUEST_ACCEPT_LANGUAGE_RE = re.compile(r'''
        ([A-Za-z]{1,8}(?:-[A-Za-z]{1,8})*|\*)   # "en", "en-au", "*"
        (?:;q=(0(?:\.\d{,3})?|1(?:.0{,3})?))?   # Optional "q=1.00", "q=0.8"
        (?:\s*,\s*|$)                           # Multiple accepts per header.
        ''', re.VERBOSE)

def extra_client_expected_langs():
    """Return language list from http.request.header.Accept-Language,
    ordered by 'q'."""
    result = []
    pieces = REQUEST_ACCEPT_LANGUAGE_RE.split(
        request.headers.get('Accept-Language', ''))
    if pieces[-1]:
        return []
    for i in range(0, len(pieces) - 1, 3):
        first, lang, priority = pieces[i: i + 3]
        if lang == '*':  # TODO: support default language
            return []
        if first:
            return []
        priority = priority and float(priority) or 1.0
        result.append((lang, priority))
    result.sort(key=lambda k: k[1], reverse=True)
    return result


def get_language_list():
    """Return a sorted list of language code-formatted languages in
    descending order of priority.
    """
    config = Config()
    lang_code = getattr(config, 'lang_code', 'en')

    expected_langs = extra_client_expected_langs()

    lang_codes = []

    for lang, priority in expected_langs:
        lang_country = lang.split('-')
        if len(lang_country) == 1:
            lang_codes.append(lang)
            continue
        country = lang_country[1]
        lang_codes.append('%s_%s' % (lang_country[0], country))
        lang_codes.append('%s_%s' % (lang_country[0], country.swapcase()))

    if not lang_code is None:
        lang_codes += [lang_code]

    return lang_codes


def locale_selector_func():
    lc_list = get_language_list()
    if lc_list:
        return lc_list[0]
    return 'en'


def get_translations():
    """Returns the correct gettext translations that should be used for
    this request.  This will never fail and return a dummy translation
    object if used outside of the request or if a translation cannot be
    found.
    """
    config = Config()
    domain = getattr(config, 'domain', 'locale')
    locale_dir = getattr(config, 'locale_dir')

    translations = request.environ.get('babel_translations', None)
    if translations is None:
        translations = support.Translations.load(locale_dir, [get_locale()])
        request.environ['babel_translations'] = translations
    return translations


def get_locale():
    """Returns the locale that should be used for this request as
    `babel.Locale` object.  This returns `None` if used outside of
    a request.
    """
    config = Config()
    locale = request.environ.get('babel_locale', None)
    if locale is None:
        preferred_lc = locale_selector_func()
        if not preferred_lc:
            locale = getattr(config, 'lang_code', 'en')
        else:
            locale = preferred_lc
        request.environ['babel_locale'] = locale
    return locale


def gettext(string, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.

    ::

        gettext(u'Hello World!')
        gettext(u'Hello %(name)s!', name='World')
    """
    t = get_translations()
    if t is None:
        return string % variables
    return t.ugettext(string) % variables

_ = gettext


def ngettext(singular, plural, num, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.
    The `num` parameter is used to dispatch between singular and various
    plural forms of the message.  It is available in the format string
    as ``%(num)d`` or ``%(num)s``.  The source language should be
    English or a similar language which only has one plural form.

    ::

        ngettext(u'%(num)d Apple', u'%(num)d Apples', num=len(apples))
    """
    variables.setdefault('num', num)
    t = get_translations()
    if t is None:
        return (singular if num == 1 else plural) % variables
    return t.ungettext(singular, plural, num) % variables


def pgettext(context, string, **variables):
    """Like :func:`gettext` but with a context.
    """
    t = get_translations()
    if t is None:
        return string % variables
    return t.upgettext(context, string) % variables


def npgettext(context, singular, plural, num, **variables):
    """Like :func:`ngettext` but with a context.
    """
    variables.setdefault('num', num)
    t = get_translations()
    if t is None:
        return (singular if num == 1 else plural) % variables
    return t.unpgettext(context, singular, plural, num) % variables