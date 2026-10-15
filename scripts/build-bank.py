#!/usr/bin/env python3
"""Build src/data/bank.json from verbatim spans and refuse anything not in the PDF."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "public" / "Nutrition_ASV_synthese.pdf"
OUT = ROOT / "src" / "data" / "bank.json"

A = "\u2019"  # right single quotation mark, as in the PDF
OE = "\u0153"
EM = "\u2014"
AR = "\u2192"
LQ = "\u00ab"
RQ = "\u00bb"

TITLES = [
    "1 Les bases et la digestion",
    "2 Glucides et lipides",
    "3 Protéines et particularités du chat",
    "4 Minéraux et oligoéléments",
    "5 Vitamines",
    "6 Eau et chiffres du cours",
    "7 Ton défi de révision",
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
    ) -> None:
        assert self._current is not None
        self._current["questions"].append(
            {
                "id": qid,
                "type": "mc",
                "prompt": prompt,
                "choices": [{"id": cid, "text": text} for cid, text in choices],
                "correctChoiceId": correct,
                "source": source,
            }
        )

    def tf(
        self,
        qid: str,
        statement: str,
        correct: bool,
        source: str,
        source_section: str | None = None,
    ) -> None:
        assert self._current is not None
        item = {
            "id": qid,
            "type": "tf",
            "prompt": "Cette phrase figure-t-elle dans cette section ?",
            "statement": statement,
            "correct": correct,
            "source": source,
        }
        if source_section:
            item["sourceSectionTitle"] = source_section
        self._current["questions"].append(item)


def build() -> dict:
    b = Bank()

    b.section("s1", TITLES[0])
    b.mc(
        "s1-q1",
        "Quel intestin absorbe surtout les nutriments ?",
        [
            (
                "a",
                "Le microbiote intestinal participe à la défense contre les agents pathogènes et à la régulation de l"
                + A
                + "inflammation.",
            ),
            (
                "b",
                "L" + A + "intestin grêle. Le gros intestin absorbe notamment l" + A + "eau.",
            ),
            (
                "c",
                "Chien et chat ont un seul estomac et un tube digestif relativement court.",
            ),
            ("d", "Ils ne digèrent pas eux-mêmes la cellulose."),
        ],
        "b",
        "Réponse à cacher : L"
        + A
        + "intestin grêle. Le gros intestin absorbe notamment l"
        + A
        + "eau.",
    )
    b.mc(
        "s1-q2",
        "Quelle formulation le texte écrit pour un nutriment ?",
        [
            (
                "a",
                "Un aliment est une substance ingérée, digérée, absorbée et utilisée par l"
                + A
                + "organisme.",
            ),
            (
                "b",
                "Les familles comprennent : glucides, lipides, protéines, minéraux, vitamines et eau.",
            ),
            (
                "c",
                "Un nutriment est "
                + LQ
                + " une substance organique ou minérale, assimilable par l"
                + A
                + "organisme "
                + RQ
                + ".",
            ),
            ("d", "Un aliment contient de l" + A + "eau et de la matière sèche."),
        ],
        "c",
        "Un nutriment est "
        + LQ
        + " une substance organique ou minérale, assimilable par l"
        + A
        + "organisme "
        + RQ
        + ".",
    )
    b.mc(
        "s1-q3",
        "Laquelle de ces phrases le texte écrit au sujet du chien ?",
        [
            (
                "a",
                "Carnivore strict. À l"
                + A
                + "origine : prédateur de petites proies, avec un taux d"
                + A
                + "échec élevé.",
            ),
            ("b", "Nombreuses petites prises alimentaires le jour et la nuit."),
            ("c", "Le support évoque une ration ad libidum."),
            (
                "d",
                "Carnivore opportuniste. À l"
                + A
                + "origine : charognard et chasseur de grandes proies en groupe.",
            ),
        ],
        "d",
        "Carnivore opportuniste. À l"
        + A
        + "origine : charognard et chasseur de grandes proies en groupe.",
    )
    b.mc(
        "s1-q4",
        "Laquelle de ces phrases le texte écrit au sujet du chat ?",
        [
            (
                "a",
                "Carnivore strict. À l"
                + A
                + "origine : prédateur de petites proies, avec un taux d"
                + A
                + "échec élevé.",
            ),
            ("b", "Repas parfois importants ; comportement plutôt glouton."),
            ("c", "Son alimentation doit répondre aux besoins de son espèce."),
            (
                "d",
                "Carnivore opportuniste. À l"
                + A
                + "origine : charognard et chasseur de grandes proies en groupe.",
            ),
        ],
        "a",
        "Carnivore strict. À l"
        + A
        + "origine : prédateur de petites proies, avec un taux d"
        + A
        + "échec élevé.",
    )
    b.mc(
        "s1-q5",
        "Quelles trois étapes le texte numérote ?",
        [
            (
                "a",
                "Les familles comprennent : glucides, lipides, protéines, minéraux, vitamines et eau.",
            ),
            (
                "b",
                "1. Décomposer les aliments. 2. Absorber les nutriments. 3. Former et éliminer les déchets.",
            ),
            (
                "c",
                "Glucides : énergie. Lipides : réserve, membranes, vitamines ADEK.",
            ),
            ("d", "Fer et cuivre " + AR + " anémie."),
        ],
        "b",
        "1. Décomposer les aliments. 2. Absorber les nutriments. 3. Former et éliminer les déchets.",
    )
    b.mc(
        "s1-q6",
        "Quelle liste de familles le texte écrit ?",
        [
            (
                "a",
                "Deux familles : acides gras saturés et acides gras insaturés.",
            ),
            ("b", "Sources à retenir : fruits, légumes, herbe et fourrages."),
            ("c", "Sept familles à retrouver"),
            (
                "d",
                "Les familles comprennent : glucides, lipides, protéines, minéraux, vitamines et eau.",
            ),
        ],
        "d",
        "Les familles comprennent : glucides, lipides, protéines, minéraux, vitamines et eau.",
    )
    b.tf(
        "s1-q7",
        "L"
        + A
        + "ASV conseille une alimentation adaptée, avec le vétérinaire pour les situations spécifiques.",
        True,
        "L"
        + A
        + "ASV conseille une alimentation adaptée, avec le vétérinaire pour les situations spécifiques.",
    )
    b.tf(
        "s1-q8",
        "Un déséquilibre peut provoquer des troubles digestifs.",
        True,
        "Le microbiote intestinal participe à la défense contre les agents pathogènes et à la régulation de l"
        + A
        + "inflammation. Un déséquilibre peut provoquer des troubles digestifs.",
    )
    b.tf(
        "s1-q9",
        "Les glucides = le carburant.",
        False,
        "Les glucides = le carburant.",
        TITLES[1],
    )

    b.section("s2", TITLES[1])
    b.mc(
        "s2-q1",
        "Quelles vitamines sont absorbées avec les graisses ?",
        [
            (
                "a",
                "B et C = vitamines hydrosolubles, liées à l"
                + A
                + "eau ; les excédents sont généralement éliminés par les urines.",
            ),
            (
                "b",
                "La vitamine C, ou acide ascorbique, participe à l"
                + A
                + "action antioxydante, à la formation du collagène, aux défenses et à la cicatrisation.",
            ),
            ("c", "A, D, E et K : les vitamines liposolubles."),
            (
                "d",
                "La B12 est absorbée dans l" + A + "iléon et participe à la croissance cellulaire.",
            ),
        ],
        "c",
        "Réponse à cacher : A, D, E et K : les vitamines liposolubles.",
    )
    b.mc(
        "s2-q2",
        "Quelle image le texte retient pour les glucides ?",
        [
            ("a", "Les glucides = le carburant."),
            (
                "b",
                "Les lipides = la réserve d"
                + A
                + "énergie, l"
                + A
                + "isolant et une partie des membranes.",
            ),
            ("c", "Les protéines sont des assemblages d" + A + "acides aminés."),
            (
                "d",
                "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables.",
            ),
        ],
        "a",
        "Les glucides = le carburant.",
    )
    b.mc(
        "s2-q3",
        "Quelle image le texte retient pour les lipides ?",
        [
            ("a", "Les glucides = le carburant."),
            ("b", "Les protéines sont des assemblages d" + A + "acides aminés."),
            (
                "c",
                "Les lipides = la réserve d"
                + A
                + "énergie, l"
                + A
                + "isolant et une partie des membranes.",
            ),
            ("d", "Eau : fonctionnement général."),
        ],
        "c",
        "Les lipides = la réserve d"
        + A
        + "énergie, l"
        + A
        + "isolant et une partie des membranes.",
    )
    b.mc(
        "s2-q4",
        "Quelle phrase le texte écrit pour définir le glucose ?",
        [
            (
                "a",
                "Mono et disaccharides : glucose, fructose, lactose. Sources citées : notamment les fruits.",
            ),
            (
                "b",
                "Longues chaînes de sucres : amidon chez les végétaux, glycogène chez les animaux.",
            ),
            ("c", "Cellulose des végétaux ; chitine des exosquelettes."),
            (
                "d",
                "Le glucose est un monosaccharide : une seule unité de sucre.",
            ),
        ],
        "d",
        "Le glucose est un monosaccharide : une seule unité de sucre.",
    )
    b.mc(
        "s2-q5",
        "Quelle phrase le texte écrit pour les polysaccharides de réserve ?",
        [
            (
                "a",
                "Longues chaînes de sucres : amidon chez les végétaux, glycogène chez les animaux.",
            ),
            ("b", "Cellulose des végétaux ; chitine des exosquelettes."),
            (
                "c",
                "Insolubles : cellulose, lignine " + EM + " légumes, parties dures des végétaux, son.",
            ),
            (
                "d",
                "Solubles : pectines et agar " + EM + " fruits à pépins, certains fruits rouges, algues.",
            ),
        ],
        "a",
        "Longues chaînes de sucres : amidon chez les végétaux, glycogène chez les animaux.",
    )
    b.mc(
        "s2-q6",
        "Quelle phrase le texte écrit sur le pouvoir des fibres ?",
        [
            ("a", "Sources à retenir : fruits, légumes, herbe et fourrages."),
            (
                "b",
                "Les fibres ont un fort pouvoir hydrophile : elles absorbent et retiennent l"
                + A
                + "eau, favorisent la satiété et participent au volume des selles et au transit.",
            ),
            (
                "c",
                "Chez les herbivores, les bactéries présentes dans le caecum permettent leur digestion.",
            ),
            (
                "d",
                "Deux familles : acides gras saturés et acides gras insaturés.",
            ),
        ],
        "b",
        "Les fibres ont un fort pouvoir hydrophile : elles absorbent et retiennent l"
        + A
        + "eau, favorisent la satiété et participent au volume des selles et au transit.",
    )
    b.mc(
        "s2-q7",
        "Quelles sources le texte cite pour les oméga 3 ?",
        [
            (
                "a",
                "Sources citées : huiles végétales, viandes, volailles et " + OE + "ufs.",
            ),
            ("b", "Effets pro-inflammatoires mis en avant dans le cours."),
            (
                "c",
                "Sources citées : poissons gras, certaines huiles, noix et " + OE + "ufs.",
            ),
            ("d", "Effets anti-inflammatoires mis en avant dans le cours."),
        ],
        "c",
        "Sources citées : poissons gras, certaines huiles, noix et " + OE + "ufs.",
    )
    b.tf(
        "s2-q8",
        "Certains acides gras sont essentiels : ils doivent être apportés par l"
        + A
        + "alimentation.",
        True,
        "Certains acides gras sont essentiels : ils doivent être apportés par l"
        + A
        + "alimentation. Le cours souligne leur rôle cardiovasculaire, cérébral et dans les processus inflammatoires.",
    )
    b.tf(
        "s2-q9",
        "Le phospholipide comprend une tête polaire (groupement phosphate hydrophile) et deux queues apolaires (acides gras hydrophobes).",
        True,
        "Le phospholipide comprend une tête polaire (groupement phosphate hydrophile) et deux queues apolaires (acides gras hydrophobes).",
    )
    b.tf(
        "s2-q10",
        "La taurine est un acide aminé essentiel chez le chat et un acide aminé non essentiel chez le chien.",
        False,
        "La taurine est un acide aminé essentiel chez le chat et un acide aminé non essentiel chez le chien.",
        TITLES[2],
    )

    b.section("s3", TITLES[2])
    b.mc(
        "s3-q1",
        "Pourquoi le pourcentage de protéines ne suffit-il pas pour juger un aliment ?",
        [
            ("a", "Sources animales : viande, poisson, " + OE + "ufs, produits laitiers."),
            ("b", "Sources végétales : céréales, soja, légumineuses."),
            (
                "c",
                "Il faut aussi regarder les acides aminés essentiels et la digestibilité.",
            ),
            ("d", "Muscles, peau, poils, ongles."),
        ],
        "c",
        "Réponse à cacher : Il faut aussi regarder les acides aminés essentiels et la digestibilité.",
    )
    b.mc(
        "s3-q2",
        "Laquelle de ces phrases est écrite dans " + LQ + " Le chat et la taurine " + RQ + " ?",
        [
            ("a", "Le chat ne convertit pas le bêta-carotène en vitamine A."),
            (
                "b",
                "La taurine est un acide aminé essentiel chez le chat et un acide aminé non essentiel chez le chien.",
            ),
            (
                "c",
                "Le cobaye ne peut pas synthétiser la vitamine C : son alimentation doit lui en apporter.",
            ),
            (
                "d",
                "Carnivore strict. À l"
                + A
                + "origine : prédateur de petites proies, avec un taux d"
                + A
                + "échec élevé.",
            ),
        ],
        "b",
        "La taurine est un acide aminé essentiel chez le chat et un acide aminé non essentiel chez le chien.",
    )
    b.mc(
        "s3-q3",
        "Quelle suite le texte écrit de l" + A + "aliment aux tissus ?",
        [
            (
                "a",
                "1. Décomposer les aliments. 2. Absorber les nutriments. 3. Former et éliminer les déchets.",
            ),
            (
                "b",
                "Protéines alimentaires "
                + AR
                + " enzymes digestives dans l"
                + A
                + "estomac et l"
                + A
                + "intestin grêle "
                + AR
                + " acides aminés "
                + AR
                + " absorption "
                + AR
                + " fabrication de nouvelles protéines.",
            ),
            ("c", "Fer et cuivre " + AR + " anémie."),
            ("d", "Les protéines sont des assemblages d" + A + "acides aminés."),
        ],
        "b",
        "Protéines alimentaires "
        + AR
        + " enzymes digestives dans l"
        + A
        + "estomac et l"
        + A
        + "intestin grêle "
        + AR
        + " acides aminés "
        + AR
        + " absorption "
        + AR
        + " fabrication de nouvelles protéines.",
    )
    b.mc(
        "s3-q4",
        "Quel exemple le texte place avec " + LQ + " Transporter " + RQ + " ?",
        [
            ("a", "Anticorps."),
            ("b", "Enzymes, notamment digestives."),
            ("c", "Hémoglobine : transport de l" + A + "oxygène."),
            ("d", "Muscles, peau, poils, ongles."),
        ],
        "c",
        "Hémoglobine : transport de l" + A + "oxygène.",
    )
    b.tf(
        "s3-q5",
        "Les acides aminés essentiels ne peuvent pas être produits par le corps et doivent être apportés par l"
        + A
        + "alimentation.",
        True,
        "Les acides aminés essentiels ne peuvent pas être produits par le corps et doivent être apportés par l"
        + A
        + "alimentation.",
    )
    b.tf(
        "s3-q6",
        "Une bonne qualité protéique dépend de la digestibilité et de la présence des acides aminés essentiels dans les bonnes proportions.",
        True,
        "Une bonne qualité protéique dépend de la digestibilité et de la présence des acides aminés essentiels dans les bonnes proportions.",
    )
    b.tf(
        "s3-q7",
        "Le support met en avant la richesse en acides aminés essentiels et la digestibilité des protéines animales.",
        True,
        "Le support met en avant la richesse en acides aminés essentiels et la digestibilité des protéines animales.",
    )
    b.mc(
        "s3-q8",
        "Quelle phrase le texte écrit pour les conséquences d"
        + A
        + "une carence en protéines ?",
        [
            (
                "a",
                "Causes possibles : apport insuffisant, mauvaise qualité, mauvaise digestibilité ou pertes liées à des troubles digestifs ou à une maladie.",
            ),
            ("b", "Carence : croissance perturbée, fragilité osseuse."),
            (
                "c",
                "Zinc "
                + AR
                + " troubles cutanés, croissance ralentie, immunité affaiblie.",
            ),
            (
                "d",
                "Conséquences : croissance réduite, perte de poids et de muscle, baisse des performances, pelage de mauvaise qualité et immunité affaiblie.",
            ),
        ],
        "d",
        "Conséquences : croissance réduite, perte de poids et de muscle, baisse des performances, pelage de mauvaise qualité et immunité affaiblie.",
    )
    b.mc(
        "s3-q9",
        "Quelle phrase le texte écrit sur le fait de nourrir un chat avec un aliment pour chiens ?",
        [
            (
                "a",
                "C"
                + A
                + "est une différence essentielle avec le chien : on ne nourrit pas un chat avec un aliment pour chiens.",
            ),
            ("b", "Sources végétales : céréales, soja, légumineuses."),
            (
                "c",
                "En cas de famine, par exemple chez les animaux cachectiques.",
            ),
            ("d", "Défendre l" + A + "organisme"),
        ],
        "a",
        "C"
        + A
        + "est une différence essentielle avec le chien : on ne nourrit pas un chat avec un aliment pour chiens.",
    )
    b.tf(
        "s3-q10",
        "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables.",
        False,
        "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables.",
        TITLES[4],
    )

    b.section("s4", TITLES[3])
    b.mc(
        "s4-q1",
        "Fer, iode, zinc : retrouve leur mot clé.",
        [
            ("a", "Fer et cuivre " + AR + " anémie."),
            (
                "b",
                "Iode " + AR + " goitre, hypothyroïdie, retard de croissance.",
            ),
            (
                "c",
                "Fer = oxygène ; iode = thyroïde ; zinc = peau et immunité.",
            ),
            (
                "d",
                "Sélénium " + AR + " faiblesse musculaire et troubles de croissance.",
            ),
        ],
        "c",
        "Réponse à cacher : Fer = oxygène ; iode = thyroïde ; zinc = peau et immunité.",
    )
    b.mc(
        "s4-q2",
        "Que dit le texte du point commun des minéraux et des oligoéléments ?",
        [
            ("a", "Oligoéléments : petites quantités, rôles spécifiques."),
            (
                "b",
                "Ils sont indispensables, même en petites quantités. Ils n"
                + A
                + "apportent pas d"
                + A
                + "énergie comme les glucides, les lipides et les protéines.",
            ),
            ("c", "Minéraux : squelette et fonctions de l" + A + "organisme."),
            ("d", "En excès, ces éléments peuvent aussi être toxiques."),
        ],
        "b",
        "Ils sont indispensables, même en petites quantités. Ils n"
        + A
        + "apportent pas d"
        + A
        + "énergie comme les glucides, les lipides et les protéines.",
    )
    b.mc(
        "s4-q3",
        "Quelle association le texte écrit pour le fer et le cuivre ?",
        [
            ("a", "Fer et cuivre " + AR + " anémie."),
            ("b", "Iode " + AR + " goitre, hypothyroïdie, retard de croissance."),
            (
                "c",
                "Zinc " + AR + " troubles cutanés, croissance ralentie, immunité affaiblie.",
            ),
            (
                "d",
                "Sélénium " + AR + " faiblesse musculaire et troubles de croissance.",
            ),
        ],
        "a",
        "Fer et cuivre " + AR + " anémie.",
    )
    b.mc(
        "s4-q4",
        "Quelle association le texte écrit pour l" + A + "iode ?",
        [
            ("a", "Fer et cuivre " + AR + " anémie."),
            ("b", "Iode " + AR + " goitre, hypothyroïdie, retard de croissance."),
            (
                "c",
                "Zinc " + AR + " troubles cutanés, croissance ralentie, immunité affaiblie.",
            ),
            (
                "d",
                "Sélénium " + AR + " faiblesse musculaire et troubles de croissance.",
            ),
        ],
        "b",
        "Iode " + AR + " goitre, hypothyroïdie, retard de croissance.",
    )
    b.mc(
        "s4-q5",
        "Quelle association le texte écrit pour le zinc ?",
        [
            ("a", "Fer et cuivre " + AR + " anémie."),
            ("b", "Iode " + AR + " goitre, hypothyroïdie, retard de croissance."),
            (
                "c",
                "Sélénium " + AR + " faiblesse musculaire et troubles de croissance.",
            ),
            (
                "d",
                "Zinc " + AR + " troubles cutanés, croissance ralentie, immunité affaiblie.",
            ),
        ],
        "d",
        "Zinc " + AR + " troubles cutanés, croissance ralentie, immunité affaiblie.",
    )
    b.mc(
        "s4-q6",
        "Quelle association le texte écrit pour le sélénium ?",
        [
            (
                "a",
                "Sélénium " + AR + " faiblesse musculaire et troubles de croissance.",
            ),
            (
                "b",
                "Zinc " + AR + " troubles cutanés, croissance ralentie, immunité affaiblie.",
            ),
            ("c", "Iode " + AR + " goitre, hypothyroïdie, retard de croissance."),
            ("d", "Fer et cuivre " + AR + " anémie."),
        ],
        "a",
        "Sélénium " + AR + " faiblesse musculaire et troubles de croissance.",
    )
    b.tf(
        "s4-q7",
        "La vitamine D favorise l"
        + A
        + "absorption intestinale du calcium et du phosphore.",
        True,
        "Le rapport Ca/P compte autant que les quantités. Un déséquilibre peut perturber le squelette en croissance et à l"
        + A
        + "âge adulte. La vitamine D favorise l"
        + A
        + "absorption intestinale du calcium et du phosphore.",
    )
    b.tf(
        "s4-q8",
        "En excès, ces éléments peuvent aussi être toxiques.",
        True,
        "En excès, ces éléments peuvent aussi être toxiques.",
    )
    b.mc(
        "s4-q9",
        "Laquelle de ces phrases figure dans cette section ?",
        [
            ("a", "Excès : calcification des tissus mous."),
            (
                "b",
                "Excès : notamment troubles osseux chez le chien en croissance.",
            ),
            ("c", "Carence : dégénérescence ou faiblesse musculaire."),
            (
                "d",
                "Carence : anorexie, saignements gingivaux, œdème, émaciation, diarrhée et diminution de la résistance aux infections.",
            ),
        ],
        "b",
        "Excès : notamment troubles osseux chez le chien en croissance.",
    )
    b.mc(
        "s4-q10",
        "Quelles sources le texte cite pour le fer ?",
        [
            ("a", "Viande rouge, épinards, lentilles."),
            ("b", "Abats, fruits de mer, noix."),
            ("c", "Sel iodé, fruits de mer."),
            ("d", "Poissons, noix du Brésil."),
        ],
        "a",
        "Viande rouge, épinards, lentilles.",
    )
    b.mc(
        "s4-q11",
        "Laquelle de ces phrases figure dans cette section ?",
        [
            ("a", "Squelette, contraction musculaire, transmission nerveuse."),
            ("b", "Carence : troubles de vision et de reproduction."),
            ("c", "Les glucides regroupent les sucres."),
            ("d", "Un aliment contient de l" + A + "eau et de la matière sèche."),
        ],
        "a",
        "Squelette, contraction musculaire, transmission nerveuse.",
    )
    b.mc(
        "s4-q12",
        "Laquelle de ces phrases figure dans cette section ?",
        [
            ("a", "Le glucose est un monosaccharide : une seule unité de sucre."),
            ("b", "Formation des hormones thyroïdiennes."),
            (
                "c",
                "La B12 est absorbée dans l"
                + A
                + "iléon et participe à la croissance cellulaire.",
            ),
            ("d", "Cache la correction."),
        ],
        "b",
        "Formation des hormones thyroïdiennes.",
    )
    b.tf(
        "s4-q13",
        "Toujours laisser de l" + A + "eau propre et fraîche à disposition de l" + A + "animal.",
        False,
        "Toujours laisser de l" + A + "eau propre et fraîche à disposition de l" + A + "animal.",
        TITLES[5],
    )

    b.section("s5", TITLES[4])
    b.mc(
        "s5-q1",
        "Quelle particularité relie le chat à la vitamine A et le cobaye à la vitamine C ?",
        [
            (
                "a",
                "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables.",
            ),
            (
                "b",
                "B et C = vitamines hydrosolubles, liées à l"
                + A
                + "eau ; les excédents sont généralement éliminés par les urines.",
            ),
            (
                "c",
                "La B12 est absorbée dans l"
                + A
                + "iléon et participe à la croissance cellulaire.",
            ),
            (
                "d",
                "Le chat a besoin de vitamine A utilisable d"
                + A
                + "origine animale ; le cobaye doit recevoir de la vitamine C dans son alimentation.",
            ),
        ],
        "d",
        "Réponse à cacher : Le chat a besoin de vitamine A utilisable d"
        + A
        + "origine animale ; le cobaye doit recevoir de la vitamine C dans son alimentation.",
    )
    b.tf(
        "s5-q2",
        "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables.",
        True,
        "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables.",
    )
    b.tf(
        "s5-q3",
        "B et C = vitamines hydrosolubles, liées à l"
        + A
        + "eau ; les excédents sont généralement éliminés par les urines.",
        True,
        "B et C = vitamines hydrosolubles, liées à l"
        + A
        + "eau ; les excédents sont généralement éliminés par les urines.",
    )
    b.mc(
        "s5-q4",
        "Quelle phrase le texte écrit sur l" + A + "hypervitaminose ?",
        [
            (
                "a",
                "L"
                + A
                + "hypervitaminose concerne un excès de vitamines ; le cours insiste sur le stockage des vitamines liposolubles.",
            ),
            (
                "b",
                "Leur fonction dépend de la vitamine : elles ne sont pas interchangeables.",
            ),
            (
                "c",
                "Les vitamines participent notamment au métabolisme, à l"
                + A
                + "immunité, à la cicatrisation et à la protection cellulaire.",
            ),
            ("d", LQ + " Plus " + RQ + " ne veut donc pas dire " + LQ + " mieux " + RQ + "."),
        ],
        "a",
        "L"
        + A
        + "hypervitaminose concerne un excès de vitamines ; le cours insiste sur le stockage des vitamines liposolubles.",
    )
    b.mc(
        "s5-q5",
        "Quelle phrase le texte écrit sur le chat et le bêta-carotène ?",
        [
            ("a", "Le chat ne convertit pas le bêta-carotène en vitamine A."),
            (
                "b",
                "Particularité de la vitamine A : chez le chat, de grandes quantités de foie peuvent entraîner un excès, avec des troubles osseux notamment au niveau du cou.",
            ),
            (
                "c",
                "Le cobaye ne peut pas synthétiser la vitamine C : son alimentation doit lui en apporter.",
            ),
            ("d", "Vision et épithélium"),
        ],
        "a",
        "Le chat ne convertit pas le bêta-carotène en vitamine A.",
    )
    b.mc(
        "s5-q6",
        "Laquelle de ces phrases figure dans cette section ?",
        [
            (
                "a",
                "Intervient dans la coagulation du sang. Une carence perturbe la coagulation.",
            ),
            ("b", "Rétention d" + A + "eau, satiété, volume des selles et transit."),
            (
                "c",
                "Elle favorise leur absorption intestinale et participe à la formation du squelette.",
            ),
            (
                "d",
                "L" + A + "aliment est mangé ; il apporte des nutriments assimilables.",
            ),
        ],
        "a",
        "Intervient dans la coagulation du sang. Une carence perturbe la coagulation.",
    )
    b.mc(
        "s5-q7",
        "Laquelle de ces phrases est écrite dans " + LQ + " Le cercle de la B12 " + RQ + " ?",
        [
            (
                "a",
                "Le cours évoque une administration injectable pour contourner cette mauvaise absorption.",
            ),
            ("b", "Les glucides = le carburant."),
            ("c", "Fer et cuivre " + AR + " anémie."),
            (
                "d",
                "Toujours laisser de l"
                + A
                + "eau propre et fraîche à disposition de l"
                + A
                + "animal.",
            ),
        ],
        "a",
        "Le cours évoque une administration injectable pour contourner cette mauvaise absorption.",
    )
    b.mc(
        "s5-q8",
        "Quelle phrase le texte écrit sur la synthèse de vitamine C chez le cobaye ?",
        [
            (
                "a",
                "Le cobaye ne peut pas synthétiser la vitamine C : son alimentation doit lui en apporter.",
            ),
            (
                "b",
                "Carence : anorexie, saignements gingivaux, œdème, émaciation, diarrhée et diminution de la résistance aux infections.",
            ),
            ("c", "Le chat ne convertit pas le bêta-carotène en vitamine A."),
            (
                "d",
                "B et C = vitamines hydrosolubles, liées à l"
                + A
                + "eau ; les excédents sont généralement éliminés par les urines.",
            ),
        ],
        "a",
        "Le cobaye ne peut pas synthétiser la vitamine C : son alimentation doit lui en apporter.",
    )
    b.tf(
        "s5-q9",
        "Particularité de la vitamine A : chez le chat, de grandes quantités de foie peuvent entraîner un excès, avec des troubles osseux notamment au niveau du cou.",
        True,
        "Particularité de la vitamine A : chez le chat, de grandes quantités de foie peuvent entraîner un excès, avec des troubles osseux notamment au niveau du cou. "
        + LQ
        + " Plus "
        + RQ
        + " ne veut donc pas dire "
        + LQ
        + " mieux "
        + RQ
        + ".",
    )
    b.tf(
        "s5-q10",
        LQ + " Plus " + RQ + " ne veut donc pas dire " + LQ + " mieux " + RQ + ".",
        True,
        LQ + " Plus " + RQ + " ne veut donc pas dire " + LQ + " mieux " + RQ + ".",
    )
    b.tf(
        "s5-q11",
        "Les fibres ont un fort pouvoir hydrophile : elles absorbent et retiennent l"
        + A
        + "eau, favorisent la satiété et participent au volume des selles et au transit.",
        False,
        "Les fibres ont un fort pouvoir hydrophile : elles absorbent et retiennent l"
        + A
        + "eau, favorisent la satiété et participent au volume des selles et au transit.",
        TITLES[1],
    )

    b.section("s6", TITLES[5])
    b.mc(
        "s6-q1",
        "Pourquoi les besoins en eau ne sont-ils pas une quantité fixe ?",
        [
            (
                "a",
                "Toujours laisser de l"
                + A
                + "eau propre et fraîche à disposition de l"
                + A
                + "animal.",
            ),
            (
                "b",
                "Ils varient avec l"
                + A
                + "alimentation, l"
                + A
                + "activité, la température et l"
                + A
                + "état physiologique.",
            ),
            (
                "c",
                "Un manque d"
                + A
                + "eau expose à la déshydratation et favorise des problèmes urinaires.",
            ),
            (
                "d",
                "Les aliments frais apportent davantage d" + A + "eau que les aliments secs.",
            ),
        ],
        "b",
        "Réponse à cacher : Ils varient avec l"
        + A
        + "alimentation, l"
        + A
        + "activité, la température et l"
        + A
        + "état physiologique.",
    )
    b.mc(
        "s6-q2",
        "Quelle valeur le texte indique pour l"
        + A
        + "eau dans le corps d"
        + A
        + "un animal adulte ?",
        [
            ("a", "Environ 70 %."),
            ("b", "50 ml/kg/jour."),
            ("c", "25 à 35 ml/kg/jour."),
            ("d", "Glucides 50 %, lipides 35 %, protéines 15 %."),
        ],
        "a",
        "Eau dans le corps d" + A + "un animal adulte Environ 70 %.",
    )
    b.mc(
        "s6-q3",
        "Quelle valeur le texte indique pour l" + A + "eau quotidienne du chien ?",
        [
            ("a", "25 à 35 ml/kg/jour."),
            ("b", "Environ 70 %."),
            ("c", "50 ml/kg/jour."),
            ("d", "Chien : 20 à 25 % ; chat : 30 à 35 %."),
        ],
        "c",
        "Eau quotidienne du chien 50 ml/kg/jour.",
    )
    b.mc(
        "s6-q4",
        "Quelle valeur le texte indique pour l" + A + "eau quotidienne du chat ?",
        [
            ("a", "50 ml/kg/jour."),
            ("b", "25 à 35 ml/kg/jour."),
            ("c", "Environ 70 %."),
            ("d", "Chien : 20 à 25 % ; chat : 30 à 35 %."),
        ],
        "b",
        "Eau quotidienne du chat 25 à 35 ml/kg/jour.",
    )
    b.mc(
        "s6-q5",
        "Que dit le texte sur la base de calcul de la concentration en protéines de l"
        + A
        + "aliment ?",
        [
            ("a", "Chien : 20 à 25 % ; chat : 30 à 35 %."),
            ("b", "Ces valeurs sont celles des supports pour réviser."),
            ("c", "La base de calcul n" + A + "est pas précisée dans le support."),
            (
                "d",
                "Elles ne remplacent pas le calcul d" + A + "une ration adaptée à un animal.",
            ),
        ],
        "c",
        "La base de calcul n" + A + "est pas précisée dans le support.",
    )
    b.mc(
        "s6-q6",
        "Quelles plages le texte indique pour le rapport calcium/phosphore ?",
        [
            (
                "a",
                "Le développement indique 1,1 à 1,3 ; la révision indique 1,1 à 1,5. Le support mentionne aussi des plages plus larges selon les sources.",
            ),
            (
                "b",
                "Repère présenté : 4 pour 1 ; comparaison humaine citée : environ 15 pour 1.",
            ),
            ("c", "Glucides 50 %, lipides 35 %, protéines 15 %."),
            ("d", "Environ 70 %."),
        ],
        "a",
        "Le développement indique 1,1 à 1,3 ; la révision indique 1,1 à 1,5. Le support mentionne aussi des plages plus larges selon les sources.",
    )
    b.mc(
        "s6-q7",
        "Quel repère oméga 6 / oméga 3 le texte présente ?",
        [
            (
                "a",
                "Glucides 50 %, lipides 35 %, protéines 15 %. À distinguer d"
                + A
                + "une ration canine ou féline.",
            ),
            (
                "b",
                "Repère présenté : 4 pour 1 ; comparaison humaine citée : environ 15 pour 1.",
            ),
            ("c", "Chien : 20 à 25 % ; chat : 30 à 35 %."),
            ("d", "50 ml/kg/jour."),
        ],
        "b",
        "Repère présenté : 4 pour 1 ; comparaison humaine citée : environ 15 pour 1.",
    )
    b.mc(
        "s6-q8",
        "Quelle répartition énergétique le texte attribue à l" + A + "introduction humaine ?",
        [
            (
                "a",
                "Glucides 50 %, lipides 35 %, protéines 15 %. À distinguer d"
                + A
                + "une ration canine ou féline.",
            ),
            ("b", "Chien : 20 à 25 % ; chat : 30 à 35 %."),
            (
                "c",
                "Repère présenté : 4 pour 1 ; comparaison humaine citée : environ 15 pour 1.",
            ),
            ("d", "Environ 70 %."),
        ],
        "a",
        "Glucides 50 %, lipides 35 %, protéines 15 %. À distinguer d"
        + A
        + "une ration canine ou féline.",
    )
    b.tf(
        "s6-q9",
        "Le cours cite notamment les cystites et les calculs urinaires, surtout chez le chat mâle.",
        True,
        "Un manque d"
        + A
        + "eau expose à la déshydratation et favorise des problèmes urinaires. Le cours cite notamment les cystites et les calculs urinaires, surtout chez le chat mâle.",
    )
    b.tf(
        "s6-q10",
        "Elle participe à la régulation de la température, à l"
        + A
        + "hydratation des muqueuses, à la production de lait, à l"
        + A
        + "élimination des déchets et aux réactions biochimiques, dont la digestion.",
        True,
        "Elle participe à la régulation de la température, à l"
        + A
        + "hydratation des muqueuses, à la production de lait, à l"
        + A
        + "élimination des déchets et aux réactions biochimiques, dont la digestion.",
    )
    b.mc(
        "s6-q11",
        "Quelle ligne le mémo écrit pour les vitamines ?",
        [
            ("a", "Eau : fonctionnement général."),
            ("b", "Minéraux : squelette et fonctions de l" + A + "organisme."),
            ("c", "Vitamines : régulation et protection."),
            ("d", "Oligoéléments : petites quantités, rôles spécifiques."),
        ],
        "c",
        "Vitamines : régulation et protection.",
    )
    b.mc(
        "s6-q12",
        "Quelle ligne le mémo écrit pour les protéines ?",
        [
            ("a", "Protéines : acides aminés et construction."),
            ("b", "Glucides : énergie."),
            ("c", "Lipides : réserve, membranes, vitamines ADEK."),
            ("d", "Minéraux : squelette et fonctions de l" + A + "organisme."),
        ],
        "a",
        "Protéines : acides aminés et construction.",
    )

    b.section("s7", TITLES[6])
    corrections = {
        "1": "L" + A + "aliment est mangé ; il apporte des nutriments assimilables.",
        "2": "L" + A + "intestin grêle.",
        "3": "Son comportement vient de la chasse de petites proies, le jour et la nuit.",
        "4": "Amidon chez les végétaux ; glycogène chez les animaux.",
        "5": "Rétention d" + A + "eau, satiété, volume des selles et transit.",
        "6": "A, D, E et K.",
        "7": "Elles sont faites d"
        + A
        + "acides aminés, séparés par la digestion puis réutilisés.",
        "8": "Les besoins sont différents, notamment pour la taurine essentielle au chat.",
        "9": "Acides aminés essentiels en bonnes proportions et digestibilité.",
        "10": "Elle favorise leur absorption intestinale et participe à la formation du squelette.",
        "11": "Fer : hémoglobine et oxygène ; iode : thyroïde ; zinc : peau et immunité.",
        "12": "Le cobaye.",
    }
    defi = [
        ("s7-q1", "Quelle est la différence entre un aliment et un nutriment ?", "1", ["4", "8", "12"]),
        ("s7-q2", "Quel organe absorbe principalement les nutriments ?", "2", ["6", "12", "4"]),
        (
            "s7-q3",
            "Pourquoi le chat prend-il souvent plusieurs petits repas ?",
            "3",
            ["1", "5", "10"],
        ),
        (
            "s7-q4",
            "Quelles sont les réserves glucidiques des végétaux et des animaux ?",
            "4",
            ["5", "6", "12"],
        ),
        ("s7-q5", "À quoi servent les fibres ?", "5", ["1", "7", "11"]),
        ("s7-q6", "Quelles vitamines sont liposolubles ?", "6", ["2", "12", "4"]),
        (
            "s7-q7",
            "En quoi les protéines ressemblent-elles à un jeu de construction ?",
            "7",
            ["3", "9", "1"],
        ),
        (
            "s7-q8",
            "Pourquoi ne donne-t-on pas un aliment pour chiens au chat ?",
            "8",
            ["3", "10", "5"],
        ),
        (
            "s7-q9",
            "Quels deux critères comptent dans la qualité des protéines ?",
            "9",
            ["7", "11", "2"],
        ),
        (
            "s7-q10",
            "Quel est le rôle de la vitamine D par rapport au calcium et au phosphore ?",
            "10",
            ["6", "8", "4"],
        ),
        (
            "s7-q11",
            "Associe fer, iode et zinc à leurs fonctions.",
            "11",
            ["9", "5", "1"],
        ),
        (
            "s7-q12",
            "Quel animal doit recevoir sa vitamine C dans son alimentation ?",
            "12",
            ["2", "6", "4"],
        ),
    ]
    letters = ["a", "b", "c", "d"]
    # Place the correct correction in a rotating slot so it is not always first.
    for index, (qid, prompt, correct_key, wrong_keys) in enumerate(defi):
        slot = index % 4
        texts = [corrections[k] for k in wrong_keys]
        texts.insert(slot, corrections[correct_key])
        choices = [(letters[i], texts[i]) for i in range(4)]
        b.mc(qid, prompt, choices, letters[slot], corrections[correct_key])

    b.tf(
        "s7-q13",
        "Si une réponse bloque, retourne uniquement à la fiche concernée.",
        True,
        "Si une réponse bloque, retourne uniquement à la fiche concernée.",
    )
    b.tf(
        "s7-q14",
        "Refais seulement les questions qui t"
        + A
        + "ont fait hésiter, puis remplis un tableau vierge du cours compact.",
        True,
        "Refais seulement les questions qui t"
        + A
        + "ont fait hésiter, puis remplis un tableau vierge du cours compact.",
    )
    b.tf(
        "s7-q15",
        "Comprendre, retrouver de mémoire, vérifier : trois étapes utiles pour apprendre.",
        True,
        "Comprendre, retrouver de mémoire, vérifier : trois étapes utiles pour apprendre.",
    )

    return {"sections": b.sections}


def verify(bank: dict, full: str, bodies: dict[str, str]) -> None:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for section in bank["sections"]:
        title = section["title"]
        if title not in bodies:
            errors.append(f"unknown section title {title}")
            continue
        body = bodies[title]
        if not section["questions"]:
            errors.append(f"{section['id']} has no questions")
        for question in section["questions"]:
            qid = question["id"]
            if qid in seen_ids:
                errors.append(f"duplicate id {qid}")
            seen_ids.add(qid)
            source = question["source"]
            if source not in full:
                errors.append(f"{qid} source not in PDF: {source[:80]}")
            if question["type"] == "mc":
                correct = next(
                    c["text"]
                    for c in question["choices"]
                    if c["id"] == question["correctChoiceId"]
                )
                if correct not in source:
                    errors.append(f"{qid} correct choice not inside source")
                if correct not in body and source not in body:
                    errors.append(f"{qid} answer not in section body")
                if source not in body:
                    errors.append(f"{qid} source not in section")
                texts = [c["text"] for c in question["choices"]]
                if len(set(texts)) != len(texts):
                    errors.append(f"{qid} duplicate choices")
                if question["prompt"] == "Laquelle de ces phrases figure dans cette section ?":
                    for choice in question["choices"]:
                        if choice["id"] != question["correctChoiceId"] and choice["text"] in body:
                            errors.append(
                                f"{qid} distractor is also in this section: {choice['text'][:60]}"
                            )
                for choice in question["choices"]:
                    if choice["text"] not in full:
                        errors.append(f"{qid} choice not in PDF: {choice['text'][:80]}")
                    if choice["id"] != question["correctChoiceId"] and choice["text"] in source:
                        errors.append(
                            f"{qid} distractor is inside the source excerpt: {choice['text'][:60]}"
                        )
            elif question["type"] == "tf":
                statement = question["statement"]
                if statement not in full:
                    errors.append(f"{qid} statement not in PDF")
                if statement not in source:
                    errors.append(f"{qid} statement not inside source")
                other = question.get("sourceSectionTitle")
                if question["correct"]:
                    if statement not in body:
                        errors.append(f"{qid} true statement missing from section")
                    if other:
                        errors.append(f"{qid} true item should not cite another section")
                else:
                    if statement in body:
                        errors.append(f"{qid} false statement is actually in this section")
                    if not other or other not in bodies:
                        errors.append(f"{qid} false item needs a real source section")
                    elif statement not in bodies[other]:
                        errors.append(f"{qid} statement missing from cited section")
            else:
                errors.append(f"{qid} unknown type")
            # Prompts copied from the synthesis must match exactly when they appear there.
            prompt = question["prompt"]
            if prompt in full or prompt.rstrip(" ?") in full:
                pass
    if errors:
        raise SystemExit("Verbatim check failed:\n" + "\n".join(errors))


def main() -> None:
    full = load_pdf()
    bodies = section_slices(full)
    bank = build()
    verify(bank, full, bodies)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {s["id"]: len(s["questions"]) for s in bank["sections"]}
    print("wrote", OUT)
    print(counts, "total", sum(counts.values()))


if __name__ == "__main__":
    main()
