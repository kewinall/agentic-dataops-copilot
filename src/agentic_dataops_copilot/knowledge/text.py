import re
import unicodedata

ASCII_TOKEN = re.compile(r"[a-z0-9][a-z0-9_.:/-]*")
CJK_RUN = re.compile(r"[\u3400-\u9fff]+")


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).lower()


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens = ASCII_TOKEN.findall(normalized)

    for run in CJK_RUN.findall(normalized):
        if len(run) == 1:
            tokens.append(run)
            continue
        tokens.extend(run[index : index + 2] for index in range(len(run) - 1))

    return tokens
