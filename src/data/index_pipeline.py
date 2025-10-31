import xml.etree.ElementTree as ET
import pandas as pd
import logging
import os
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def parse_term(term_node: ET.Element, parent_titles: List[str], records: List[Dict[str, Any]], level: int = 0):
    """Recursively process <term> or <mainTerm> nodes."""
    title = (term_node.findtext("title") or "").strip()
    code = term_node.findtext("code")
    see = term_node.findtext("see")
    see_also = term_node.findtext("seeAlso")
    nemod_elems = term_node.findall("nemod")
    nemod_text = " ".join([n.text.strip() for n in nemod_elems if n.text]) if nemod_elems else None

    record = {
        "path": " > ".join(parent_titles + [title]) if title else " > ".join(parent_titles),
        "main_term": parent_titles[0] if parent_titles else title,
        "title": title,
        "code": code,
        "see": see,
        "see_also": see_also,
        "nemod": nemod_text,
        "level": level
    }
    records.append(record)

    # Process nested <term> recursively
    for child_term in term_node.findall("term"):
        parse_term(child_term, parent_titles + [title], records, level + 1)


def parse_icd10_index(xml_path: str) -> pd.DataFrame:
    """Parse ICD-10-CM index XML file into a flat list of entries."""
    logging.info(f"Parsing XML file: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    records: List[Dict[str, Any]] = []

    # Loop over <letter> elements
    for letter in root.findall("letter"):
        letter_title = letter.findtext("title")
        logging.info(f"Processing letter: {letter_title}")

        # Loop over <mainTerm> entries within each letter
        for main_term in letter.findall("mainTerm"):
            parse_term(main_term, [main_term.findtext("title") or ""], records, level=0)

    logging.info(f"Total index records extracted: {len(records)}")
    return pd.DataFrame(records)


def main():
    xsd_file = r"C:\Users\Utilizador\ICD10\icd10cm-index-April-2024.xsd"
    xml_file = r"C:\Users\Utilizador\ICD10\icd10cm-index-April-2024.xml"

    if not os.path.exists(xml_file):
        logging.error(f"XML file not found: {xml_file}")
        return

    df = parse_icd10_index(xml_file)
    logging.info(f"DataFrame created with {len(df)} rows")

    print(f"📘 Total entries extracted: {len(df)}")
    print(df.head(10))

    out_csv = "src/data/icd10_index_extracted.csv"
    df.to_csv(out_csv, index=False)
    logging.info(f"Saved extracted records to: {out_csv}")


if __name__ == "__main__":
    main()
