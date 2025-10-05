import argparse
import pandas as pd
from pathlib import Path

def load_data(file_path: str, decimal_comma: bool = False) -> pd.DataFrame | None:
    """Lädt CSV-Datei mit Transaktionsdaten."""
    try:
        df = pd.read_csv(file_path)
        print("✅ Datei erfolgreich geladen!")
        if decimal_comma:
            # Beträge wie -32,50 in -32.50 umwandeln
            if "Betrag" in df.columns:
                df["Betrag"] = (
                    df["Betrag"].astype(str).str.replace(",", ".", regex=False)
                )
        return df
    except FileNotFoundError:
        print("❌ Datei nicht gefunden. Bitte Pfad prüfen.")
        return None

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Bereinigt Spalten und Datentypen."""
    df = df.dropna(how="all")

    required = {"Datum", "Empfänger", "Betrag", "Kategorie"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Fehlende Spalten in CSV: {missing}")

    df["Betrag"] = pd.to_numeric(df["Betrag"], errors="coerce")
    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")

    df = df.dropna(subset=["Datum", "Betrag"])  # entfernt unbrauchbare Zeilen
    return df

def analyze_data(df: pd.DataFrame) -> dict:
    """Einfache Kennzahlen + Gruppierungen."""
    total = df["Betrag"].sum()
    average = df["Betrag"].mean()

    # Top-3 Kategorien nach Anzahl
    top_count = df["Kategorie"].value_counts().head(3)

    # Top-3 Kategorien nach SUMME der Beträge (absolut größte Ausgaben)
    by_sum = (
        df.groupby("Kategorie")["Betrag"]
        .sum()
        .sort_values()  # negative Werte (Ausgaben) stehen unten; wir drehen gleich um
    )
    # „Top Ausgaben“ = niedrigste (stärkst negative) Summen
    top_spend = by_sum.nsmallest(3)

    return {
        "total": total,
        "average": average,
        "top_count": top_count,
        "top_spend": top_spend,
    }

def export_results(df_clean: pd.DataFrame, out_path: str):
    """Speichert bereinigte Daten als CSV."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(out, index=False)
    print(f"💾 Bereinigte Daten exportiert nach: {out.resolve()}")

def main():
    parser = argparse.ArgumentParser(
        description="Smart Finance Data Cleaner – CSV einlesen, bereinigen, analysieren."
    )
    parser.add_argument(
        "--file", default="data/transactions.csv",
        help="Pfad zur CSV-Datei (Standard: data/transactions.csv)"
    )
    parser.add_argument(
        "--out", default=None,
        help="Optionaler Pfad, um bereinigte Daten als CSV zu exportieren (z. B. results/cleaned.csv)"
    )
    parser.add_argument(
        "--decimal-comma", action="store_true",
        help="Aktivieren, falls Beträge in der CSV Komma als Dezimaltrennzeichen nutzen"
    )
    args = parser.parse_args()

    df = load_data(args.file, decimal_comma=args.decimal_comma)
    if df is None:
        return

    try:
        df = clean_data(df)
        metrics = analyze_data(df)

        print("\n📊 Finanzanalyse:")
        print(f"Gesamtsumme aller Beträge: {metrics['total']:.2f} €")
        print(f"Durchschnittlicher Betrag: {metrics['average']:.2f} €")

        print("\nTop 3 Kategorien (nach Anzahl Buchungen):")
        print(metrics["top_count"])

        print("\nTop 3 Ausgabenkategorien (nach Summe – stärkste neg. Beträge):")
        print(metrics["top_spend"])

        if args.out:
            export_results(df, args.out)

    except Exception as e:
        print(f"⚠️ Fehler bei der Verarbeitung: {e}")

if __name__ == "__main__":
    main()
