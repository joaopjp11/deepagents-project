import xml.etree.ElementTree as ET
import csv


INPUT_XML = r"C:\Users\joaop\ICD10\ICD10\icd10pcs_index_2026.xml"
OUTPUT_CSV = r"src/data/icd10pcs_index_2026.csv"


def extract_text(element):
    """Extract element text."""
    text = (element.text or "").strip()
    for child in element:
        child_text = extract_text(child)
        if child_text:
            text += " " + child_text
    if element.tail:
        text += " " + element.tail.strip()
    return text.strip()


def extract_codes_from_element(element):
    """Extract codes from element (<code> or <codes>)."""
    codes = []
    for code_elem in element.findall(".//code"):
        code_text = extract_text(code_elem).strip()
        if code_text:
            codes.append(code_text)
    for codes_elem in element.findall(".//codes"):
        codes_text = extract_text(codes_elem).strip()
        if codes_text:
            codes.append(codes_text)
    return codes


def process_term(term_elem, main_term_title, parent_path, rows, level=0):
    """
    Process element <term>.
    Extract: title, use, see, code/codes.
    """
    level_attr = term_elem.get("level", "")

    title_elem = term_elem.find("title")
    term_title = extract_text(title_elem) if title_elem is not None else ""
    
    current_path = parent_path + [term_title] if term_title else parent_path
    
    for child in term_elem:
        if child.tag == "title":
            continue 
        
        elif child.tag == "use":
            use_text = extract_text(child).strip()
            if use_text:
                rows.append({
                    "main_term": main_term_title,
                    "path": " > ".join(current_path),
                    "full_term": " > ".join(current_path),
                    "level": level_attr or str(level),
                    "type": "use",
                    "value": use_text,
                    "code": ""
                })
        
        elif child.tag == "see":
            see_text = extract_text(child).strip()
            codes = extract_codes_from_element(child)
            if see_text or codes:
                rows.append({
                    "main_term": main_term_title,
                    "path": " > ".join(current_path),
                    "full_term": " > ".join(current_path),
                    "level": level_attr or str(level),
                    "type": "see",
                    "value": see_text,
                    "code": " | ".join(codes)
                })
        
        elif child.tag == "code":
            code_text = extract_text(child).strip()
            if code_text:
                rows.append({
                    "main_term": main_term_title,
                    "path": " > ".join(current_path),
                    "full_term": " > ".join(current_path),
                    "level": level_attr or str(level),
                    "type": "code",
                    "value": "",
                    "code": code_text
                })
        
        elif child.tag == "codes":
            codes_text = extract_text(child).strip()
            if codes_text:
                rows.append({
                    "main_term": main_term_title,
                    "path": " > ".join(current_path),
                    "full_term": " > ".join(current_path),
                    "level": level_attr or str(level),
                    "type": "codes",
                    "value": "",
                    "code": codes_text
                })
        
        elif child.tag == "term":
            process_term(child, main_term_title, current_path, rows, level + 1)


def parse_index_xml():
    """Parse for Index XML ICD-10-PCS."""
    tree = ET.parse(INPUT_XML)
    root = tree.getroot()

    rows = []

    for letter in root.findall("letter"):
        letter_title = letter.find("title")
        letter_name = extract_text(letter_title) if letter_title is not None else "?"
        
        for main_term in letter.findall("mainTerm"):
            title_elem = main_term.find("title")
            main_term_title = extract_text(title_elem) if title_elem is not None else ""
            
            if not main_term_title:
                continue
            
            for child in main_term:
                if child.tag == "title":
                    continue
                
                elif child.tag == "use":
                    use_text = extract_text(child).strip()
                    if use_text:
                        rows.append({
                            "main_term": main_term_title,
                            "path": main_term_title,
                            "full_term": main_term_title,
                            "level": "0",
                            "type": "use",
                            "value": use_text,
                            "code": ""
                        })
                
                elif child.tag == "see":
                    see_text = extract_text(child).strip()
                    codes = extract_codes_from_element(child)
                    if see_text or codes:
                        rows.append({
                            "main_term": main_term_title,
                            "path": main_term_title,
                            "full_term": main_term_title,
                            "level": "0",
                            "type": "see",
                            "value": see_text,
                            "code": " | ".join(codes)
                        })
                
                elif child.tag == "code":
                    code_text = extract_text(child).strip()
                    if code_text:
                        rows.append({
                            "main_term": main_term_title,
                            "path": main_term_title,
                            "full_term": main_term_title,
                            "level": "0",
                            "type": "code",
                            "value": "",
                            "code": code_text
                        })
                
                elif child.tag == "codes":
                    codes_text = extract_text(child).strip()
                    if codes_text:
                        rows.append({
                            "main_term": main_term_title,
                            "path": main_term_title,
                            "full_term": main_term_title,
                            "level": "0",
                            "type": "codes",
                            "value": "",
                            "code": codes_text
                        })
                
                elif child.tag == "term":
                    process_term(child, main_term_title, [main_term_title], rows, level=1)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "main_term",
                "path",
                "full_term",
                "level",
                "type",
                "value",
                "code"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    parse_index_xml()