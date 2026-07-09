from pypdf import PdfReader, PdfWriter
from csv import DictReader
from pypdf.generic import NameObject, TextStringObject
import time
import argparse
import unicodedata

PDF_INPUT = r"C:\Users\cathe\Downloads\MedailleBronze2020Final_Fillable.pdf"
CSV_INPUT = r"C:\code\feuilleDexamenMedailleBronze\formulaire.csv"
PDF_OUTPUT = r"C:\code\feuilleDexamenMedailleBronze\rempli.pdf"

# writer est créé dans main(), une fois qu'on connaît le vrai chemin du PDF
# d'entrée (dépend des arguments -i passés en ligne de commande).
writer = None

data = {}


def set_font_size(field_name, size):
    fields = writer._root_object["/AcroForm"]["/Fields"]

    def apply_da(obj):
        obj[NameObject("/DA")] = TextStringObject(f"/Helv {size} Tf 0 g")

    def search(fields):
        for field in fields:
            obj = field.get_object()

            # Nom du champ
            if obj.get("/T") == field_name:
                apply_da(obj)
                # Si le champ a des widgets enfants (Kids), les mettre à jour aussi
                if "/Kids" in obj:
                    for kid in obj["/Kids"]:
                        apply_da(kid.get_object())
                return True

            # Cherche dans les enfants
            if "/Kids" in obj:
                if search(obj["/Kids"]):
                    return True

        return False

    return search(fields)


def normalize(text):
    """Normalise une chaîne pour comparaison robuste :
    - forme Unicode NFC (règle les accents encodés différemment, ex: export Google Sheets)
    - espaces superflus retirés
    - insensible à la casse
    """
    return unicodedata.normalize("NFC", text).strip().casefold()


def get_column(row, column_name):
    """Récupère une valeur du CSV en tolérant les différences d'accents,
    d'espaces ou de casse dans le nom de colonne."""
    target = normalize(column_name)
    for key, value in row.items():
        if key is not None and normalize(key) == target:
            return value
    raise KeyError(
        f"Colonne '{column_name}' introuvable. "
        f"Colonnes disponibles : {list(row.keys())}"
    )


def remplir_informations_moniteur():
    data["Text32"] = "Laurent Corbeil"
    data["Text33"] = "41FK768"
    data["Text34"] = "LaurentCorbeil05@gmail.com"
    data["Text35"] = "514"
    data["Text36"] = "386-4599"


def remplir_informations_evaluateur():
    data["Text39"] = "Antoine Cottenoir-Doucet"
    data["Text40"] = "4K73695"
    data["Text41"] = "antoine.doucet@icloud.com"
    data["Text42"] = "438"
    data["Text47"] = "394-2526"
    data["Check Box50"] = "/Yes"


def remplir_informations_facturation():
    data["Text19"] = "Centre recreoaquatique de Blainville"
    data["Text20"] = "450"
    data["Text21"] = "434-5275"
    data["Text22"] = " 190 Rue Marie Chapleau"
    data["Text23"] = "Blainville"
    data["Text24"] = "QC"
    data["Text25"] = "J7C 0E7"


def remplir_informations_examen():
    data["Date28_af_date"] = time.strftime("%Y-%m-%d")  # Date du jour
    data["Text29"] = "Centre recreoaquatique de Blainville"
    data["Text30"] = "450"
    data["Text31"] = "434-5275"


def remplir_informations_eleves(csv_input):
    suffixes = {
        0: "1.0",
        1: "1.1.0",
        2: "1.1.1.0",
        3: "1.1.1.1.0",
        4: "1.1.1.1.1.0",
        5: "1.1.1.1.1.1",
        6: ".0.0",
        7: ".0.1.0",
        8: ".0.1.1.0",
        9: ".0.1.1.1.0",
        10: ".0.1.1.1.1.0",
        11: ".0.1.1.1.1.1.0",
        12: ".0.1.1.1.1.1.1",
    }
    with open(csv_input, newline="", encoding="utf-8-sig") as csvfile:

        rows = list(DictReader(csvfile))
        nbPersonnes = sum(
            1 for row in rows if get_column(row, "Nom") and get_column(row, "Prenom")
        )
        if nbPersonnes > 6:
            data["More Candidates"] = "/Yes"

        # 0 = taille automatique, le lecteur PDF (Acrobat, Edge, etc.)
        # calcule lui-même la meilleure taille pour que le texte tienne
        for suffix in suffixes.values():
            set_font_size("Email" + suffix, 0)

        for index, row in enumerate(rows):

            if index >= nbPersonnes:
                break

            # Le vrai suffixe du PDF
            suffix = suffixes.get(index, "")

            data["Name" + suffix] = (
                get_column(row, "Nom") + " " + get_column(row, "Prenom")
            )
            data["Address" + suffix] = get_column(row, "Adresse")
            data["City" + suffix] = get_column(row, "Ville")
            data["Postal" + suffix] = get_column(row, "Code postal")
            data["Email" + suffix] = get_column(row, "Username")
            data["Phone" + suffix] = get_column(row, "Téléphone")

            date = get_column(row, "Date de naissance").split("-")

            data["DOBY" + suffix] = date[0][-2:]
            data["DOBM" + suffix] = date[1]
            data["DOBD" + suffix] = date[2]


def main():
    global writer

    parser = argparse.ArgumentParser(
        description="Remplit la feuille d'examen Médaille de Bronze à partir d'un CSV."
    )
    parser.add_argument(
        "-csv",
        nargs="?",
        default=CSV_INPUT,
        help="Chemin vers le fichier CSV (défaut: %(default)s)",
    )
    parser.add_argument(
        "-i", "--input",
        default=PDF_INPUT,
        help="Chemin du PDF d'entrée (défaut: %(default)s)",
    )
    parser.add_argument(
        "-o", "--output",
        default=PDF_OUTPUT,
        help="Chemin du PDF de sortie (défaut: %(default)s)",
    )
    args = parser.parse_args()

    # Le PDF d'entrée n'est chargé qu'ici, une fois qu'on connaît
    # le vrai chemin (issu de -i, ou de la valeur par défaut)
    reader = PdfReader(args.input)
    writer = PdfWriter()
    writer.append(reader)

    remplir_informations_moniteur()
    remplir_informations_evaluateur()
    remplir_informations_facturation()
    remplir_informations_examen()
    remplir_informations_eleves(args.csv)

    print("\nDonnées envoyées:")
    for k, v in data.items():
        print(k, "=", v)

    for page in writer.pages:
        writer.update_page_form_field_values(
            page,
            data,
            auto_regenerate=True
        )

    # Force les lecteurs PDF à recalculer l'affichage (auto-fit du texte)
    writer.set_need_appearances_writer(True)

    with open(args.output, "wb") as f:
        writer.write(f)

    print("Terminé")


if __name__ == "__main__":
    main()