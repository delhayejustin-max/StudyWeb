#!/usr/bin/env python3
"""Build src/data/bank.json from the synthesis.

The correct option and the post-answer excerpt are verbatim PDF spans.
Every other option is false relative to the PDF: it must not be another
true sentence copied from the synthesis.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "public" / "Nutrition_ASV_synthese.pdf"
OUT = ROOT / "src" / "data" / "bank.json"

TITLES = [
    "1 Les bases et la digestion",
    "2 Glucides et lipides",
    "3 Protéines et particularités du chat",
    "4 Minéraux et oligoéléments",
    "5 Vitamines",
    "6 Eau et chiffres du cours",
    "7 Ton défi de révision",
]

TF_PROMPT = "D’après cette section, l’affirmation suivante est-elle exacte ?"


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
    ) -> None:
        assert self._current is not None
        self._current["questions"].append(
            {
                "id": qid,
                "type": "tf",
                "prompt": TF_PROMPT,
                "statement": statement,
                "correct": correct,
                "source": source,
            }
        )


def build() -> dict:
    b = Bank()

    b.section("s1", TITLES[0])
    b.mc(
        "s1-q1",
        "Quel intestin absorbe surtout les nutriments ?",
        [
            ("a", "Le gros intestin. L’intestin grêle absorbe notamment l’eau."),
            ("b", "L’intestin grêle. Le gros intestin absorbe notamment l’eau."),
            ("c", "L’estomac. Le gros intestin absorbe notamment les nutriments."),
            ("d", "Le caecum. L’intestin grêle forme les selles et n’absorbe pas les nutriments."),
        ],
        "b",
        "Réponse à cacher : L’intestin grêle. Le gros intestin absorbe notamment l’eau.",
    )
    b.mc(
        "s1-q2",
        "Quelle formulation le texte écrit pour un nutriment ?",
        [
            ("a", "Un nutriment est une substance ingérée qui n’est pas assimilable par l’organisme."),
            ("b", "Un nutriment est uniquement une vitamine hydrosoluble, non assimilable."),
            (
                "c",
                "Un nutriment est « une substance organique ou minérale, assimilable par l’organisme ».",
            ),
            ("d", "Un nutriment est une fibre insoluble que l’organisme n’absorbe pas."),
        ],
        "c",
        "Un nutriment est « une substance organique ou minérale, assimilable par l’organisme ».",
    )
    b.mc(
        "s1-q3",
        "Dans la colonne « Le chien », quel portrait le texte donne-t-il ?",
        [
            ("a", "Herbivore opportuniste. À l’origine : brouteur de fourrages en troupeau."),
            (
                "b",
                "Carnivore opportuniste. À l’origine : charognard et chasseur de grandes proies en groupe.",
            ),
            ("c", "Carnivore strict. À l’origine : prédateur solitaire de grandes proies, sans échec."),
            ("d", "Omnivore facultatif. À l’origine : charognard de petites graines, en solitaire."),
        ],
        "b",
        "Carnivore opportuniste. À l’origine : charognard et chasseur de grandes proies en groupe.",
    )
    b.mc(
        "s1-q4",
        "Dans la colonne « Le chat », quel portrait le texte donne-t-il ?",
        [
            (
                "a",
                "Carnivore strict. À l’origine : prédateur de petites proies, avec un taux d’échec élevé.",
            ),
            (
                "b",
                "Carnivore opportuniste. À l’origine : charognard de grandes proies, avec un taux d’échec nul.",
            ),
            ("c", "Herbivore strict. À l’origine : brouteur de petites plantes, avec un taux d’échec faible."),
            ("d", "Omnivore. À l’origine : chasseur de grandes proies en groupe, sans échec."),
        ],
        "a",
        "Carnivore strict. À l’origine : prédateur de petites proies, avec un taux d’échec élevé.",
    )
    b.mc(
        "s1-q5",
        "Quelles sont les trois étapes, dans l’ordre écrit par le texte ?",
        [
            ("a", "1. Absorber les nutriments. 2. Décomposer les aliments. 3. Stocker les graisses."),
            ("b", "1. Décomposer les aliments. 2. Absorber les nutriments. 3. Former et éliminer les déchets."),
            ("c", "1. Former et éliminer les déchets. 2. Absorber l’eau. 3. Décomposer les vitamines."),
            ("d", "1. Fabriquer les enzymes. 2. Éliminer les nutriments. 3. Décomposer les selles."),
        ],
        "b",
        "1. Décomposer les aliments. 2. Absorber les nutriments. 3. Former et éliminer les déchets.",
    )
    b.mc(
        "s1-q6",
        "Que dit le texte de l’intestin grêle et du gros intestin ?",
        [
            (
                "a",
                "L’intestin grêle récupère l’eau ; le gros intestin absorbe les nutriments et forme les enzymes.",
            ),
            (
                "b",
                "L’intestin grêle absorbe les nutriments ; le gros intestin récupère de l’eau et participe à la formation des selles.",
            ),
            ("c", "L’intestin grêle digère la cellulose ; le gros intestin absorbe les lipides."),
            ("d", "L’intestin grêle forme seul les selles ; le gros intestin décompose les aliments."),
        ],
        "b",
        "L’intestin grêle absorbe les nutriments ; le gros intestin récupère de l’eau et participe à la formation des selles.",
    )
    b.mc(
        "s1-q7",
        "Dans la colonne « Le chien », que dit le texte des repas ?",
        [
            ("a", "Repas parfois importants ; comportement plutôt glouton."),
            ("b", "Repas toujours minuscules ; comportement plutôt frugal."),
            ("c", "Une seule prise par semaine ; comportement plutôt lent."),
            ("d", "Aucune prise le jour ; comportement plutôt sélectif."),
        ],
        "a",
        "Repas parfois importants ; comportement plutôt glouton.",
    )
    b.mc(
        "s1-q8",
        "Dans la colonne « Le chat », que dit le texte des prises alimentaires ?",
        [
            ("a", "Une seule grosse prise, uniquement le matin."),
            ("b", "Aucune prise la nuit, seulement un repas du soir."),
            ("c", "Nombreuses petites prises alimentaires le jour et la nuit."),
            ("d", "Prises rares et très volumineuses, seulement en groupe."),
        ],
        "c",
        "Nombreuses petites prises alimentaires le jour et la nuit.",
    )
    b.tf(
        "s1-q9",
        "Chien et chat ont un seul estomac et un tube digestif relativement court.",
        True,
        "Chien et chat ont un seul estomac et un tube digestif relativement court.",
    )
    b.tf(
        "s1-q10",
        "Chien et chat digèrent eux-mêmes la cellulose.",
        False,
        "Ils ne digèrent pas eux-mêmes la cellulose.",
    )
    b.tf(
        "s1-q11",
        "Le support évoque une ration ad libidum.",
        True,
        "Le support évoque une ration ad libidum.",
    )

    b.section("s2", TITLES[1])
    b.mc(
        "s2-q1",
        "Quelle image le texte donne-t-il des glucides ?",
        [
            ("a", "Les glucides = le carburant."),
            ("b", "Les glucides = un isolant thermique sans rôle énergétique."),
            ("c", "Les glucides = uniquement des minéraux stockables."),
            ("d", "Les glucides = l’eau de constitution des cellules."),
        ],
        "a",
        "Les glucides = le carburant.",
    )
    b.mc(
        "s2-q2",
        "Quelle image le texte donne-t-il des lipides ?",
        [
            ("a", "Les lipides = le seul carburant immédiat, sans rôle de membrane."),
            ("b", "Les lipides = des sucres simples solubles dans l’eau."),
            ("c", "Les lipides = la réserve d’énergie, l’isolant et une partie des membranes."),
            ("d", "Les lipides = des vitamines éliminées sans stockage."),
        ],
        "c",
        "Les lipides = la réserve d’énergie, l’isolant et une partie des membranes.",
    )
    b.mc(
        "s2-q3",
        "Comment le texte définit-il le glucose ?",
        [
            ("a", "Le glucose est un polysaccharide : de longues chaînes de sucres."),
            ("b", "Le glucose est un monosaccharide : une seule unité de sucre."),
            ("c", "Le glucose est un minéral : une unité de calcium."),
            ("d", "Le glucose est un disaccharide : deux unités de lipides."),
        ],
        "b",
        "Le glucose est un monosaccharide : une seule unité de sucre.",
    )
    b.mc(
        "s2-q4",
        "Quelles réserves glucidiques le texte attribue-t-il aux végétaux et aux animaux ?",
        [
            ("a", "glycogène chez les végétaux, amidon chez les animaux"),
            ("b", "pectines chez les végétaux, agar chez les animaux"),
            ("c", "amidon chez les végétaux, glycogène chez les animaux"),
            ("d", "lactose chez les végétaux, fructose chez les animaux"),
        ],
        "c",
        "Longues chaînes de sucres : amidon chez les végétaux, glycogène chez les animaux.",
    )
    b.mc(
        "s2-q5",
        "Quels polysaccharides structuraux le texte cite-t-il ?",
        [
            ("a", "Glucose des végétaux ; fructose des exosquelettes."),
            ("b", "Cellulose des végétaux ; chitine des exosquelettes."),
            ("c", "Pectines des minéraux ; agar des vitamines."),
            ("d", "Lignine des animaux ; lactose des exosquelettes."),
        ],
        "b",
        "Cellulose des végétaux ; chitine des exosquelettes.",
    )
    b.mc(
        "s2-q6",
        "Quelles sources le texte cite-t-il pour les oméga 3 ?",
        [
            ("a", "poissons gras, certaines huiles, noix et œufs"),
            ("b", "fruits à pépins, son et algues uniquement"),
            ("c", "lait écrémé, plumes et eau sucrée"),
            ("d", "épinards secs, son de riz et agar en poudre"),
        ],
        "a",
        "Sources citées : poissons gras, certaines huiles, noix et œufs.",
    )
    b.mc(
        "s2-q7",
        "Comment le texte décrit-il un phospholipide ?",
        [
            (
                "a",
                "Le phospholipide comprend une tête apolaire hydrophobe et deux queues polaires hydrophiles.",
            ),
            (
                "b",
                "Le phospholipide comprend une tête polaire (groupement phosphate hydrophile) et deux queues apolaires (acides gras hydrophobes).",
            ),
            ("c", "Le phospholipide comprend trois têtes polaires et aucune queue."),
            ("d", "Le phospholipide comprend une tête de glucose et quatre queues de minéraux."),
        ],
        "b",
        "Le phospholipide comprend une tête polaire (groupement phosphate hydrophile) et deux queues apolaires (acides gras hydrophobes).",
    )
    b.mc(
        "s2-q8",
        "Quelles vitamines sont absorbées avec les graisses ?",
        [
            ("a", "B et C : les vitamines liposolubles."),
            ("b", "A, B, C et D : les vitamines hydrosolubles stockées."),
            ("c", "Uniquement la vitamine C, stockée avec les graisses."),
            ("d", "A, D, E et K : les vitamines liposolubles."),
        ],
        "d",
        "Réponse à cacher : A, D, E et K : les vitamines liposolubles.",
    )
    b.tf(
        "s2-q9",
        "Ce sont les matières grasses, insolubles dans l’eau.",
        True,
        "Ce sont les matières grasses, insolubles dans l’eau.",
    )
    b.tf(
        "s2-q10",
        "Les fibres ont un faible pouvoir hydrophile : elles rejettent l’eau.",
        False,
        "Les fibres ont un fort pouvoir hydrophile : elles absorbent et retiennent l’eau, favorisent la satiété et participent au volume des selles et au transit.",
    )
    b.tf(
        "s2-q11",
        "Certains acides gras sont essentiels : ils doivent être apportés par l’alimentation.",
        True,
        "Certains acides gras sont essentiels : ils doivent être apportés par l’alimentation.",
    )

    b.section("s3", TITLES[2])
    b.mc(
        "s3-q1",
        "Comment le texte présente-t-il les protéines ?",
        [
            ("a", "Les protéines sont des assemblages de sucres simples."),
            ("b", "Les protéines sont des assemblages d’acides aminés."),
            ("c", "Les protéines sont des minéraux insolubles dans l’eau."),
            ("d", "Les protéines sont des vitamines stockées dans le foie."),
        ],
        "b",
        "Les protéines sont des assemblages d’acides aminés.",
    )
    b.mc(
        "s3-q2",
        "Quel enchaînement le texte écrit, de l’aliment jusqu’aux nouvelles protéines ?",
        [
            (
                "a",
                "Acides aminés alimentaires → stockage dans le gros intestin → protéines → rejet sans absorption.",
            ),
            (
                "b",
                "Protéines alimentaires → enzymes digestives dans l’estomac et l’intestin grêle → acides aminés → absorption → fabrication de nouvelles protéines.",
            ),
            (
                "c",
                "Glucides alimentaires → enzymes dans le caecum → lipides → absorption → fabrication de taurine.",
            ),
            (
                "d",
                "Protéines alimentaires → absorption directe sans enzyme → glucose → élimination urinaire.",
            ),
        ],
        "b",
        "Protéines alimentaires → enzymes digestives dans l’estomac et l’intestin grêle → acides aminés → absorption → fabrication de nouvelles protéines.",
    )
    b.mc(
        "s3-q3",
        "Quel exemple le texte donne pour la fonction « transporter » ?",
        [
            ("a", "Hémoglobine : transport du calcium."),
            ("b", "Anticorps : transport de l’oxygène."),
            ("c", "Hémoglobine : transport de l’oxygène."),
            ("d", "Enzymes : transport des selles."),
        ],
        "c",
        "Hémoglobine : transport de l’oxygène.",
    )
    b.mc(
        "s3-q4",
        "Que dit le texte d’un acide aminé essentiel ?",
        [
            (
                "a",
                "Les acides aminés essentiels sont produits par le corps et ne doivent pas être apportés par l’alimentation.",
            ),
            (
                "b",
                "Les acides aminés essentiels ne peuvent pas être produits par le corps et doivent être apportés par l’alimentation.",
            ),
            ("c", "Les acides aminés essentiels sont des sucres fabriqués par le gros intestin."),
            ("d", "Les acides aminés essentiels sont éliminés par les urines sans être utilisés."),
        ],
        "b",
        "Les acides aminés essentiels ne peuvent pas être produits par le corps et doivent être apportés par l’alimentation.",
    )
    b.mc(
        "s3-q5",
        "Que dit le texte de la taurine chez le chat et chez le chien ?",
        [
            (
                "a",
                "La taurine est un acide aminé essentiel chez le chien et un acide aminé non essentiel chez le chat.",
            ),
            (
                "b",
                "La taurine est un acide aminé essentiel chez le chat et un acide aminé non essentiel chez le chien.",
            ),
            ("c", "La taurine est une vitamine essentielle chez les deux espèces."),
            ("d", "La taurine est un glucide non essentiel chez le chat et essentiel chez le cobaye."),
        ],
        "b",
        "La taurine est un acide aminé essentiel chez le chat et un acide aminé non essentiel chez le chien.",
    )
    b.mc(
        "s3-q6",
        "Pourquoi le pourcentage de protéines ne suffit-il pas pour juger un aliment ?",
        [
            ("a", "Il suffit de lire le pourcentage, sans regarder les acides aminés."),
            ("b", "Il faut seulement compter les fibres insolubles."),
            ("c", "Il faut remplacer les protéines par des glucides."),
            ("d", "Il faut aussi regarder les acides aminés essentiels et la digestibilité."),
        ],
        "d",
        "Réponse à cacher : Il faut aussi regarder les acides aminés essentiels et la digestibilité.",
    )
    b.mc(
        "s3-q7",
        "Quelles sources animales le texte cite-t-il ?",
        [
            ("a", "Sources animales : son, algues, pectines."),
            ("b", "Sources animales : viande, poisson, œufs, produits laitiers."),
            ("c", "Sources animales : fruits à pépins, agar, lignine."),
            ("d", "Sources animales : eau, cellulose et vitamines seules."),
        ],
        "b",
        "Sources animales : viande, poisson, œufs, produits laitiers.",
    )
    b.mc(
        "s3-q8",
        "Quelles conséquences de la carence en protéines le texte écrit-il ?",
        [
            (
                "a",
                "Conséquences : croissance réduite, perte de poids et de muscle, baisse des performances, pelage de mauvaise qualité et immunité affaiblie.",
            ),
            ("b", "Conséquences : prise de poids, pelage plus brillant et immunité renforcée."),
            ("c", "Conséquences : excès de collagène et calcification des tissus mous."),
            ("d", "Conséquences : aucun signe, la carence reste sans effet."),
        ],
        "a",
        "Conséquences : croissance réduite, perte de poids et de muscle, baisse des performances, pelage de mauvaise qualité et immunité affaiblie.",
    )
    b.tf(
        "s3-q9",
        "Beaucoup de protéines ne suffisent pas si des acides aminés nécessaires manquent.",
        True,
        "Beaucoup de protéines ne suffisent pas si des acides aminés nécessaires manquent.",
    )
    b.tf(
        "s3-q10",
        "La taurine est un acide aminé non essentiel chez le chat et essentiel chez le chien.",
        False,
        "La taurine est un acide aminé essentiel chez le chat et un acide aminé non essentiel chez le chien.",
    )
    b.tf(
        "s3-q11",
        "Le support met en avant la richesse en acides aminés essentiels et la digestibilité des protéines animales.",
        True,
        "Le support met en avant la richesse en acides aminés essentiels et la digestibilité des protéines animales.",
    )

    b.section("s4", TITLES[3])
    b.mc(
        "s4-q1",
        "Que dit le texte de l’énergie apportée par les minéraux et les oligoéléments ?",
        [
            ("a", "Ils apportent davantage d’énergie que les glucides, les lipides et les protéines."),
            ("b", "Ils n’apportent pas d’énergie comme les glucides, les lipides et les protéines."),
            ("c", "Ils remplacent les lipides comme unique carburant."),
            ("d", "Ils sont facultatifs et n’ont aucun rôle dans l’organisme."),
        ],
        "b",
        "Ils n’apportent pas d’énergie comme les glucides, les lipides et les protéines.",
    )
    b.mc(
        "s4-q2",
        "Que dit le texte du rapport calcium/phosphore ?",
        [
            ("a", "Le rapport Ca/P ne compte pas : seules les quantités importent."),
            ("b", "Le rapport Ca/P doit toujours être inférieur à 0,1."),
            ("c", "Le rapport Ca/P compte autant que les quantités."),
            ("d", "Le rapport Ca/P remplace l’apport de vitamine C."),
        ],
        "c",
        "Le rapport Ca/P compte autant que les quantités.",
    )
    b.mc(
        "s4-q3",
        "Quel rôle le texte donne-t-il à la vitamine D pour le calcium et le phosphore ?",
        [
            ("a", "La vitamine D bloque l’absorption intestinale du calcium et du phosphore."),
            ("b", "La vitamine D favorise l’élimination urinaire du fer et du zinc."),
            ("c", "La vitamine D remplace le calcium dans le squelette."),
            ("d", "La vitamine D favorise l’absorption intestinale du calcium et du phosphore."),
        ],
        "d",
        "La vitamine D favorise l’absorption intestinale du calcium et du phosphore.",
    )
    b.mc(
        "s4-q4",
        "Fer, iode, zinc : retrouve leur mot clé.",
        [
            ("a", "Fer = thyroïde ; iode = oxygène ; zinc = squelette uniquement."),
            ("b", "Fer = peau ; iode = coagulation ; zinc = oxygène."),
            ("c", "Fer = oxygène ; iode = thyroïde ; zinc = peau et immunité."),
            ("d", "Fer = collagène ; iode = glucose ; zinc = vision."),
        ],
        "c",
        "Réponse à cacher : Fer = oxygène ; iode = thyroïde ; zinc = peau et immunité.",
    )
    b.mc(
        "s4-q5",
        "Quelle association de carence le texte écrit-il pour le fer et le cuivre ?",
        [
            ("a", "Fer et cuivre → goitre isolé."),
            ("b", "Fer et cuivre → anémie."),
            ("c", "Fer et cuivre → calcification des tissus mous."),
            ("d", "Fer et cuivre → excès de collagène."),
        ],
        "b",
        "Fer et cuivre → anémie.",
    )
    b.mc(
        "s4-q6",
        "Quelle association de carence le texte écrit-il pour l’iode ?",
        [
            ("a", "Iode → goitre, hypothyroïdie, retard de croissance."),
            ("b", "Iode → anémie isolée, sans effet sur la thyroïde."),
            ("c", "Iode → troubles cutanés seuls, avec immunité renforcée."),
            ("d", "Iode → calcification des artères et vision améliorée."),
        ],
        "a",
        "Iode → goitre, hypothyroïdie, retard de croissance.",
    )
    b.mc(
        "s4-q7",
        "Quelle association de carence le texte écrit-il pour le zinc ?",
        [
            ("a", "Zinc → goitre, hypothyroïdie et anémie isolée."),
            ("b", "Zinc → excès de collagène et vision renforcée."),
            ("c", "Zinc → troubles cutanés, croissance ralentie, immunité affaiblie."),
            ("d", "Zinc → aucune carence : le texte n’en décrit pas."),
        ],
        "c",
        "Zinc → troubles cutanés, croissance ralentie, immunité affaiblie.",
    )
    b.mc(
        "s4-q8",
        "Quelle association de carence le texte écrit-il pour le sélénium ?",
        [
            ("a", "Sélénium → goitre et anémie uniquement."),
            ("b", "Sélénium → troubles de la coagulation du sang."),
            ("c", "Sélénium → excès d’oxygène dans l’hémoglobine."),
            ("d", "Sélénium → faiblesse musculaire et troubles de croissance."),
        ],
        "d",
        "Sélénium → faiblesse musculaire et troubles de croissance.",
    )
    b.tf(
        "s4-q9",
        "Ils sont indispensables, même en petites quantités.",
        True,
        "Ils sont indispensables, même en petites quantités.",
    )
    b.tf(
        "s4-q10",
        "Un déséquilibre du rapport calcium/phosphore laisse le squelette intact, en croissance comme à l’âge adulte.",
        False,
        "Un déséquilibre peut perturber le squelette en croissance et à l’âge adulte.",
    )
    b.tf(
        "s4-q11",
        "En excès, ces éléments peuvent aussi être toxiques.",
        True,
        "En excès, ces éléments peuvent aussi être toxiques.",
    )

    b.section("s5", TITLES[4])
    b.mc(
        "s5-q1",
        "Comment le texte classe-t-il les vitamines ADEK ?",
        [
            ("a", "ADEK = vitamines hydrosolubles, éliminées dès l’absorption et non stockables."),
            ("b", "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables."),
            ("c", "ADEK = minéraux qui apportent l’énergie principale."),
            ("d", "ADEK = fibres insolubles du gros intestin."),
        ],
        "b",
        "ADEK = vitamines liposolubles, absorbées avec les lipides et stockables.",
    )
    b.mc(
        "s5-q2",
        "Comment le texte classe-t-il les vitamines B et C ?",
        [
            (
                "a",
                "B et C = vitamines hydrosolubles, liées à l’eau ; les excédents sont généralement éliminés par les urines.",
            ),
            ("b", "B et C = vitamines liposolubles, stockées dans les graisses sans élimination."),
            ("c", "B et C = oligoéléments de l’hémoglobine."),
            ("d", "B et C = polysaccharides de réserve."),
        ],
        "a",
        "B et C = vitamines hydrosolubles, liées à l’eau ; les excédents sont généralement éliminés par les urines.",
    )
    b.mc(
        "s5-q3",
        "Que dit le texte du chat et du bêta-carotène ?",
        [
            ("a", "Le chat convertit le bêta-carotène en vitamine A."),
            ("b", "Le chat ne convertit pas le bêta-carotène en vitamine A."),
            ("c", "Le chat convertit le bêta-carotène en vitamine C."),
            ("d", "Le chat n’a pas besoin de vitamine A, le bêta-carotène suffit."),
        ],
        "b",
        "Le chat ne convertit pas le bêta-carotène en vitamine A.",
    )
    b.mc(
        "s5-q4",
        "Que dit le texte d’un excès de foie chez le chat, pour la vitamine A ?",
        [
            (
                "a",
                "chez le chat, de grandes quantités de foie protègent le cou et évitent tout excès.",
            ),
            (
                "b",
                "chez le chat, de grandes quantités de foie peuvent entraîner un excès, avec des troubles osseux notamment au niveau du cou.",
            ),
            ("c", "chez le chat, le foie remplace toute vitamine A sans risque osseux."),
            ("d", "chez le chat, le foie est la source de vitamine C et n’a aucun lien avec la vitamine A."),
        ],
        "b",
        "Particularité de la vitamine A : chez le chat, de grandes quantités de foie peuvent entraîner un excès, avec des troubles osseux notamment au niveau du cou.",
    )
    b.mc(
        "s5-q5",
        "Quelle formule le texte écrit après l’excès de vitamine A ?",
        [
            ("a", "« Plus » veut donc dire « mieux »."),
            ("b", "« Moins » suffit toujours, sans limite inférieure."),
            ("c", "« Plus » ne veut donc pas dire « mieux »."),
            ("d", "Un excès de vitamines est toujours bénéfique."),
        ],
        "c",
        "« Plus » ne veut donc pas dire « mieux ».",
    )
    b.mc(
        "s5-q6",
        "Où le texte situe-t-il l’absorption de la vitamine B12 ?",
        [
            ("a", "La B12 est absorbée dans l’estomac et ne participe pas à la croissance cellulaire."),
            ("b", "La B12 est absorbée dans l’iléon et participe à la croissance cellulaire."),
            ("c", "La B12 est absorbée dans le caecum et reste une vitamine liposoluble."),
            ("d", "La B12 n’est pas absorbée : le texte la dit uniquement injectable d’emblée."),
        ],
        "b",
        "La B12 est absorbée dans l’iléon et participe à la croissance cellulaire.",
    )
    b.mc(
        "s5-q7",
        "Que dit le texte du cobaye et de la vitamine C ?",
        [
            ("a", "Le cobaye synthétise la vitamine C : son alimentation ne doit pas lui en apporter."),
            ("b", "Le cobaye ne peut pas synthétiser la vitamine C : son alimentation doit lui en apporter."),
            ("c", "Le cobaye convertit le bêta-carotène en vitamine C."),
            ("d", "Le cobaye stocke la vitamine C avec les graisses et n’en reçoit pas dans l’aliment."),
        ],
        "b",
        "Le cobaye ne peut pas synthétiser la vitamine C : son alimentation doit lui en apporter.",
    )
    b.mc(
        "s5-q8",
        "Quelle particularité relie le chat à la vitamine A et le cobaye à la vitamine C ?",
        [
            (
                "a",
                "Le chat synthétise la vitamine A à partir du bêta-carotène ; le cobaye synthétise la vitamine C.",
            ),
            (
                "b",
                "Le chat doit recevoir de la vitamine C ; le cobaye a besoin de vitamine A d’origine végétale seule.",
            ),
            (
                "c",
                "Le chat a besoin de vitamine A utilisable d’origine animale ; le cobaye doit recevoir de la vitamine C dans son alimentation.",
            ),
            ("d", "Les deux synthétisent ces vitamines et n’ont rien à recevoir dans l’aliment."),
        ],
        "c",
        "Réponse à cacher : Le chat a besoin de vitamine A utilisable d’origine animale ; le cobaye doit recevoir de la vitamine C dans son alimentation.",
    )
    b.tf(
        "s5-q9",
        "Leur fonction dépend de la vitamine : elles ne sont pas interchangeables.",
        True,
        "Leur fonction dépend de la vitamine : elles ne sont pas interchangeables.",
    )
    b.tf(
        "s5-q10",
        "Le chat convertit le bêta-carotène en vitamine A.",
        False,
        "Le chat ne convertit pas le bêta-carotène en vitamine A.",
    )
    b.tf(
        "s5-q11",
        "Les excédents de vitamines B et C sont généralement stockés avec les graisses.",
        False,
        "B et C = vitamines hydrosolubles, liées à l’eau ; les excédents sont généralement éliminés par les urines.",
    )

    b.section("s6", TITLES[5])
    b.mc(
        "s6-q1",
        "Quelle part d’eau le cours indique-t-il dans le corps d’un animal adulte ?",
        [
            ("a", "Environ 30 %."),
            ("b", "Environ 45 %."),
            ("c", "Environ 70 %."),
            ("d", "Environ 90 %."),
        ],
        "c",
        "Eau dans le corps d’un animal adulte Environ 70 %.",
    )
    b.mc(
        "s6-q2",
        "Quelle valeur le cours indique-t-il pour l’eau quotidienne du chien ?",
        [
            ("a", "15 ml/kg/jour."),
            ("b", "50 ml/kg/jour."),
            ("c", "80 ml/kg/jour."),
            ("d", "120 ml/kg/jour."),
        ],
        "b",
        "Eau quotidienne du chien 50 ml/kg/jour.",
    )
    b.mc(
        "s6-q3",
        "Quelle valeur le cours indique-t-il pour l’eau quotidienne du chat ?",
        [
            ("a", "10 à 15 ml/kg/jour."),
            ("b", "25 à 35 ml/kg/jour."),
            ("c", "60 à 90 ml/kg/jour."),
            ("d", "100 ml/kg/jour."),
        ],
        "b",
        "Eau quotidienne du chat 25 à 35 ml/kg/jour.",
    )
    b.mc(
        "s6-q4",
        "Quelles concentrations en protéines de l’aliment le cours indique-t-il pour le chien et le chat ?",
        [
            ("a", "Chien : 40 à 45 % ; chat : 10 à 12 %."),
            ("b", "Chien : 5 à 8 % ; chat : 60 à 65 %."),
            ("c", "Chien : 20 à 25 % ; chat : 30 à 35 %."),
            ("d", "Chien : 90 % ; chat : 90 %."),
        ],
        "c",
        "Chien : 20 à 25 % ; chat : 30 à 35 %.",
    )
    b.mc(
        "s6-q5",
        "Que dit le support sur la base de calcul de ces pourcentages de protéines ?",
        [
            ("a", "La base de calcul est la matière grasse, et le support la fixe à 12 %."),
            ("b", "La base de calcul n’est pas précisée dans le support."),
            ("c", "La base de calcul est le poids des os, précisée dans le support."),
            ("d", "La base de calcul est l’amidon, fixé à 8 % dans le support."),
        ],
        "b",
        "La base de calcul n’est pas précisée dans le support.",
    )
    b.mc(
        "s6-q6",
        "Quelles plages de rapport calcium/phosphore le texte attribue-t-il au développement et à la révision ?",
        [
            ("a", "Le développement indique 2,8 à 3,4 ; la révision indique 0,2 à 0,3."),
            ("b", "Le développement indique 6 à 8 ; la révision indique 9 à 10."),
            ("c", "Le cours indique un rapport unique de 0,4, sans autre plage."),
            ("d", "Le développement indique 1,1 à 1,3 ; la révision indique 1,1 à 1,5."),
        ],
        "d",
        "Le développement indique 1,1 à 1,3 ; la révision indique 1,1 à 1,5.",
    )
    b.mc(
        "s6-q7",
        "Quel repère oméga 6 / oméga 3 le cours présente-t-il, et quelle comparaison humaine cite-t-il ?",
        [
            ("a", "Repère présenté : 1 pour 9 ; comparaison humaine citée : environ 2 pour 1."),
            ("b", "Repère présenté : 4 pour 1 ; comparaison humaine citée : environ 15 pour 1."),
            ("c", "Repère présenté : 12 pour 1 ; comparaison humaine citée : environ 3 pour 1."),
            ("d", "Repère présenté : 30 pour 1 ; comparaison humaine citée : environ 1 pour 2."),
        ],
        "b",
        "Repère présenté : 4 pour 1 ; comparaison humaine citée : environ 15 pour 1.",
    )
    b.mc(
        "s6-q8",
        "Quelle répartition énergétique le texte donne-t-il pour l’introduction humaine ?",
        [
            ("a", "Glucides 40 %, lipides 40 %, protéines 20 %."),
            ("b", "Glucides 80 %, lipides 10 %, protéines 10 %."),
            ("c", "Glucides 50 %, lipides 35 %, protéines 15 %."),
            ("d", "Glucides 25 %, lipides 25 %, protéines 50 %."),
        ],
        "c",
        "Glucides 50 %, lipides 35 %, protéines 15 %. À distinguer d’une ration canine ou féline.",
    )
    b.mc(
        "s6-q9",
        "Pourquoi les besoins en eau ne sont-ils pas une quantité fixe ?",
        [
            ("a", "Ils sont identiques pour tous les animaux, quel que soit l’aliment."),
            ("b", "Ils ne dépendent que de la couleur du pelage."),
            ("c", "Ils deviennent nuls pendant la lactation."),
            ("d", "Ils varient avec l’alimentation, l’activité, la température et l’état physiologique."),
        ],
        "d",
        "Réponse à cacher : Ils varient avec l’alimentation, l’activité, la température et l’état physiologique.",
    )
    b.tf(
        "s6-q10",
        "Toujours laisser de l’eau propre et fraîche à disposition de l’animal.",
        True,
        "Toujours laisser de l’eau propre et fraîche à disposition de l’animal.",
    )
    b.tf(
        "s6-q11",
        "Les aliments secs apportent davantage d’eau que les aliments frais.",
        False,
        "Les aliments frais apportent davantage d’eau que les aliments secs.",
    )
    b.tf(
        "s6-q12",
        "Le cours cite notamment les cystites et les calculs urinaires, surtout chez le chat mâle.",
        True,
        "Le cours cite notamment les cystites et les calculs urinaires, surtout chez le chat mâle.",
    )

    b.section("s7", TITLES[6])
    b.mc(
        "s7-q1",
        "Quelle est la différence entre un aliment et un nutriment ?",
        [
            ("a", "Le nutriment est mangé ; il apporte des aliments non assimilables."),
            ("b", "L’aliment est mangé ; il apporte des nutriments assimilables."),
            ("c", "L’aliment et le nutriment sont le même mot dans le cours."),
            ("d", "L’aliment n’apporte aucun nutriment."),
        ],
        "b",
        "L’aliment est mangé ; il apporte des nutriments assimilables.",
    )
    b.mc(
        "s7-q2",
        "Quel organe absorbe principalement les nutriments ?",
        [
            ("a", "Le gros intestin, qui absorbe les nutriments."),
            ("b", "L’estomac, seul organe d’absorption."),
            ("c", "L’intestin grêle."),
            ("d", "Le caecum des herbivores, cité comme organe principal."),
        ],
        "c",
        "2. L’intestin grêle.",
    )
    b.mc(
        "s7-q3",
        "Pourquoi le chat prend-il souvent plusieurs petits repas ?",
        [
            ("a", "Son comportement vient de la chasse de grandes proies, une fois par semaine."),
            ("b", "Son comportement vient de la chasse de petites proies, le jour et la nuit."),
            ("c", "Il ne prend qu’un repas, toujours au matin."),
            ("d", "Parce qu’il broute en continu comme un herbivore."),
        ],
        "b",
        "Son comportement vient de la chasse de petites proies, le jour et la nuit.",
    )
    b.mc(
        "s7-q4",
        "Quelles sont les réserves glucidiques des végétaux et des animaux ?",
        [
            ("a", "Glycogène chez les végétaux ; amidon chez les animaux."),
            ("b", "Pectines chez les végétaux ; agar chez les animaux."),
            ("c", "Lactose chez les végétaux ; fructose chez les animaux."),
            ("d", "Amidon chez les végétaux ; glycogène chez les animaux."),
        ],
        "d",
        "Amidon chez les végétaux ; glycogène chez les animaux.",
    )
    b.mc(
        "s7-q5",
        "À quoi servent les fibres ?",
        [
            ("a", "Apport d’énergie principal, isolation thermique et membranes."),
            ("b", "Rétention d’eau, satiété, volume des selles et transit."),
            ("c", "Coagulation du sang et vision nocturne."),
            ("d", "Synthèse de la vitamine C chez le cobaye."),
        ],
        "b",
        "Rétention d’eau, satiété, volume des selles et transit.",
    )
    b.mc(
        "s7-q6",
        "Quelles vitamines sont liposolubles ?",
        [
            ("a", "B et C uniquement, stockées dans les graisses."),
            ("b", "Uniquement la vitamine C."),
            ("c", "A, D, E et K."),
            ("d", "Fer, iode et zinc, cités comme vitamines."),
        ],
        "c",
        "6. A, D, E et K.",
    )
    b.mc(
        "s7-q7",
        "En quoi les protéines ressemblent-elles à un jeu de construction ?",
        [
            ("a", "Elles sont faites de sucres, collés sans digestion."),
            ("b", "Elles sont des minéraux impossibles à séparer."),
            ("c", "Elles ne sont jamais réutilisées après la digestion."),
            ("d", "Elles sont faites d’acides aminés, séparés par la digestion puis réutilisés."),
        ],
        "d",
        "Elles sont faites d’acides aminés, séparés par la digestion puis réutilisés.",
    )
    b.mc(
        "s7-q8",
        "Pourquoi ne donne-t-on pas un aliment pour chiens au chat ?",
        [
            ("a", "Les besoins sont identiques ; la taurine est essentielle au chien seulement."),
            ("b", "Le chat synthétise toute sa taurine, comme le chien."),
            ("c", "Les besoins sont différents, notamment pour la taurine essentielle au chat."),
            ("d", "L’aliment pour chiens contient trop de vitamine C pour le chat."),
        ],
        "c",
        "Les besoins sont différents, notamment pour la taurine essentielle au chat.",
    )
    b.mc(
        "s7-q9",
        "Quels deux critères comptent dans la qualité des protéines ?",
        [
            ("a", "Uniquement le pourcentage de protéines affiché."),
            ("b", "La teneur en cellulose et en eau seulement."),
            ("c", "L’absence totale d’acides aminés."),
            ("d", "Acides aminés essentiels en bonnes proportions et digestibilité."),
        ],
        "d",
        "Acides aminés essentiels en bonnes proportions et digestibilité.",
    )
    b.mc(
        "s7-q10",
        "Quel est le rôle de la vitamine D par rapport au calcium et au phosphore ?",
        [
            ("a", "Elle bloque leur absorption intestinale et fragilise le squelette."),
            ("b", "Elle favorise leur absorption intestinale et participe à la formation du squelette."),
            ("c", "Elle remplace le calcium et le phosphore."),
            ("d", "Elle n’a aucun lien avec le calcium ni le phosphore."),
        ],
        "b",
        "Elle favorise leur absorption intestinale et participe à la formation du squelette.",
    )
    b.mc(
        "s7-q11",
        "Associe fer, iode et zinc à leurs fonctions.",
        [
            ("a", "Fer : thyroïde ; iode : peau ; zinc : hémoglobine uniquement."),
            ("b", "Fer : coagulation ; iode : collagène ; zinc : glucose."),
            ("c", "Fer : hémoglobine et oxygène ; iode : thyroïde ; zinc : peau et immunité."),
            ("d", "Fer : vision ; iode : satiété ; zinc : transit."),
        ],
        "c",
        "Fer : hémoglobine et oxygène ; iode : thyroïde ; zinc : peau et immunité.",
    )
    b.mc(
        "s7-q12",
        "Quel animal doit recevoir sa vitamine C dans son alimentation ?",
        [
            ("a", "Le chaton sevré."),
            ("b", "Le chien adulte, jamais un rongeur."),
            ("c", "La vache laitière."),
            ("d", "Le cobaye."),
        ],
        "d",
        "12. Le cobaye.",
    )
    b.tf(
        "s7-q13",
        "Comprendre, retrouver de mémoire, vérifier : trois étapes utiles pour apprendre.",
        True,
        "Comprendre, retrouver de mémoire, vérifier : trois étapes utiles pour apprendre.",
    )
    b.tf(
        "s7-q14",
        "L’organe qui absorbe principalement les nutriments est le gros intestin.",
        False,
        "2. L’intestin grêle.",
    )

    return {"sections": b.sections}


def pdf_sentences(full: str) -> list[str]:
    parts = re.split(r"(?<=[.!?]) ", full)
    return [part.strip() for part in parts if len(part.strip()) >= 35]


def verify(bank: dict, full: str, bodies: dict[str, str]) -> None:
    errors: list[str] = []
    seen_ids: set[str] = set()
    folded = full.casefold()
    sentences = pdf_sentences(full)

    for section in bank["sections"]:
        title = section["title"]
        if title not in TITLES:
            errors.append(f"unknown section title {title}")
            continue
        if section["title"] != TITLES[int(section["id"][1]) - 1]:
            errors.append(f"{section['id']} title mismatch")
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
                errors.append(f"{qid} source not in PDF: {source[:90]}")
            if source not in body:
                errors.append(f"{qid} source not in section")
            if question["type"] == "mc":
                ids = [c["id"] for c in question["choices"]]
                if ids != ["a", "b", "c", "d"]:
                    errors.append(f"{qid} choices must be a b c d")
                if question["correctChoiceId"] not in ids:
                    errors.append(f"{qid} missing correct id")
                correct = next(
                    c["text"] for c in question["choices"] if c["id"] == question["correctChoiceId"]
                )
                if correct not in source:
                    errors.append(f"{qid} correct choice not inside source")
                if correct not in full:
                    errors.append(f"{qid} correct choice not in PDF")
                if correct not in body:
                    errors.append(f"{qid} correct choice not in section")
                texts = [c["text"] for c in question["choices"]]
                if len(set(texts)) != len(texts):
                    errors.append(f"{qid} duplicate choices")
                for choice in question["choices"]:
                    text = choice["text"]
                    if choice["id"] == question["correctChoiceId"]:
                        continue
                    if text in full or text.casefold() in folded:
                        errors.append(f"{qid} distractor is a PDF span: {text[:80]}")
                    if text in source or correct in text or text in correct:
                        errors.append(f"{qid} distractor overlaps the correct answer: {text[:60]}")
                    for sentence in sentences:
                        if sentence.casefold() in text.casefold():
                            errors.append(f"{qid} distractor contains a PDF sentence: {sentence[:60]}")
                            break
            elif question["type"] == "tf":
                if question["prompt"] != TF_PROMPT:
                    errors.append(f"{qid} unexpected true/false prompt")
                statement = question["statement"]
                if question["correct"]:
                    if statement not in full:
                        errors.append(f"{qid} true statement not in PDF")
                    if statement not in source:
                        errors.append(f"{qid} true statement not inside source")
                    if statement not in body:
                        errors.append(f"{qid} true statement not in section")
                else:
                    if statement in full or statement.casefold() in folded:
                        errors.append(f"{qid} false statement is actually in the PDF")
                    if statement in source:
                        errors.append(f"{qid} false statement is inside the source")
                    for sentence in sentences:
                        if sentence.casefold() in statement.casefold():
                            errors.append(f"{qid} false statement contains a PDF sentence")
                            break
            else:
                errors.append(f"{qid} unknown type")

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
