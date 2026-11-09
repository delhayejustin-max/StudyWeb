#!/usr/bin/env python3
"""Build src/data/anatomie.json from verbatim spans of Anatomie du chien.

The correct option and the excerpt are PDF spans. For ordinary questions, the
other options are false relative to this PDF and are not another true sentence.
The numbered schema uses only the number-to-name key written in the PDF.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "public" / "Anatomie_du_chien_synthese.pdf"
OUT = ROOT / "src" / "data" / "anatomie.json"
SCHEMA = "/schema-anatomie-chien.jpg"
DASH = "\u2013"

TITLES = [
    f"Schéma original {DASH} photo entière",
    "Repères du schéma",
    "1. Classification des chiens",
    "2. Les trois types d'os",
    "3. Anatomie d'un os long",
    "4. Les régions de la tête et du tronc",
    "5. Les membres",
    "6. Os du membre antérieur",
    "7. Régions ventrales et bassin",
    "8. Vocabulaire à retenir",
]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\f", " ")).strip()


def load_pdf() -> str:
    raw = subprocess.check_output(
        ["pdftotext", "-raw", "-enc", "UTF-8", str(PDF), "-"],
        text=True,
    )
    return norm(raw)


def section_slices(full: str) -> dict[str, str]:
    indexes = []
    for title in TITLES:
        at = full.find(title)
        if at < 0:
            raise SystemExit(f"section title missing: {title}")
        indexes.append((at, title))
    indexes.sort()
    bodies: dict[str, str] = {}
    for i, (at, title) in enumerate(indexes):
        end = indexes[i + 1][0] if i + 1 < len(indexes) else len(full)
        bodies[title] = full[at:end]
    return bodies


def schema_key(full: str) -> list[tuple[str, str]]:
    start = full.find("Repères du schéma")
    end = full.find("1. Classification des chiens")
    if start < 0 or end < 0 or end <= start:
        raise SystemExit("schema key block missing")
    block = full[start:end]
    found = re.findall(r"(\d+)\.\s+(.*?)(?=\s+\d+\.\s+|$)", block)
    items = [(number, label.strip()) for number, label in found]
    items.sort(key=lambda item: int(item[0]))
    if [number for number, _ in items] != [str(n) for n in range(1, 34)]:
        raise SystemExit(f"schema numbers are not 1..33: {[n for n, _ in items]}")
    labels = [label for _, label in items]
    if len(set(labels)) != len(labels):
        raise SystemExit("schema key has a repeated label")
    for number, label in items:
        source = f"{number}. {label}"
        if source not in full:
            raise SystemExit(f"schema line missing from PDF: {source}")
    return items


class Bank:
    def __init__(self) -> None:
        self.sections: list[dict] = []
        self._current: dict | None = None

    def section(self, sid: str, title: str) -> None:
        self._current = {"id": sid, "title": title, "questions": []}
        self.sections.append(self._current)

    def mc(
        self,
        qid: str,
        prompt: str,
        choices: list[tuple[str, str]],
        correct: str,
        source: str,
        image: str | None = None,
    ) -> None:
        assert self._current is not None
        question = {
            "id": qid,
            "type": "mc",
            "prompt": prompt,
            "choices": [{"id": cid, "text": text} for cid, text in choices],
            "correctChoiceId": correct,
            "source": source,
        }
        if image:
            question["image"] = image
        self._current["questions"].append(question)


def other_labels(key: list[tuple[str, str]], index: int, correct: str) -> list[str]:
    chosen: list[str] = []
    step = 0
    while len(chosen) < 3:
        if step >= len(key):
            raise SystemExit(f"not enough other labels for {correct}")
        _, candidate = key[(index + 1 + step) % len(key)]
        step += 1
        if candidate == correct or candidate in chosen:
            continue
        chosen.append(candidate)
    return chosen


def add_schema(bank: Bank, key: list[tuple[str, str]]) -> None:
    bank.section("a2", "Repères du schéma")
    slots = ["a", "b", "c", "d"]
    allowed = {label for _, label in key}
    for index, (number, label) in enumerate(key):
        distractors = other_labels(key, index, label)
        correct_slot = slots[index % 4]
        choices: list[tuple[str, str]] = []
        distractor_at = 0
        for slot in slots:
            if slot == correct_slot:
                choices.append((slot, label))
            else:
                choices.append((slot, distractors[distractor_at]))
                distractor_at += 1
        texts = [text for _, text in choices]
        if texts.count(label) != 1 or len(set(texts)) != 4:
            raise SystemExit(f"schema {number} does not have one unique answer")
        if any(text not in allowed for text in texts):
            raise SystemExit(f"schema {number} uses a label outside the key")
        bank.mc(
            f"a2-d{index + 1}",
            f"Sur le schéma, que désigne le numéro {number} ?",
            choices,
            correct_slot,
            f"{number}. {label}",
            SCHEMA,
        )


def build(key: list[tuple[str, str]]) -> dict:
    b = Bank()
    b.section("a1", TITLES[0])
    b.mc(
        "a1-q1",
        "Que dit le texte de la photo du schéma ?",
        [
            ("a", "La photo complète est recadrée avant d’être posée."),
            ("b", "La photo complète est conservée, sans recadrage."),
            ("c", "La photo complète est remplacée par un dessin neuf."),
            ("d", "La photo complète est coupée pour ne garder que la tête."),
        ],
        "b",
        "La photo complète est conservée, sans recadrage.",
    )
    b.mc(
        "a1-q2",
        "Que dit le texte de la taille de cette photo ?",
        [
            ("a", "Elle est agrandie pour déborder de la page."),
            ("b", "Elle est redessinée pour remplir toute la page."),
            ("c", "Elle est simplement réduite pour tenir sur la page."),
            ("d", "Elle est tournée pour occuper deux pages."),
        ],
        "c",
        "Elle est simplement réduite pour tenir sur la page.",
    )

    add_schema(b, key)

    b.section("a3", TITLES[2])
    b.mc(
        "a3-q1",
        "Que dit le texte sur l’origine des races de chiens ?",
        [
            ("a", "Les races de chiens résultent de choix humains et ne constituent pas une classification biologique."),
            ("b", "Les races de chiens résultent d’une classification biologique, sans choix humain."),
            ("c", "Les races de chiens résultent du climat seul et constituent une classification biologique."),
            ("d", "Les races de chiens résultent de choix humains et constituent une classification biologique."),
        ],
        "a",
        "Les races de chiens résultent de choix humains et ne constituent pas une classification biologique.",
    )
    b.mc(
        "a3-q2",
        "Comment le texte décrit-il les petits chiens ?",
        [
            ("a", "petits chiens (plus de 61 cm au garrot ou plus de 25 kg)"),
            ("b", "petits chiens (46 à 61 cm au garrot ou 10 à 25 kg)"),
            ("c", "petits chiens (moins de 46 cm au garrot ou moins de 10 kg)"),
            ("d", "petits chiens (moins de 20 cm au garrot ou moins de 2 kg)"),
        ],
        "c",
        "petits chiens (moins de 46 cm au garrot ou moins de 10 kg)",
    )
    b.mc(
        "a3-q3",
        "Comment le texte décrit-il les chiens moyens ?",
        [
            ("a", "chiens moyens (46 à 61 cm ou 10 à 25 kg)"),
            ("b", "chiens moyens (moins de 46 cm ou moins de 10 kg)"),
            ("c", "chiens moyens (plus de 61 cm ou plus de 25 kg)"),
            ("d", "chiens moyens (61 à 80 cm ou 25 à 40 kg)"),
        ],
        "a",
        "chiens moyens (46 à 61 cm ou 10 à 25 kg)",
    )
    b.mc(
        "a3-q4",
        "Comment le texte décrit-il les grands chiens ?",
        [
            ("a", "grands chiens (moins de 46 cm ou moins de 10 kg)"),
            ("b", "grands chiens (46 à 61 cm ou 10 à 25 kg)"),
            ("c", "grands chiens (plus de 80 cm ou plus de 40 kg)"),
            ("d", "grands chiens (plus de 61 cm ou plus de 25 kg)"),
        ],
        "d",
        "grands chiens (plus de 61 cm ou plus de 25 kg)",
    )

    b.section("a4", TITLES[3])
    b.mc(
        "a4-q1",
        "Comment le texte décrit-il les os longs ?",
        [
            ("a", "Os longs : deux diaphyses et aucune épiphyse."),
            ("b", "Os longs : une diaphyse centrale et deux épiphyses"),
            ("c", "Os longs : un os plat sans diaphyse."),
            ("d", "Os longs : trois épiphyses sans partie centrale."),
        ],
        "b",
        "Os longs : une diaphyse centrale et deux épiphyses",
    )
    b.mc(
        "a4-q2",
        "Où le texte place-t-il les os longs, et que possèdent-ils ?",
        [
            ("a", "ils ne possèdent pas de canal médullaire et se trouvent surtout dans le crâne"),
            ("b", "ils possèdent un canal médullaire et se trouvent surtout au carpe"),
            ("c", "ils possèdent un canal médullaire et se trouvent surtout dans les membres"),
            ("d", "ils possèdent deux canaux médullaires et se trouvent surtout au tarse"),
        ],
        "c",
        "ils possèdent un canal médullaire et se trouvent surtout dans les membres",
    )
    b.mc(
        "a4-q3",
        "Comment le texte décrit-il les os plats ?",
        [
            ("a", "Os plats : surtout dans les membres, comme l’humérus."),
            ("b", "Os plats : surtout au carpe et au tarse, sans scapula."),
            ("c", "Os plats : surtout dans la cavité médullaire, comme la scapula."),
            ("d", "Os plats : surtout au crâne et aux ceintures, comme la scapula."),
        ],
        "d",
        "Os plats : surtout au crâne et aux ceintures, comme la scapula.",
    )
    b.mc(
        "a4-q4",
        "Comment le texte décrit-il les os courts ?",
        [
            ("a", "Os courts : petits os sans canal médullaire, notamment au carpe et au tarse."),
            ("b", "Os courts : petits os avec un canal médullaire, notamment au crâne."),
            ("c", "Os courts : grands os sans canal médullaire, notamment dans les membres."),
            ("d", "Os courts : petits os sans canal médullaire, notamment à la scapula."),
        ],
        "a",
        "Os courts : petits os sans canal médullaire, notamment au carpe et au tarse.",
    )

    b.section("a5", TITLES[4])
    definitions = [
        (
            "a5-q1",
            "Que dit le texte de la diaphyse ?",
            "Diaphyse : partie centrale.",
            [
                "Diaphyse : extrémité de l’os.",
                "Diaphyse : membrane externe.",
                "Diaphyse : cartilage de croissance.",
            ],
        ),
        (
            "a5-q2",
            "Que dit le texte des épiphyses ?",
            "Épiphyses : extrémités.",
            [
                "Épiphyses : partie centrale.",
                "Épiphyses : moelle jaune.",
                "Épiphyses : membrane du périoste.",
            ],
        ),
        (
            "a5-q3",
            "Que dit le texte de l’os compact ?",
            "Os compact : tissu dense.",
            [
                "Os compact : tissu poreux.",
                "Os compact : cartilage articulaire.",
                "Os compact : moelle jaune.",
            ],
        ),
        (
            "a5-q4",
            "Que dit le texte de l’os spongieux ?",
            "Os spongieux : tissu poreux.",
            [
                "Os spongieux : tissu dense.",
                "Os spongieux : membrane externe.",
                "Os spongieux : canal vide.",
            ],
        ),
        (
            "a5-q5",
            "Que dit le texte du cartilage articulaire ?",
            "Cartilage articulaire : recouvre les surfaces articulaires.",
            [
                "Cartilage articulaire : permet la croissance en longueur.",
                "Cartilage articulaire : remplit la cavité médullaire.",
                "Cartilage articulaire : recouvre le périoste seulement.",
            ],
        ),
        (
            "a5-q6",
            "Que dit le texte du cartilage de conjugaison ?",
            "Cartilage de conjugaison : permet la croissance en longueur.",
            [
                "Cartilage de conjugaison : recouvre les surfaces articulaires.",
                "Cartilage de conjugaison : contient la moelle jaune.",
                "Cartilage de conjugaison : forme le périoste.",
            ],
        ),
        (
            "a5-q7",
            "Que dit le texte de la cavité médullaire ?",
            "Cavité médullaire : espace dans la diaphyse contenant principalement la moelle jaune.",
            [
                "Cavité médullaire : espace dans l’épiphyse contenant principalement le périoste.",
                "Cavité médullaire : membrane qui recouvre tout l’os.",
                "Cavité médullaire : cartilage qui recouvre les surfaces articulaires.",
            ],
        ),
        (
            "a5-q8",
            "Que dit le texte du périoste ?",
            "Périoste : membrane qui recouvre l'os, sauf les surfaces articulaires.",
            [
                "Périoste : membrane qui recouvre seulement les surfaces articulaires.",
                "Périoste : espace dans la diaphyse contenant la moelle jaune.",
                "Périoste : tissu poreux au centre de l’os.",
            ],
        ),
        (
            "a5-q9",
            "Que comprend un os, selon le texte ?",
            "Un os comprend du tissu osseux, du périoste, du cartilage et de la moelle osseuse.",
            [
                "Un os comprend seulement du cartilage, sans périoste ni moelle.",
                "Un os comprend du tissu nerveux, du sang et aucun cartilage.",
                "Un os comprend de la moelle osseuse, sans tissu osseux.",
            ],
        ),
        (
            "a5-q10",
            "Comment le texte décrit-il l’irrigation et l’innervation de l’os ?",
            "Il est irrigué par des vaisseaux sanguins et innervé par des nerfs.",
            [
                "Il est irrigué par des nerfs et innervé par des vaisseaux sanguins.",
                "Il est sans vaisseau sanguin et sans nerf.",
                "Il est irrigué par la moelle jaune et innervé par le cartilage.",
            ],
        ),
        (
            "a5-q11",
            "Que contient notamment un os, selon le texte ?",
            "Il contient notamment de l'osséine (protéines) et des sels minéraux.",
            [
                "Il contient notamment de l’osséine (sucres) et aucun sel minéral.",
                "Il contient notamment du cartilage articulaire et aucun sel minéral.",
                "Il contient notamment de l’osséine (lipides) et des gaz.",
            ],
        ),
    ]
    for qid, prompt, correct, wrongs in definitions:
        b.mc(
            qid,
            prompt,
            [("a", correct), ("b", wrongs[0]), ("c", wrongs[1]), ("d", wrongs[2])],
            "a",
            correct,
        )

    b.section("a6", TITLES[5])
    b.mc(
        "a6-q1",
        "Quelles parties le texte place-t-il dans la tête ?",
        [
            ("a", "Tête : encolure, garrot, dos, flanc, sternum et queue."),
            ("b", "Tête : bassin, cuisse, grasset, jambe, tarse et doigts."),
            ("c", "Tête : truffe, chanfrein, front, oreille, œil, babines, joue et museau."),
            ("d", "Tête : diaphyse, épiphyse, périoste, cartilage et moelle."),
        ],
        "c",
        "Tête : truffe, chanfrein, front, oreille, œil, babines, joue et museau.",
    )
    b.mc(
        "a6-q2",
        "Quelles parties le texte place-t-il dans le tronc ?",
        [
            ("a", "Tronc : encolure (cou), gorge, garrot, dos, région lombaire (rein), croupe ou région sacrée, flanc, région costale, sternum et queue."),
            ("b", "Tronc : truffe, chanfrein, front, oreille, œil et museau."),
            ("c", "Tronc : carpe, métacarpe, doigts, tarse et métatarse."),
            ("d", "Tronc : diaphyse, épiphyse, périoste, cartilage et moelle."),
        ],
        "a",
        "Tronc : encolure (cou), gorge, garrot, dos, région lombaire (rein), croupe ou région sacrée, flanc, région costale, sternum et queue.",
    )

    b.section("a7", TITLES[6])
    b.mc(
        "a7-q1",
        "Quelles régions le texte donne-t-il au membre antérieur ?",
        [
            ("a", "Membre antérieur (thoracique) : bassin, cuisse, grasset, jambe, tarse et métatarse."),
            ("b", "Membre antérieur (thoracique) : région scapulaire (omoplate), pointe de l'épaule, région axillaire (aisselle), bras ou région brachiale, coude, pointe du coude, avant-bras ou région antibrachiale, carpe, métacarpe et doigts."),
            ("c", "Membre antérieur (thoracique) : truffe, chanfrein, front, oreille et œil."),
            ("d", "Membre antérieur (thoracique) : diaphyse, épiphyse, périoste et moelle jaune."),
        ],
        "b",
        "Membre antérieur (thoracique) : région scapulaire (omoplate), pointe de l'épaule, région axillaire (aisselle), bras ou région brachiale, coude, pointe du coude, avant-bras ou région antibrachiale, carpe, métacarpe et doigts.",
    )
    b.mc(
        "a7-q2",
        "Que comprend la main, selon le texte ?",
        [
            ("a", "La main comprend le tarse, les métatarses et les phalanges."),
            ("b", "La main comprend le bassin, la cuisse et le grasset."),
            ("c", "La main comprend la scapula, l’humérus et l’ulna."),
            ("d", "La main comprend le carpe, les métacarpes et les phalanges."),
        ],
        "d",
        "La main comprend le carpe, les métacarpes et les phalanges.",
    )
    b.mc(
        "a7-q3",
        "Quelles régions le texte donne-t-il au membre postérieur ?",
        [
            ("a", "Membre postérieur (pelvien) : région scapulaire, coude, carpe et métacarpe."),
            ("b", "Membre postérieur (pelvien) : truffe, chanfrein, front et oreille."),
            ("c", "Membre postérieur (pelvien) : bassin, cuisse, grasset (équivalent du genou), jambe, tarse ou jarret, pointe du jarret, métatarse et doigts."),
            ("d", "Membre postérieur (pelvien) : diaphyse, cartilage articulaire et périoste."),
        ],
        "c",
        "Membre postérieur (pelvien) : bassin, cuisse, grasset (équivalent du genou), jambe, tarse ou jarret, pointe du jarret, métatarse et doigts.",
    )
    b.mc(
        "a7-q4",
        "Que comprend le pied, selon le texte ?",
        [
            ("a", "Le pied comprend le carpe, les métacarpes et les phalanges."),
            ("b", "Le pied comprend le tarse, les métatarses et les phalanges."),
            ("c", "Le pied comprend le coude, le radius et l’ulna."),
            ("d", "Le pied comprend la scapula, le bras et le carpe."),
        ],
        "b",
        "Le pied comprend le tarse, les métatarses et les phalanges.",
    )

    b.section("a8", TITLES[7])
    b.mc(
        "a8-q1",
        "Que comprend la ceinture thoracique, selon le texte ?",
        [
            ("a", "La ceinture thoracique comprend l’humérus."),
            ("b", "La ceinture thoracique comprend le bassin."),
            ("c", "La ceinture thoracique comprend la scapula."),
            ("d", "La ceinture thoracique comprend le tarse."),
        ],
        "c",
        "La ceinture thoracique comprend la scapula.",
    )
    b.mc(
        "a8-q2",
        "Comment la ceinture thoracique est-elle reliée au rachis ?",
        [
            ("a", "Elle n'est pas articulée directement avec le rachis : des muscles la maintiennent."),
            ("b", "Elle est articulée directement avec le rachis, sans muscle."),
            ("c", "Elle n’est pas articulée directement avec le rachis : un os la soude."),
            ("d", "Elle est articulée directement avec le sternum seulement."),
        ],
        "a",
        "Elle n'est pas articulée directement avec le rachis : des muscles la maintiennent.",
    )
    b.mc(
        "a8-q3",
        "Que dit le texte de la clavicule ?",
        [
            ("a", "La clavicule est complète et visible hors de tout muscle."),
            ("b", "La clavicule est rudimentaire et cachée dans le muscle du jarret."),
            ("c", "La clavicule est absente et remplacée par le tarse."),
            ("d", "La clavicule est rudimentaire et cachée dans le muscle brachio-céphalique."),
        ],
        "d",
        "La clavicule est rudimentaire et cachée dans le muscle brachio-céphalique.",
    )
    b.mc(
        "a8-q4",
        "Quel os le texte attribue-t-il à l’humérus ?",
        [
            ("a", "Humérus : os de l’avant-bras."),
            ("b", "Humérus : os du bras."),
            ("c", "Humérus : os de la cuisse."),
            ("d", "Humérus : os du carpe."),
        ],
        "b",
        "Humérus : os du bras.",
    )
    b.mc(
        "a8-q5",
        "Quels os le texte attribue-t-il à l’avant-bras ?",
        [
            ("a", "Radius et ulna : os du bras."),
            ("b", "Radius et ulna : os de la jambe."),
            ("c", "Radius et ulna : os de l'avant-bras."),
            ("d", "Radius et ulna : os du crâne."),
        ],
        "c",
        "Radius et ulna : os de l'avant-bras.",
    )
    b.mc(
        "a8-q6",
        "Que forme l’olécrâne, selon le texte ?",
        [
            ("a", "L'olécrâne, qui appartient au radius, forme la pointe du jarret."),
            ("b", "L'olécrâne, qui appartient à la scapula, forme la pointe de l'épaule."),
            ("c", "L'olécrâne, qui appartient à l'humérus, forme le carpe."),
            ("d", "L'olécrâne, qui appartient à l'ulna, forme la pointe du coude."),
        ],
        "d",
        "L'olécrâne, qui appartient à l'ulna, forme la pointe du coude.",
    )
    b.mc(
        "a8-q7",
        "Que permettent la pronation et la supination, selon le texte ?",
        [
            ("a", "Les mouvements de pronation et de supination permettent la rotation de l'avant-bras."),
            ("b", "Les mouvements de pronation et de supination permettent la rotation de la queue."),
            ("c", "Les mouvements de pronation et de supination bloquent l’avant-bras."),
            ("d", "Les mouvements de pronation et de supination allongent la queue."),
        ],
        "a",
        "Les mouvements de pronation et de supination permettent la rotation de l'avant-bras.",
    )

    b.section("a9", TITLES[8])
    b.mc(
        "a9-q1",
        "Que repère le texte en vue de dessous ?",
        [
            ("a", "En vue de dessous, on repère notamment la truffe, le chanfrein, le front et l’oreille."),
            ("b", "En vue de dessous, on repère notamment le carpe, le métacarpe et les doigts."),
            ("c", "En vue de dessous, on repère notamment la mandibule, l'œsophage, la région pectorale, le sternum, l'hypochondre, l'ombilic, l'abdomen, le flanc, la région prépubienne et la région inguinale."),
            ("d", "En vue de dessous, on repère notamment la diaphyse, l’épiphyse et le périoste."),
        ],
        "c",
        "En vue de dessous, on repère notamment la mandibule, l'œsophage, la région pectorale, le sternum, l'hypochondre, l'ombilic, l'abdomen, le flanc, la région prépubienne et la région inguinale.",
    )
    b.mc(
        "a9-q2",
        "Que dit le texte du bassin par rapport à l’abdomen ?",
        [
            ("a", "Le bassin prolonge l’abdomen vers l’avant et donne attache aux membres antérieurs."),
            ("b", "Le bassin prolonge l'abdomen vers l'arrière et donne attache aux membres postérieurs."),
            ("c", "Le bassin sépare l’abdomen et ne donne aucune attache."),
            ("d", "Le bassin prolonge le crâne vers l’arrière et donne attache à la queue seule."),
        ],
        "b",
        "Le bassin prolonge l'abdomen vers l'arrière et donne attache aux membres postérieurs.",
    )
    b.mc(
        "a9-q3",
        "Quelles régions le texte distingue-t-il avec la croupe ?",
        [
            ("a", "On distingue la truffe, le chanfrein et le front."),
            ("b", "On distingue le carpe, le métacarpe et les doigts."),
            ("c", "On distingue la diaphyse, l’épiphyse et le périoste."),
            ("d", "On distingue la croupe (région sacrée), les hanches et la région fessière."),
        ],
        "d",
        "On distingue la croupe (région sacrée), les hanches et la région fessière.",
    )
    b.mc(
        "a9-q4",
        "Où se trouve la région interfessière, selon le texte ?",
        [
            ("a", "La région interfessière se trouve sous la base de la queue."),
            ("b", "La région interfessière se trouve sous la truffe."),
            ("c", "La région interfessière se trouve dans le carpe."),
            ("d", "La région interfessière se trouve au sommet du crâne."),
        ],
        "a",
        "La région interfessière se trouve sous la base de la queue.",
    )
    b.mc(
        "a9-q5",
        "Où le texte situe-t-il le périnée ?",
        [
            ("a", "Le périnée est situé entre les deux oreilles."),
            ("b", "Le périnée est situé entre le carpe et les doigts."),
            ("c", "Le périnée est situé entre l'anus et les organes génitaux."),
            ("d", "Le périnée est situé entre le front et la truffe."),
        ],
        "c",
        "Le périnée est situé entre l'anus et les organes génitaux.",
    )
    b.mc(
        "a9-q6",
        "À quoi correspond la queue, selon le texte ?",
        [
            ("a", "La queue prolonge le crâne et correspond au début du rachis."),
            ("b", "La queue prolonge le sternum et correspond au carpe."),
            ("c", "La queue remplace le bassin et ne fait pas partie du rachis."),
            ("d", "La queue prolonge le bassin et correspond à la partie terminale du rachis."),
        ],
        "d",
        "La queue prolonge le bassin et correspond à la partie terminale du rachis.",
    )
    b.mc(
        "a9-q7",
        "Comment le texte nomme-t-il un chien sans queue ?",
        [
            ("a", "Un chien avec une queue est dit anoure."),
            ("b", "Un chien sans queue est dit anoure."),
            ("c", "Un chien sans oreille est dit anoure."),
            ("d", "Un chien sans queue est dit moyen."),
        ],
        "b",
        "Un chien sans queue est dit anoure.",
    )

    b.section("a10", TITLES[9])
    vocab = [
        (
            "a10-q1",
            "Quelle équivalence le texte donne-t-il pour le carpe ?",
            "Carpe : poignet.",
            ["Carpe : genou du chien.", "Carpe : omoplate.", "Carpe : colonne vertébrale."],
        ),
        (
            "a10-q2",
            "Quelle équivalence le texte donne-t-il pour le tarse ?",
            "Tarse / jarret : région du pied postérieur.",
            [
                "Tarse / jarret : région du pied antérieur.",
                "Tarse / jarret : os du bras.",
                "Tarse / jarret : pointe du coude.",
            ],
        ),
        (
            "a10-q3",
            "Quelle équivalence le texte donne-t-il pour le grasset ?",
            "Grasset : genou du chien.",
            ["Grasset : poignet.", "Grasset : omoplate.", "Grasset : colonne vertébrale."],
        ),
        (
            "a10-q4",
            "Quelle équivalence le texte donne-t-il pour le rachis ?",
            "Rachis : colonne vertébrale.",
            ["Rachis : poignet.", "Rachis : genou du chien.", "Rachis : omoplate."],
        ),
        (
            "a10-q5",
            "Quelle équivalence le texte donne-t-il pour la scapula ?",
            "Scapula : omoplate.",
            ["Scapula : poignet.", "Scapula : genou du chien.", "Scapula : colonne vertébrale."],
        ),
        (
            "a10-q6",
            "Quelle équivalence le texte donne-t-il pour l’olécrâne ?",
            "Olécrâne : pointe du coude.",
            ["Olécrâne : pointe du jarret.", "Olécrâne : poignet.", "Olécrâne : omoplate."],
        ),
        (
            "a10-q7",
            "Où le texte place-t-il le métacarpe ?",
            "Métacarpe : entre le carpe et les doigts.",
            [
                "Métacarpe : entre le tarse et les doigts.",
                "Métacarpe : entre le crâne et le cou.",
                "Métacarpe : entre le bassin et la queue.",
            ],
        ),
        (
            "a10-q8",
            "Où le texte place-t-il le métatarse ?",
            "Métatarse : entre le tarse et les doigts.",
            [
                "Métatarse : entre le carpe et les doigts.",
                "Métatarse : entre le crâne et le cou.",
                "Métatarse : entre le bassin et la queue.",
            ],
        ),
    ]
    for qid, prompt, correct, wrongs in vocab:
        b.mc(
            qid,
            prompt,
            [("a", wrongs[0]), ("b", correct), ("c", wrongs[1]), ("d", wrongs[2])],
            "b",
            correct,
        )
    b.mc(
        "a10-q9",
        "Dans quel ordre le conseil dit-il d’apprendre ?",
        [
            ("a", "Conseil : apprends d’abord les parties de l’os long, puis les repères du schéma."),
            ("b", "Conseil : apprends d’abord les races, puis la photo entière."),
            ("c", "Conseil : laisse les repères du schéma pour la fin."),
            ("d", "Conseil : apprends d'abord les repères du schéma, puis les régions des membres et enfin les parties de l'os long."),
        ],
        "d",
        "Conseil : apprends d'abord les repères du schéma, puis les régions des membres et enfin les parties de l'os long.",
    )

    return {"sections": b.sections}


def pdf_sentences(full: str) -> list[str]:
    parts = re.split(r"(?<=[.!?]) ", full)
    return [part.strip() for part in parts if len(part.strip()) >= 40]


def verify(bank: dict, full: str, bodies: dict[str, str], key_labels: set[str]) -> None:
    errors: list[str] = []
    seen: set[str] = set()
    folded = full.casefold()
    sentences = pdf_sentences(full)
    for section in bank["sections"]:
        title = section["title"]
        if title not in bodies:
            errors.append(f"unknown title {title}")
            continue
        body = bodies[title]
        if not section["questions"]:
            errors.append(f"{section['id']} has no questions")
        for question in section["questions"]:
            qid = question["id"]
            if qid in seen:
                errors.append(f"duplicate {qid}")
            seen.add(qid)
            source = question["source"]
            if source not in full:
                errors.append(f"{qid} source not in PDF: {source[:110]}")
            if source not in body:
                errors.append(f"{qid} source not in section: {source[:90]}")
            if question["type"] != "mc":
                errors.append(f"{qid} bad type")
                continue
            ids = [choice["id"] for choice in question["choices"]]
            if ids != ["a", "b", "c", "d"]:
                errors.append(f"{qid} choices must be a b c d")
            correct = next(
                choice["text"]
                for choice in question["choices"]
                if choice["id"] == question["correctChoiceId"]
            )
            if correct not in source or correct not in full or correct not in body:
                errors.append(f"{qid} correct choice not inside source/section")
            texts = [choice["text"] for choice in question["choices"]]
            if len(set(texts)) != 4 or texts.count(correct) != 1:
                errors.append(f"{qid} does not have one unique answer")
            schema = qid.startswith("a2-d")
            for choice in question["choices"]:
                if choice["id"] == question["correctChoiceId"]:
                    continue
                text = choice["text"]
                if schema:
                    if text not in key_labels or text == correct:
                        errors.append(f"{qid} distractor is not another schema label: {text}")
                    if question.get("image") != SCHEMA:
                        errors.append(f"{qid} missing schema image")
                    continue
                if question.get("image"):
                    errors.append(f"{qid} text question has an image")
                if text in full or text.casefold() in folded:
                    errors.append(f"{qid} distractor is a PDF span: {text[:90]}")
                if text in source or correct in text or (len(text) > 12 and text in correct):
                    errors.append(f"{qid} distractor overlaps correct")
                for sentence in sentences:
                    if sentence.casefold() in text.casefold():
                        errors.append(f"{qid} distractor contains a PDF sentence")
                        break
    if errors:
        raise SystemExit("Verbatim check failed:\n" + "\n".join(errors))


def main() -> None:
    full = load_pdf()
    title = f"ANATOMIE DU CHIEN {DASH} SYNTHÈSE"
    if title not in full:
        raise SystemExit("course title missing from PDF")
    bodies = section_slices(full)
    key = schema_key(full)
    bank = build(key)
    verify(bank, full, bodies, {label for _, label in key})
    OUT.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {section["id"]: (section["title"], len(section["questions"])) for section in bank["sections"]}
    print(title)
    print(counts)
    print("total", sum(count for _, count in counts.values()))


if __name__ == "__main__":
    main()
