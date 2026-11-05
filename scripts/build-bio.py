#!/usr/bin/env python3
"""Build src/data/bio.json from verbatim spans of Les caractéristiques du vivant.

The correct option and the excerpt are PDF spans. Other options are false
relative to this PDF and must not be another true sentence from it.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "public" / "Les_caracteristiques_du_vivant.pdf"
OUT = ROOT / "src" / "data" / "bio.json"

B = "\uf0b7"
A = "'"  # ASCII apostrophe, as in most of this PDF
C = "\u2019"  # curly apostrophe, as in a few sentences

TITLES = [
    "Les caractéristiques du vivant",
    "Il y a différent système",
    "Cellule animale",
    "Fonction des organites",
    "Cellule végétale",
    "Transport membranaire",
]

# The plant-cell figure has no text layer. That section stays empty.
EMPTY_OK = {"Cellule végétale"}

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

    def tf(self, qid: str, statement: str, correct: bool, source: str) -> None:
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
    bullet = f" {B} "

    b.section("b1", TITLES[0])
    b.mc(
        "b1-q1",
        "Que dit le texte de la cytologie ?",
        [
            ("a", "Cytologie : étude des organes entiers."),
            ("b", "Cytologie : étude des cellules"),
            ("c", "Cytologie : étude des systèmes digestifs."),
            ("d", "Cytologie : étude des atomes isolés."),
        ],
        "b",
        "Cytologie : étude des cellules",
    )
    b.mc(
        "b1-q2",
        "Quelle définition le texte donne-t-il d’un tissu ?",
        [
            ("a", "Un tissu : ensemble de cellules qui ont la même fonction"),
            ("b", "Un tissu : une seule cellule isolée, sans fonction."),
            ("c", "Un tissu : ensemble d’organes aux fonctions opposées."),
            ("d", "Un tissu : ensemble de molécules d’azote seulement."),
        ],
        "a",
        "Un tissu : ensemble de cellules qui ont la même fonction",
    )
    b.mc(
        "b1-q3",
        "Quelle définition le texte donne-t-il d’un organe ?",
        [
            ("a", "Un organe : une cellule unique, sans tissu autour."),
            ("b", "Un organe : ensemble de système sans limite."),
            ("c", "Un organe : ensemble de différent tissu organiser et limiter"),
            ("d", "Un organe : uniquement un atome de carbone."),
        ],
        "c",
        "Un organe : ensemble de différent tissu organiser et limiter",
    )
    b.mc(
        "b1-q4",
        "Quelle définition le texte donne-t-il d’un système ?",
        [
            ("a", "Un système : ensemble d'organe qui ont la même grande fonction"),
            ("b", "Un système : une seule molécule sans fonction."),
            ("c", "Un système : ensemble de cellules toutes de fonctions différentes."),
            ("d", "Un système : un atome isolé, hors de tout organe."),
        ],
        "a",
        "Un système : ensemble d'organe qui ont la même grande fonction",
    )
    b.mc(
        "b1-q5",
        "Quelle définition le texte donne-t-il d’un organisme ?",
        [
            ("a", "Un organisme : une cellule seule, sans aucun système."),
            ("b", "Un organisme : ensemble de système judicieusement organiser"),
            ("c", "Un organisme : seulement un tissu nerveux."),
            ("d", "Un organisme : un minéral qui ne forme pas de système."),
        ],
        "b",
        "Un organisme : ensemble de système judicieusement organiser",
    )
    b.mc(
        "b1-q6",
        "Quels éléments le texte cite-t-il comme composition essentielle des êtres vivants ?",
        [
            ("a", "fer, iode, calcium, sodium, potassium, chlore"),
            ("b", "hélium, néon, argon, xénon, radon, krypton"),
            ("c", "azote, carbone, hydrogène, oxygène, phosphore, soufre"),
            ("d", "or, argent, cuivre, plomb, étain, mercure"),
        ],
        "c",
        "Les être vivant sont composer essentiellement de ses éléments suivent : azote, carbone, hydrogène, oxygène, phosphore, soufre",
    )
    families = f"Matier grasse{bullet}Glucide{bullet}Protéine{bullet}Acide nucléique"
    b.mc(
        "b1-q7",
        "Quelles 4 familles de molécules le texte écrit-il ?",
        [
            ("a", f"Eau{bullet}Sel{bullet}Fer{bullet}Vitamine"),
            ("b", families),
            ("c", f"Os{bullet}Sang{bullet}Nerf{bullet}Muscle"),
            ("d", f"Azote{bullet}Soufre{bullet}Or{bullet}Plomb"),
        ],
        "b",
        f"Il y a 4 familles de molécules{bullet}{families}",
    )
    domains = (
        f"Bactérie{bullet}Archées{bullet}Eucaryote{bullet}Regne végétale"
        f"{bullet}Regne animale{bullet}Reigne des champignon"
    )
    b.mc(
        "b1-q8",
        "Quelle liste le texte place sous « Il y a 3 domaines et règne du vivant » ?",
        [
            ("a", f"Virus{bullet}Prion{bullet}Minéral{bullet}Gaz{bullet}Métal{bullet}Roche"),
            ("b", f"Poisson{bullet}Oiseau{bullet}Insecte{bullet}Ver{bullet}Méduse{bullet}Éponge"),
            ("c", domains),
            ("d", f"Foie{bullet}Cœur{bullet}Poumon{bullet}Rein{bullet}Peau{bullet}Os"),
        ],
        "c",
        f"Il y a 3 domaines et règne du vivant{bullet}{domains}",
    )
    tissues = (
        f"Tissu nerveux{bullet}Tissu osseux{bullet}Tissu musculaire{bullet}Tissu conjonctif"
        f"{bullet}Tissu sanguin{bullet}Tissu cartilagineux{bullet}Tissu épithélial"
    )
    b.mc(
        "b1-q9",
        "Quels tissus le texte énumère-t-il chez un être vivant ?",
        [
            ("a", f"Tissu hépatique{bullet}Tissu rénal{bullet}Tissu pulmonaire"),
            ("b", tissues),
            ("c", f"Tissu minéral{bullet}Tissu gazeux{bullet}Tissu métallique"),
            ("d", f"Tissu viral{bullet}Tissu fossile{bullet}Tissu vide"),
        ],
        "b",
        f"Il y a plusieurs tissus chez un être vivant{bullet}{tissues}",
    )
    b.mc(
        "b1-q10",
        "Que dit le texte de la matière et des molécules ?",
        [
            (
                "a",
                "La matière est constituée d’atomes liens entre eux et forme ders molécules ces molécules vont s’organiser et former l’unité structurale tous les être vivant",
            ),
            ("b", "La matière est vide d’atomes et ne forme aucune molécule."),
            ("c", "La matière est faite seulement de cellules déjà organisées, sans atome."),
            ("d", "La matière refuse les molécules et reste en atomes séparés."),
        ],
        "a",
        "La matière est constituée d’atomes liens entre eux et forme ders molécules ces molécules vont s’organiser et former l’unité structurale tous les être vivant",
    )
    b.tf(
        "b1-q11",
        "Elles sont constituées d'une ou plusieurs cellules",
        True,
        "Elles sont constituées d'une ou plusieurs cellules",
    )
    b.tf(
        "b1-q12",
        "Un tissu est une seule molécule, sans cellule et sans fonction.",
        False,
        "Un tissu : ensemble de cellules qui ont la même fonction",
    )
    b.tf(
        "b1-q13",
        "L'ensemble des systèmes= un être vivant",
        True,
        "L'ensemble des systèmes= un être vivant",
    )

    b.section("b2", TITLES[1])
    systems = (
        f"Systèmes digestifs{bullet}Reproducteur{bullet}Nerveux{bullet}Cardiovasculaire"
        f"{bullet}Locomoteur{bullet}Endocrinien{bullet}Urinaire{bullet}Respiratoire"
        f"{bullet}Lymphatique{bullet}Immunitaire"
    )
    b.mc(
        "b2-q1",
        "Quels systèmes le texte énumère-t-il ?",
        [
            ("a", f"Solaire{bullet}Lunaire{bullet}Minéral{bullet}Gazeux"),
            ("b", systems),
            ("c", f"Hépatique seul{bullet}Cutané seul{bullet}Osseux seul"),
            ("d", f"Optique{bullet}Auditif{bullet}Olfactif{bullet}Gustatif"),
        ],
        "b",
        f"Il y a différent système{bullet}{systems}",
    )
    b.mc(
        "b2-q2",
        "Le texte écrit-il un système digestif dans cette liste ?",
        [
            ("a", "Non : la liste commence par un système minéral."),
            ("b", "Systèmes digestifs"),
            ("c", "Non : le texte ne cite que le système solaire."),
            ("d", "Non : la liste ne contient que des tissus osseux."),
        ],
        "b",
        f"Il y a différent système{bullet}Systèmes digestifs",
    )
    b.tf(
        "b2-q3",
        "Il y a différent système",
        True,
        "Il y a différent système",
    )
    b.tf(
        "b2-q4",
        "Le texte ne cite aucun système respiratoire ni immunitaire.",
        False,
        f"Respiratoire{bullet}Lymphatique{bullet}Immunitaire",
    )

    b.section("b3", TITLES[2])
    b.mc(
        "b3-q1",
        "Que place le texte au numéro 1 de la cellule animale ?",
        [
            ("a", "1.mitochondrie"),
            ("b", "1.noyaux"),
            ("c", "1.centriole"),
            ("d", "1.vacuole"),
        ],
        "b",
        "1.noyaux",
    )
    b.mc(
        "b3-q2",
        "Que place le texte au repère 1’ ?",
        [
            ("a", "1’. glucose"),
            ("b", "1’. lipide"),
            ("c", "1’. ADN"),
            ("d", "1’. ATP"),
        ],
        "c",
        "1’. ADN",
    )
    b.mc(
        "b3-q3",
        "Quel numéro le texte donne-t-il à l’appareil de Golgi ?",
        [
            ("a", "3.appareil de Golgi"),
            ("b", "9.appareil de Golgi"),
            ("c", "14.appareil de Golgi"),
            ("d", "6.appareil de Golgi"),
        ],
        "d",
        "6.appareil de Golgi",
    )
    b.mc(
        "b3-q4",
        "Quel numéro le texte donne-t-il à la mitochondrie ?",
        [
            ("a", "9.mitochondrie"),
            ("b", "2.mitochondrie"),
            ("c", "13.mitochondrie"),
            ("d", "5.mitochondrie"),
        ],
        "a",
        "9.mitochondrie",
    )
    b.mc(
        "b3-q5",
        "Que place le texte au numéro 5 ?",
        [
            ("a", "5.REL"),
            ("b", "5.noyaux"),
            ("c", "5.RER"),
            ("d", "5.centriole"),
        ],
        "c",
        "5.RER",
    )
    b.mc(
        "b3-q9",
        "Que place le texte au numéro 8 ?",
        [
            ("a", "8.RER"),
            ("b", "8.REL"),
            ("c", "8.noyaux"),
            ("d", "8.vacuole"),
        ],
        "b",
        "8.REL",
    )
    b.mc(
        "b3-q6",
        "Que place le texte au numéro 14 ?",
        [
            ("a", "14.noyaux"),
            ("b", "14.ribosome"),
            ("c", "14.vacuole centrale"),
            ("d", "14.membrane cytoplasmique"),
        ],
        "d",
        "14.membrane cytoplasmique",
    )
    b.tf(
        "b3-q7",
        "13.centriole",
        True,
        "13.centriole",
    )
    b.tf(
        "b3-q8",
        "Le texte place une vacuole au numéro 11 de la cellule animale.",
        False,
        "11.cytoplasme",
    )

    b.section("b4", TITLES[3])
    b.mc(
        "b4-q1",
        "Quelle fonction le texte donne-t-il au RE rugueux ?",
        [
            ("a", "Fonction RE rugueux : détruit l’ADN dans le noyau."),
            ("b", "Fonction RE rugueux : stoker les protéines fabriquées par les ribosomes"),
            ("c", "Fonction RE rugueux : produit l’ATP de la respiration."),
            ("d", "Fonction RE rugueux : fabrique la paroi de cellulose."),
        ],
        "b",
        "Fonction RE rugueux : stoker les protéines fabriquées par les ribosomes",
    )
    b.mc(
        "b4-q2",
        "Quelle fonction le texte donne-t-il au RE lisse ?",
        [
            ("a", "Fonction RE lisse : synthétise les lipides pour ensuite pénétrer dans des vésicules"),
            ("b", "Fonction RE lisse : stocke l’ADN hors de la cellule."),
            ("c", "Fonction RE lisse : brise les protéines en eau pure."),
            ("d", "Fonction RE lisse : bloque tout passage de lipides."),
        ],
        "a",
        "Fonction RE lisse : synthétise les lipides pour ensuite pénétrer dans des vésicules",
    )
    b.mc(
        "b4-q3",
        "Quelle fonction le texte donne-t-il au ribosome ?",
        [
            ("a", "Fonction ribosome : synthèse des lipides sur le RE lisse."),
            ("b", "Fonction ribosome : respiration cellulaire et production d’ATP."),
            ("c", "Fonction ribosome : synthèse des protéines sur le RE rugueux"),
            ("d", "Fonction ribosome : destruction des vésicules."),
        ],
        "c",
        "Fonction ribosome : synthèse des protéines sur le RE rugueux",
    )
    b.mc(
        "b4-q4",
        "Quelle fonction le texte donne-t-il à l’appareil de Golgi ?",
        [
            (
                "a",
                "Fonction appareille de Golgi : transformations des protéines provenant du RER et apparait comme des organites de stockage et distribution des protéines",
            ),
            ("b", "Fonction appareille de Golgi : synthèse de l’ADN dans les mitochondries."),
            ("c", "Fonction appareille de Golgi : destruction de tous les lipides."),
            ("d", "Fonction appareille de Golgi : aucun stockage et aucune distribution."),
        ],
        "a",
        "Fonction appareille de Golgi : transformations des protéines provenant du RER et apparait comme des organites de stockage et distribution des protéines",
    )
    b.mc(
        "b4-q5",
        "Quelle fonction le texte donne-t-il aux lysosomes ?",
        [
            ("a", "Fonction des lysosomes : stockent les lipides sans les modifier."),
            ("b", "Fonction des lysosomes : assurent la respiration et produisent l’ATP."),
            ("c", "Fonction des lysosomes : fabriquent la membrane nucléaire."),
            ("d", "Fonction des lysosomes : brise les macromolécules à savoir les protéines puis sont dégrader en acide animer"),
        ],
        "d",
        "Fonction des lysosomes : brise les macromolécules à savoir les protéines puis sont dégrader en acide animer",
    )
    b.mc(
        "b4-q6",
        "Quelle fonction le texte donne-t-il aux mitochondries ?",
        [
            ("a", "Fonction des mitochondries : les mitochondries assurent la respiration cellulaire et produit de l'énergie sous forme d'adénosine triphosphate"),
            ("b", "Fonction des mitochondries : elles stockent les protéines des ribosomes sans énergie."),
            ("c", "Fonction des mitochondries : elles synthétisent les lipides des vésicules."),
            ("d", "Fonction des mitochondries : elles n’ont aucun rôle énergétique."),
        ],
        "a",
        "Fonction des mitochondries : les mitochondries assurent la respiration cellulaire et produit de l'énergie sous forme d'adénosine triphosphate",
    )
    b.tf(
        "b4-q7",
        "Le RE lisse stocke les protéines fabriquées par les ribosomes.",
        False,
        "Fonction RE lisse : synthétise les lipides pour ensuite pénétrer dans des vésicules",
    )
    b.tf(
        "b4-q8",
        "Le texte dit que les mitochondries ne produisent pas d’énergie.",
        False,
        "Fonction des mitochondries : les mitochondries assurent la respiration cellulaire et produit de l'énergie sous forme d'adénosine triphosphate",
    )

    b.section("b5", TITLES[4])

    b.section("b6", TITLES[5])
    b.mc(
        "b6-q1",
        "Comment le texte décrit-il la diffusion simple au début du transport ?",
        [
            (
                "a",
                "Diffusion simple : les molécules remontent le gradient en dépensant de l’ATP.",
            ),
            (
                "b",
                "Diffusion simple : diffusent librement au travers de la membrane d'une région à forte concentration vers une région faible concentration en la même molécule",
            ),
            ("c", "Diffusion simple : l’eau seule traverse, jamais les autres molécules."),
            ("d", "Diffusion simple : le passage exige une protéine et de l’ATP."),
        ],
        "b",
        "Diffusion simple : diffusent librement au travers de la membrane d'une région à forte concentration vers une région faible concentration en la même molécule",
    )
    b.mc(
        "b6-q2",
        "Que dit le texte de l’énergie du transport passif ?",
        [
            ("a", "Le transport passif dépense toujours de l’ATP."),
            (
                "b",
                "Le transport passif est un mécanisme de transport membranaire qui permet le passage de molécules ou d'ions à travers la membrane cellulaire sans aucune dépense d'énergie (sans ATP).",
            ),
            ("c", "Le transport passif est impossible sans une pompe à ATP."),
            ("d", "Le transport passif ne concerne ni les molécules ni les ions."),
        ],
        "b",
        "Le transport passif est un mécanisme de transport membranaire qui permet le passage de molécules ou d'ions à travers la membrane cellulaire sans aucune dépense d'énergie (sans ATP).",
    )
    b.mc(
        "b6-q3",
        "Dans quel sens le texte dit-il que le transport passif se fait ?",
        [
            ("a", "Il remonte le gradient, de la zone la moins concentrée vers la plus concentrée."),
            ("b", "Il s’arrête avant tout déplacement de substance."),
            (
                "c",
                "Il se fait spontanément dans le sens du gradient de concentration (ou gradient électrochimique), c'est-à-dire d'une zone où la substance est la plus concentrée vers une zone où elle l'est moins, jusqu'à l'équilibre.",
            ),
            ("d", "Il ne suit aucun gradient et consomme de l’ATP."),
        ],
        "c",
        "Il se fait spontanément dans le sens du gradient de concentration (ou gradient électrochimique), c'est-à-dire d'une zone où la substance est la plus concentrée vers une zone où elle l'est moins, jusqu'à l'équilibre.",
    )
    b.mc(
        "b6-q4",
        "Quel principe le texte donne-t-il à la diffusion simple (ou libre) ?",
        [
            ("a", "Principe : Les molécules traversent directement la bicouche lipidique de la membrane."),
            ("b", "Principe : Les molécules restent bloquées hors de la bicouche."),
            ("c", "Principe : Seuls les ions chargés traversent la bicouche sans protéine."),
            ("d", "Principe : La bicouche lipidique interdit tout passage."),
        ],
        "a",
        "Principe : Les molécules traversent directement la bicouche lipidique de la membrane.",
    )
    b.mc(
        "b6-q5",
        "Quelles molécules le texte associe-t-il à la diffusion simple ?",
        [
            (
                "a",
                "Molécules concernées : grosses molécules chargées, comme les protéines et l’ADN.",
            ),
            (
                "b",
                "Molécules concernées : Petites molécules non chargées et non polaires (comme l'oxygène O₂ , le dioxyde de carbone CO₂ ) ou molécules lipophiles.",
            ),
            ("c", "Molécules concernées : uniquement l’eau, jamais l’oxygène."),
            ("d", "Molécules concernées : seulement les ions, jamais le dioxyde de carbone."),
        ],
        "b",
        "Molécules concernées : Petites molécules non chargées et non polaires (comme l'oxygène O₂ , le dioxyde de carbone CO₂ ) ou molécules lipophiles.",
    )
    b.mc(
        "b6-q6",
        "Quel principe le texte donne-t-il à la diffusion facilitée ?",
        [
            ("a", "Principe : Le passage se fait sans protéine et avec une forte dépense d’ATP."),
            ("b", "Principe : Le passage se fait contre le gradient grâce à une pompe."),
            ("c", "Principe : Le passage se fait avec l'aide de protéines membranaires spécialisées qui n'utilisent pas d'énergie."),
            ("d", "Principe : Le passage est impossible pour le glucose."),
        ],
        "c",
        "Principe : Le passage se fait avec l'aide de protéines membranaires spécialisées qui n'utilisent pas d'énergie.",
    )
    b.mc(
        "b6-q7",
        "Que dit le texte des canaux ioniques ou porines ?",
        [
            ("a", "Les canaux ioniques ou porines : ferment la membrane et bloquent tous les ions."),
            ("b", "Les canaux ioniques ou porines : forment des pores hydrophiles laissant passer rapidement des ions spécifiques."),
            ("c", "Les canaux ioniques ou porines : synthétisent l’ATP dans la mitochondrie."),
            ("d", "Les canaux ioniques ou porines : ne laissent passer que des lipides neutres."),
        ],
        "b",
        "Les canaux ioniques ou porines : forment des pores hydrophiles laissant passer rapidement des ions spécifiques.",
    )
    b.mc(
        "b6-q8",
        "Que dit le texte des transporteurs (uniports) ?",
        [
            ("a", "Les transporteurs (uniports) : changent de conformation pour faire traverser des molécules polaires ou plus grosses (comme le glucose) dans le sens de leur gradient"),
            ("b", "Les transporteurs (uniports) : dépensent de l’ATP pour remonter le gradient du glucose."),
            ("c", "Les transporteurs (uniports) : ne changent jamais de forme."),
            ("d", "Les transporteurs (uniports) : ne laissent passer que l’ADN."),
        ],
        "a",
        "Les transporteurs (uniports) : changent de conformation pour faire traverser des molécules polaires ou plus grosses (comme le glucose) dans le sens de leur gradient",
    )
    b.mc(
        "b6-q9",
        "Comment le texte définit-il l’osmose ?",
        [
            ("a", "Principe : C'est un cas particulier de diffusion qui concerne spécifiquement le mouvement de l'eau (H₂ O) à travers une membrane semi-perméable."),
            ("b", "Principe : C’est le mouvement des protéines à travers une membrane sans eau."),
            ("c", "Principe : C’est un transport qui dépense de l’ATP pour l’ADN."),
            ("d", "Principe : C’est le passage des ions par des porines, sans eau."),
        ],
        "a",
        "Principe : C'est un cas particulier de diffusion qui concerne spécifiquement le mouvement de l'eau (H₂ O) à travers une membrane semi-perméable.",
    )
    b.mc(
        "b6-q10",
        "Dans quel sens le texte dit-il que l’eau se déplace lors de l’osmose ?",
        [
            ("a", "De l’hypertonique vers l’hypotonique, pour augmenter l’écart."),
            ("b", "Elle ne se déplace pas : les deux milieux restent isolés."),
            ("c", "Du milieu sans soluté vers un milieu sans membrane."),
            ("d", "Direction : L'eau se déplace d'une zone faiblement concentrée en solutés (milieu hypotonique) vers une zone fortement concentrée en solutés (milieu hypertonique) pour équilibrer les concentrations."),
        ],
        "d",
        "Direction : L'eau se déplace d'une zone faiblement concentrée en solutés (milieu hypotonique) vers une zone fortement concentrée en solutés (milieu hypertonique) pour équilibrer les concentrations.",
    )
    b.tf(
        "b6-q11",
        "La diffusion facilitée dépense de l’ATP et se fait sans protéine membranaire.",
        False,
        "Principe : Le passage se fait avec l'aide de protéines membranaires spécialisées qui n'utilisent pas d'énergie.",
    )
    b.tf(
        "b6-q12",
        "Lors de l’osmose, l’eau va du milieu hypertonique vers le milieu hypotonique.",
        False,
        "Direction : L'eau se déplace d'une zone faiblement concentrée en solutés (milieu hypotonique) vers une zone fortement concentrée en solutés (milieu hypertonique) pour équilibrer les concentrations.",
    )

    return {"sections": b.sections}


def pdf_sentences(full: str) -> list[str]:
    parts = re.split(r"(?<=[.!?]) ", full)
    return [part.strip() for part in parts if len(part.strip()) >= 40]


def verify(bank: dict, full: str, bodies: dict[str, str]) -> None:
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
        if not section["questions"] and title not in EMPTY_OK:
            errors.append(f"{section['id']} has no questions")
        for question in section["questions"]:
            qid = question["id"]
            if qid in seen:
                errors.append(f"duplicate {qid}")
            seen.add(qid)
            source = question["source"]
            if source not in full:
                errors.append(f"{qid} source not in PDF: {source[:90]}")
            if source not in body:
                errors.append(f"{qid} source not in section: {source[:70]}")
            if question["type"] == "mc":
                ids = [c["id"] for c in question["choices"]]
                if ids != ["a", "b", "c", "d"]:
                    errors.append(f"{qid} choices must be a b c d")
                correct = next(c["text"] for c in question["choices"] if c["id"] == question["correctChoiceId"])
                if correct not in source or correct not in full or correct not in body:
                    errors.append(f"{qid} correct choice not inside source/section")
                texts = [c["text"] for c in question["choices"]]
                if len(set(texts)) != 4:
                    errors.append(f"{qid} duplicate choices")
                for choice in question["choices"]:
                    if choice["id"] == question["correctChoiceId"]:
                        continue
                    text = choice["text"]
                    if text in full or text.casefold() in folded:
                        errors.append(f"{qid} distractor is a PDF span: {text[:70]}")
                    if text in source or correct in text or (len(text) > 12 and text in correct):
                        errors.append(f"{qid} distractor overlaps correct")
                    for sentence in sentences:
                        if sentence.casefold() in text.casefold():
                            errors.append(f"{qid} distractor contains a PDF sentence")
                            break
            elif question["type"] == "tf":
                if question["prompt"] != TF_PROMPT:
                    errors.append(f"{qid} bad prompt")
                statement = question["statement"]
                if question["correct"]:
                    if statement not in full or statement not in source or statement not in body:
                        errors.append(f"{qid} true statement not in section")
                else:
                    if statement in full or statement.casefold() in folded:
                        errors.append(f"{qid} false statement is in the PDF")
            else:
                errors.append(f"{qid} bad type")
    if errors:
        raise SystemExit("Verbatim check failed:\n" + "\n".join(errors))


DIAGRAM = "/schema-cellule-animale.webp"
# Justin's key, verbatim. Not the plant-cell figure: these labels match the animal cell.
KEY = [
    ("1", "noyaux"),
    ("1'", "ADN"),
    ("2", "membrane nucléaire"),
    ("3", "ribosome"),
    ("4", "lysosome"),
    ("5", "RER"),
    ("6", "appareil de Golgi"),
    ("7", "cytosquelette"),
    ("8", "REL"),
    ("9", "mitochondrie"),
    ("10", "lysosome"),
    ("11", "cytoplasme"),
    ("12", "vésicule"),
    ("13", "centriole"),
    ("14", "membrane cytoplasmique"),
]


def other_key_labels(key: list[tuple[str, str]], index: int, correct: str) -> list[str]:
    """Three other labels from this diagram. A repeated correct label is skipped."""
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


def diagram_questions(key: list[tuple[str, str]], image: str, id_prefix: str) -> list[dict]:
    allowed = {label for _, label in key}
    questions = []
    slots = ["a", "b", "c", "d"]
    for index, (number, label) in enumerate(key):
        if label not in allowed:
            raise SystemExit(f"correct label is not in the key: {label}")
        distractors = other_key_labels(key, index, label)
        correct_slot = slots[index % 4]
        choices = []
        distractor_at = 0
        for slot in slots:
            if slot == correct_slot:
                choices.append({"id": slot, "text": label})
            else:
                choices.append({"id": slot, "text": distractors[distractor_at]})
                distractor_at += 1
        texts = [choice["text"] for choice in choices]
        if texts.count(label) != 1 or len(set(texts)) != 4:
            raise SystemExit(f"diagram {number} does not have one unique answer")
        if any(text not in allowed for text in texts):
            raise SystemExit(f"diagram {number} uses a label outside its key")
        questions.append(
            {
                "id": f"{id_prefix}{index + 1}",
                "type": "mc",
                "prompt": f"Sur le schéma, que désigne le numéro {number} ?",
                "image": image,
                "choices": choices,
                "correctChoiceId": correct_slot,
                "source": f"{number}. {label}",
            }
        )
    return questions


def add_diagram(bank: dict) -> None:
    section = next(item for item in bank["sections"] if item["id"] == "b3")
    if section["title"] != "Cellule animale":
        raise SystemExit("diagram section is not Cellule animale")
    section["questions"] = diagram_questions(KEY, DIAGRAM, "b3-d") + section["questions"]


PLANT_DIAGRAM = "/schema-cellule-vegetale.jpg"
# Justin's key, verbatim. Numbers 2 and 4 are both « Appareil de Golgi ».
PLANT_KEY = [
    ("1", "Vésicule"),
    ("2", "Appareil de Golgi"),
    ("3", "Reticulum Endoplasmique rugueux"),
    ("4", "Appareil de Golgi"),
    ("5", "Plasmodesme"),
    ("6", "Paroi cellulosique"),
    ("7", "Pore Nucléaire"),
    ("8", "Membrane nucléaire"),
    ("9", "Nucléole"),
    ("10", "Noyau"),
    ("11", "Reticulum endoplasmique lisse"),
    ("12", "Thylakoide"),
    ("13", "Grain d'amidon"),
    ("14", "Chloroplaste"),
    ("15", "Grande vacuole"),
    ("16", "Mitochondrie"),
    ("17", "Cytoplasme"),
    ("18", "Membrane plasmique"),
]


def add_plant_diagram(bank: dict) -> None:
    section = next(item for item in bank["sections"] if item["id"] == "b5")
    if section["title"] != "Cellule végétale":
        raise SystemExit("plant diagram section is not Cellule végétale")
    section["questions"] = diagram_questions(PLANT_KEY, PLANT_DIAGRAM, "b5-d")


def main() -> None:
    full = load_pdf()
    bodies = section_slices(full)
    bank = build()
    verify(bank, full, bodies)
    add_diagram(bank)
    add_plant_diagram(bank)
    OUT.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {s["id"]: (s["title"], len(s["questions"])) for s in bank["sections"]}
    print(counts)
    print("total", sum(n for _, n in counts.values()))


if __name__ == "__main__":
    main()
