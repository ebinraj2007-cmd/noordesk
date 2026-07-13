"""Reply drafting. Per-language, per-intent templates.

Guarantee: the reply is always in the customer's detected language.
Optional FAQ grounding injects real business facts (hours, phone) when provided.
"""
from __future__ import annotations

from typing import Optional, Dict

# templates[lang][intent] -> reply text. Every supported language covers every intent.
TEMPLATES: Dict[str, Dict[str, str]] = {
    "en": {
        "booking": "Thank you for your booking request. We'd be happy to help — could you share your preferred date and time?{hours}",
        "complaint": "We're very sorry to hear about this and take it seriously. Could you share a few more details so we can make it right as soon as possible?",
        "price_enquiry": "Thanks for your interest! We'll send you the pricing details right away.{phone}",
        "support": "Thanks for reaching out. We're on it — could you tell us a bit more about the issue so we can help quickly?",
        "spam": "",
        "general": "Thank you for your message. A member of our team will get back to you shortly.{hours}",
    },
    "ar": {
        "booking": "شكرًا لطلب الحجز. يسعدنا مساعدتك — هل يمكنك تحديد التاريخ والوقت المناسبين لك؟{hours}",
        "complaint": "نأسف جدًا لما حدث ونتعامل مع الأمر بجدية. هل يمكنك تزويدنا بمزيد من التفاصيل حتى نصحح الأمر في أسرع وقت؟",
        "price_enquiry": "شكرًا لاهتمامك! سنرسل لك تفاصيل الأسعار على الفور.{phone}",
        "support": "شكرًا لتواصلك معنا. نحن نعمل على ذلك — هل يمكنك إخبارنا بمزيد من التفاصيل عن المشكلة لمساعدتك بسرعة؟",
        "spam": "",
        "general": "شكرًا لرسالتك. سيتواصل معك أحد أعضاء فريقنا قريبًا.{hours}",
    },
    "ml": {
        "booking": "ബുക്കിംഗ് അഭ്യർത്ഥനയ്ക്ക് നന്ദി. സഹായിക്കാൻ ഞങ്ങൾ സന്തോഷിക്കുന്നു — നിങ്ങൾക്ക് സൗകര്യപ്രദമായ തീയതിയും സമയവും അറിയിക്കാമോ?{hours}",
        "complaint": "ഇത് കേട്ടതിൽ ഞങ്ങൾക്ക് അതിയായ ഖേദമുണ്ട്, ഇത് ഗൗരവമായി കാണുന്നു. എത്രയും വേഗം പരിഹരിക്കാൻ കുറച്ച് വിശദാംശങ്ങൾ കൂടി പങ്കുവെക്കാമോ?",
        "price_enquiry": "താൽപ്പര്യത്തിന് നന്ദി! വിലവിവരങ്ങൾ ഉടൻ അയച്ചുതരാം.{phone}",
        "support": "ബന്ധപ്പെട്ടതിന് നന്ദി. ഞങ്ങൾ ഇത് പരിഹരിക്കുന്നു — വേഗത്തിൽ സഹായിക്കാൻ പ്രശ്നത്തെക്കുറിച്ച് കുറച്ചുകൂടി പറയാമോ?",
        "spam": "",
        "general": "നിങ്ങളുടെ സന്ദേശത്തിന് നന്ദി. ഞങ്ങളുടെ ടീം ഉടൻ നിങ്ങളെ ബന്ധപ്പെടും.{hours}",
    },
    "ta": {
        "booking": "உங்கள் முன்பதிவு கோரிக்கைக்கு நன்றி. உதவ மகிழ்ச்சி — உங்களுக்கு வசதியான தேதி மற்றும் நேரத்தைத் தெரிவிக்க முடியுமா?{hours}",
        "complaint": "இதைக் கேட்டதற்கு மிகவும் வருந்துகிறோம், இதை தீவிரமாக எடுத்துக்கொள்கிறோம். விரைவில் சரிசெய்ய இன்னும் சில விவரங்களைப் பகிர முடியுமா?",
        "price_enquiry": "உங்கள் ஆர்வத்திற்கு நன்றி! விலை விவரங்களை உடனே அனுப்புகிறோம்.{phone}",
        "support": "தொடர்பு கொண்டதற்கு நன்றி. நாங்கள் பார்த்துக்கொள்கிறோம் — விரைவில் உதவ பிரச்சனை பற்றி இன்னும் கொஞ்சம் சொல்ல முடியுமா?",
        "spam": "",
        "general": "உங்கள் செய்திக்கு நன்றி. எங்கள் குழு விரைவில் உங்களைத் தொடர்பு கொள்ளும்.{hours}",
    },
    "fr": {
        "booking": "Merci pour votre demande de réservation. Nous serions ravis de vous aider — pourriez-vous indiquer la date et l'heure qui vous conviennent ?{hours}",
        "complaint": "Nous sommes vraiment désolés et prenons cela au sérieux. Pourriez-vous nous donner quelques détails afin que nous puissions résoudre cela au plus vite ?",
        "price_enquiry": "Merci de votre intérêt ! Nous vous envoyons les tarifs tout de suite.{phone}",
        "support": "Merci de nous avoir contactés. Nous nous en occupons — pourriez-vous préciser le problème pour que nous puissions vous aider rapidement ?",
        "spam": "",
        "general": "Merci pour votre message. Un membre de notre équipe vous répondra très bientôt.{hours}",
    },
}


