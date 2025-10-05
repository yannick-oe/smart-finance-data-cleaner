import pandas as pd

def load_data(file_path):
    """Lädt CSV-Datei mit Transaktionsdaten."""
    try:
        df = pd.read_csv(file_path)
        print("✅ Datei erfolgreich geladen!")
        return df
    except FileNotFoundError:
        print("❌ Datei nicht gefunden. Bitte Pfad prüfen.")
        return None

def clean_data(df):
    """Bereinigt Spalten und Datentypen."""
    # Entferne Zeilen mit komplett fehlenden Werten
    df = df.dropna(how="all")

    # Falls Spaltennamen mal anders geschrieben sind, hier anpassen
    expected_cols = {"Datum", "Empfänger", "Betrag", "Kategorie"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Fehlende Spalten in CSV: {missing}")

    # Datentypen säubern
    # Wenn deine Beträge Komma statt Punkt haben, ersetze die nächste Zeile durch:
    # df["Betrag"] = (df["Betrag"].astype(str).str.replace(",", ".").astype(float))
    df["Betrag"] = df["Betrag"].astype(float)

    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
    df = df.dropna(subset=["Datum", "Betrag"])  # entferne Zeilen ohne Datum/Betrag
    return df

def analyze_data(df):
    """Einfache Auswertung der Finanzdaten."""
    total = df["Betrag"].sum()
    average = df["Betrag"].mean()

    # Top-3-Kategorien nach Anzahl
    top_categories_count = df["Kategorie"].value_counts().head(3)

    print("\n📊 Finanzanalyse:")
    print(f"Gesamtsumme aller Beträge: {total:.2f} €")
    print(f"Durchschnittlicher Betrag: {average:.2f} €")
    print("\nTop 3 Kategorien (nach Anzahl Buchungen):")
    print(top_categories_count)

def main():
    file_path = "data/transactions.csv"
    df = load_data(file_path)
    if df is not None:
        try:
            df = clean_data(df)
            analyze_data(df)
        except Exception as e:
            print(f"⚠️ Fehler bei der Verarbeitung: {e}")

if __name__ == "__main__":
    main()
