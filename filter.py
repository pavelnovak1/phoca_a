import random
import sys
import threading


class Filter():
    WHITELIST = [
        ".amazonaws.com",
        ".microsoft.com"
    ]
    SUSP_NAMES = [
        "airbnb",
        "abnb",
        "amazon",
        "booking",
        "citrix",
        "coinbase",
        "facebook",
        "github",
        "instagram",
        "linkedin",
        "o365",
        "office365",
        "microsoft",
        "outlook",
        "okta",
        "onelogin",
        "paypal",
        "protonmail",
        "reddit",
        "tiktok",
        "twitter",
        "wordpress"
    ]

    SUSP_TLD = [
        "abc",
        "app",
        "bank",
        "bar",
        "bet",
        "bid",
        "biz",
        "business",
        "buzz",
        "by",
        "cam",
        "casa",
        "cc",
        "center",
        "cf",
        "cl",
        "cloud",
        "club",
        "cn",
        "cool",
        "country",
        "cricket",
        "cyou",
        "date",
        "dev",
        "download",
        "fit",
        "fun",
        "ga",
        "gdn",
        "gq",
        "gratis",
        "host",
        "icu",
        "id",
        "in",
        "info",
        "kim",
        "life",
        "link",
        "live",
        "loan",
        "me",
        "men",
        "ml",
        "mobi",
        "mom",
        "monster",
        "ng",
        "np",
        "okinawa",
        "online",
        "page",
        "party",
        "ph",
        "press",
        "pro",
        "pw",
        "qrs",
        "racing",
        "recipes",
        "review",
        "ryukyu",
        "sbs",
        "science",
        "shop",
        "site",
        "space",
        "store",
        "stream",
        "study",
        "support",
        "surf",
        "tech",
        "th",
        "tk",
        "today",
        "tokyo",
        "top",
        "uno",
        "viajes",
        "vip",
        "website",
        "win",
        "work",
        "xxx",
        "xyz",
        "zyx",
        "zzz"
    ]

    THRESHOLD = 1

    @staticmethod
    def process(cert, storage):
        domains = Filter.cert_decision(cert)
        for domain in domains:
            storage.push(domain)

    @staticmethod
    def cert_decision(cert):
        domains = Filter.Parser.cert_get_domains(cert)
        return [domain.strip() for domain in domains if Filter.Comparator.decide(domain, Filter.THRESHOLD)]

    class Parser:

        @staticmethod
        def cert_get_domains(cert):
            return cert["data"]["leaf_cert"]["all_domains"]

        @staticmethod
        def parse_domain(domain):
            return domain.split(".")

    class Comparator:
        @staticmethod
        def is_susp_tld(tld):
            return tld in Filter.SUSP_TLD

        @staticmethod
        def is_on_whitelist(domain):
            for whitelisted in Filter.WHITELIST:
                if domain.endswith(whitelisted):
                    return True
            return False

        @staticmethod
        def contains_keyword(parsed_domain):
            for subdomain in parsed_domain:
                for keyword in Filter.SUSP_NAMES:
                    if keyword in subdomain:
                        return True
            return False

        @staticmethod
        def decide(domain, threshold=1):
            if "*" in domain or Filter.Comparator.is_on_whitelist(domain):
                return False
            parsed_domain = Filter.Parser.parse_domain(domain)
            if Filter.Comparator.is_susp_tld(parsed_domain[-1]):
                pass

            if Filter.Comparator.contains_keyword(parsed_domain):
                return True
            return False