# Personal mode: a single warm auto-reply per language (no business specifics).
PERSONAL = {
    "en": "Thanks for your message! I'll get back to you as soon as I can.",
    "ar": "شكرًا لرسالتك! سأرد عليك في أقرب وقت ممكن.",
    "ml": "നിങ്ങളുടെ സന്ദേശത്തിന് നന്ദി! എത്രയും വേഗം ഞാൻ മറുപടി നൽകാം.",
    "ta": "உங்கள் செய்திக்கு நன்றி! விரைவில் நான் பதிலளிக்கிறேன்.",
    "fr": "Merci pour votre message ! Je vous réponds dès que possible.",
}


# Small-talk: greet back, thank, and sign off like a real chatbot.
# Words are grouped by language so a short "hi"/"bye" replies in English, not
# whatever the (unreliable for 1-2 words) language detector guessed.
SMALLTALK_WORDS = {
    "greeting": {
        "ar": ["مرحبا", "اهلا", "أهلا", "السلام", "هاي"],
        "ml": ["ഹായ്", "നമസ്കാരം", "ഹലോ"],
        "ta": ["வணக்கம்", "ஹாய்", "ஹலோ"],
        "en": ["hi", "hii", "hiii", "hiiii", "hello", "helo", "hey", "heya", "hiya",
               "yo", "wassup", "wasup", "sup", "whatsup", "howdy", "gm",
               "good morning", "good afternoon", "good evening"],
        "fr": ["salut", "bonjour", "coucou", "hola", "hallo"],
    },
    "thanks": {
        "ar": ["شكرا", "شكرًا"], "ml": ["നന്ദി"], "ta": ["நன்றி"],
        "en": ["thank", "thanks", "thankyou", "thx", "ty", "shukran", "nandri"],
        "fr": ["merci"],
    },
    "bye": {
        "ar": ["مع السلامة", "وداعا"], "ml": ["വിട"], "ta": ["பிறகு"],
        "en": ["bye", "goodbye", "see you", "see ya", "cya", "take care", "gotta go"],
        "fr": ["au revoir", "à bientôt"],
    },
}
SMALLTALK_REPLY = {
    "greeting": {
        "en": "Hey! 👋 How can I help you today?",
        "ar": "مرحبًا! 👋 كيف يمكنني مساعدتك اليوم؟",
        "ml": "ഹായ്! 👋 എന്ത് സഹായം വേണം?",
        "ta": "வணக்கம்! 👋 நான் எப்படி உதவட்டும்?",
        "fr": "Salut ! 👋 Comment puis-je vous aider ?"},
    "thanks": {
        "en": "You're welcome! 😊 Anything else I can help with?",
        "ar": "على الرحب والسعة! 😊 هل تحتاج أي شيء آخر؟",
        "ml": "സന്തോഷം! 😊 വേറെ എന്തെങ്കിലും വേണോ?",
        "ta": "பரவாயில்லை! 😊 வேறு ஏதேனும் வேண்டுமா?",
        "fr": "Avec plaisir ! 😊 Autre chose ?"},
    "bye": {
        "en": "Take care! 👋 Talk soon.", "ar": "مع السلامة! 👋",
        "ml": "വിട! 👋", "ta": "பிறகு பார்க்கலாம்! 👋", "fr": "À bientôt ! 👋"},
}
_LANG_ORDER = ["ar", "ml", "ta", "en", "fr"]   # distinct scripts first


