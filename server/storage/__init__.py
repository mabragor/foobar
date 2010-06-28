# -*- coding: utf-8 -*-

def translit(value):
    TRANSTABLE = (
        (u"а", u"a"),   (u"б", u"b"),   (u"в", u"v"),   (u"г", u"g"),
        (u"д", u"d"),   (u"е", u"e"),   (u"ё", u"yo"),  (u"ж", u"zh"),
        (u"з", u"z"),   (u"и", u"i"),   (u"й", u"j"),   (u"к", u"k"),
        (u"л", u"l"),   (u"м", u"m"),   (u"н", u"n"),   (u"о", u"o"),
        (u"п", u"p"),   (u"р", u"r"),   (u"с", u"s"),   (u"т", u"t"),
        (u"у", u"u"),   (u"ф", u"f"),   (u"х", u"h"),   (u"ц", u"ts"),
        (u"ч", u"ch"),  (u"ш", u"sh"),  (u"щ", u"sch"), (u"ъ", u"_"),
        (u"ы", u"yi"),  (u"ь", u""),    (u"э", u"e"),   (u"ю", u"yu"),
        (u"я", u"ya"),  (u" ", u"_"),
        )
    translit = value.lower()
    for symb_in, symb_out in TRANSTABLE:
        translit = translit.replace(symb_in, symb_out)
    return translit
