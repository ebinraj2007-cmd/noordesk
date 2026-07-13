"""Role/profile system: personal vs business replies, and persistence."""
from noordesk import profile as profiles
from noordesk.responder import draft_reply, PERSONAL
from noordesk.pipeline import process_message


def test_personal_mode_generic_reply():
    r = draft_reply("price_enquiry", "en", {"mode": "personal", "name": "Ebin"})
    assert r.startswith(PERSONAL["en"])
    assert r.endswith("Ebin")          # signed with the person's name


def test_business_mode_intent_reply():
    r = draft_reply("price_enquiry", "en", {"mode": "business", "phone": "+9714"})
    assert "pricing" in r.lower()
    assert "+9714" in r                # grounded with the business phone


def test_personal_reply_stays_in_language():
    r = process_message({"id": "x", "sender": "s", "raw_text": "أريد حجز موعد"},
                        profile={"mode": "personal"})
    assert r["detected_language"] == "ar"
    assert any(ord(c) > 0x0590 for c in r["suggested_reply"])   # Arabic reply


def test_profile_save_and_load_roundtrip():
    profiles.save({"role": "restaurant", "name": "Cafe Noor",
                   "products": [{"name": "Latte", "price": "AED 18"}]})
    p = profiles.load()
    assert p["configured"] is True
    assert p["role"] == "restaurant"
    assert p["mode"] == "business"          # derived from the role
    assert p["name"] == "Cafe Noor"
    assert p["products"][0]["price"] == "AED 18"


def test_price_reply_lists_products():
    from noordesk.responder import draft_reply
    reply = draft_reply("price_enquiry", "en", {
        "mode": "business", "role": "shop",
        "products": [{"name": "Cable", "price": "AED 15"}, {"name": "Charger", "price": "AED 40"}],
    })
    assert "Cable" in reply and "AED 15" in reply and "Charger" in reply


def test_default_profile_unconfigured():
    assert profiles.load()["configured"] is False