def _smalltalk(text: str, lang: str):
    """Return a conversational reply for greetings / thanks / goodbye, else None.
    The reply language comes from the matched word, not the detector."""
    t = (text or "").lower().strip()
    if not t:
        return None
    n_words = len(t.split())
    for kind in ("thanks", "bye", "greeting"):
        if kind == "greeting" and n_words > 4:
            continue   # "hi, do you deliver?" should route to the real answer
        for lg in _LANG_ORDER:
            if any(w in t for w in SMALLTALK_WORDS[kind][lg]):
                return SMALLTALK_REPLY[kind][lg]
    return None


def draft_reply(intent: str, lang: str, profile: Optional[dict] = None, text: str = "") -> str:
    lang = lang if lang in TEMPLATES else "en"
    profile = profile or {}
    if intent == "spam":
        return ""  # never auto-reply to spam

    # Conversational small-talk first (both personal and business modes).
    st = _smalltalk(text, lang)
    if st:
        return st

    # Personal mode: a generic friendly acknowledgement, optionally signed.
    if profile.get("mode") == "personal":
        reply = PERSONAL[lang]
        name = (profile.get("name") or "").strip()
        if name:
            reply += " — " + name
        return reply

    # Business + a pricing question + products on file -> quote the price list.
    if intent == "price_enquiry":
        priced = [q for q in (profile.get("products") or []) if q.get("name") and q.get("price")]
        if priced:
            intro = {"en": "Here's our pricing:", "ar": "إليك قائمة أسعارنا:",
                     "ml": "ഞങ്ങളുടെ വിലവിവരം ഇതാ:", "ta": "எங்கள் விலைப்பட்டியல்:",
                     "fr": "Voici nos tarifs :"}[lang]
            lines = "\n".join("• " + q["name"] + " — " + q["price"] for q in priced[:10])
            return intro + "\n" + lines

    # Business mode: intent-specific template, grounded with hours/phone.
    template = TEMPLATES[lang].get(intent, TEMPLATES[lang]["general"])
    if not template:
        return ""

    hours = ""
    phone = ""
    if intent in ("booking", "general") and profile.get("hours"):
        label = {"en": " Our hours: ", "ar": " ساعات العمل: ", "ml": " ഞങ്ങളുടെ സമയം: ",
                 "ta": " எங்கள் நேரம்: ", "fr": " Nos horaires : "}[lang]
        hours = label + str(profile["hours"])
    if intent == "price_enquiry" and profile.get("phone"):
        label = {"en": " Call us: ", "ar": " اتصل بنا: ", "ml": " വിളിക്കുക: ",
                 "ta": " அழைக்கவும்: ", "fr": " Appelez-nous : "}[lang]
        phone = label + str(profile["phone"])

    return template.format(hours=hours, phone=phone)
