from fpdf import FPDF
import os
import re
import requests

_BDR_CODES = re.compile(r'([0-9]{6})')


def fetch_catalog_metadata(bdr_code):
    """Fetch catalog metadata using the direct BDR API endpoint for the item."""
    metadata = {"dwc_catalog_number_ssi": f"PBRU {bdr_code}"}

    try:
        # API endpoint for the item
        api_url = f"https://repository.library.brown.edu/api/items/bdr:{bdr_code}/"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            # Catalog number
            if "dwc_catalog_number_ssi" in data:
                metadata["dwc_catalog_number_ssi"] = data["dwc_catalog_number_ssi"]

            # Scientific name
            if "dwc_accepted_name_usage_ssi" in data:
                metadata["dwc_accepted_name_usage_ssi"] = data["dwc_accepted_name_usage_ssi"]
            elif "dwc_scientific_name_ssi" in data:
                scientific_name = data["dwc_scientific_name_ssi"]
                if "dwc_scientific_name_authorship_ssi" in data:
                    scientific_name += f" {data['dwc_scientific_name_authorship_ssi']}"
                metadata["dwc_accepted_name_usage_ssi"] = scientific_name

            # Year
            if "dwc_year_ssi" in data:
                metadata["dwc_year_ssi"] = data["dwc_year_ssi"]

            # Collector info
            if "dwc_recorded_by_ssi" in data:
                metadata["dwc_recorded_by_ssi"] = data["dwc_recorded_by_ssi"]

            # IIIF image URL
            if data.get("iiif_resource_bsi", False):
                metadata["iiif_url"] = f"https://repository.library.brown.edu/iiif/image/bdr:{bdr_code}/info.json"

    except Exception as e:
        print(f"Error fetching metadata for BDR:{bdr_code} from API: {e}")

    if "dwc_accepted_name_usage_ssi" not in metadata:
        metadata["dwc_accepted_name_usage_ssi"] = f"Specimen {bdr_code}"

    return metadata


class PDFWithFooter(FPDF):
    """
    Define footer method for generating pdf file.
    """
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font: Arial italic 8
        self.set_font("Times", "I", 8)
        self.set_text_color(0, 0, 0)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
def generate_pdf(
        matched_img_paths: list[str], 
        similarity_scores: list[float],
        output_path: str,
        image_dir: str
    ) -> None:
    """
    Generates a PDF file that contains the search results, including 
        matched labels, their metadata, and URLs to the original images

    Parameters
    ----------
    matched_img_paths : list[str]
        List of paths to matched labels
    similarity_scores : list[float]
        List of match scores corresponding to each image path
    output_path : str
        Path of output pdf file
    image_dir : str
        Directory of segmented labels 

    Returns 
    -------
    None. A PDF file is generated at the output_path.
    """
    pdf = PDFWithFooter()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_auto_page_break(True, margin=10)

    font = "Times"
    image_height = 40
    spacing_after_image = 10

    # Info for first page
    pdf.set_font(font, size=12, style="BU")
    num_matches = f"Number of matches found: {len(matched_img_paths)}"
    pdf.cell(200, 10, txt=num_matches, ln=1, align="L") # type: ignore

    for path, score in zip(matched_img_paths, similarity_scores):
        if "/" not in path:
            path = os.path.join(image_dir, path)

        code = re.search(_BDR_CODES, path).group(0) # type: ignore
        
        # Check remaining space on page
        current_y = pdf.get_y()
        if current_y + image_height + spacing_after_image > pdf.h - pdf.b_margin:
            pdf.add_page()

        # Fetch and add metadata
        metadata = fetch_catalog_metadata(code)
        catalog_num = metadata.get("dwc_catalog_number_ssi") or "N/A"
        plant_name = metadata.get("dwc_accepted_name_usage_ssi") or "N/A"
        year = metadata.get("dwc_year_ssi") or "N/A"
        collectors = metadata.get("dwc_recorded_by_ssi") or "N/A"

        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font(font, style="")
        pdf.cell(200, 5, txt=f"Catalog number: {catalog_num}", ln=1, align="L") # type: ignore
        pdf.cell(200, 5, txt=f"Plant name: {plant_name}", ln=1, align="L") # type: ignore
        pdf.cell(200, 5, txt=f"Year collected: {year}", ln=1, align="L") # type: ignore
        pdf.cell(200, 5, txt=f"Collector(s): {collectors}", ln=1, align="L") # type: ignore

        # Add similarity score
        pdf.cell(200, 5, txt=f"Match score: {score:.2f}", ln=1, align="L") # type: ignore
        
        # Add hyperlink text
        link_url = f"https://repository.library.brown.edu/studio/item/bdr:{code}/"
        pdf.set_text_color(0, 0, 255)
        pdf.set_font(font, style="U")
        pdf.cell(200, 5, txt=link_url, ln=1, align="L", link=link_url) # type: ignore
        
        # Add image
        pdf.image(path, x=pdf.get_x(), y=pdf.get_y() + 2, h=image_height)
        pdf.ln(image_height + spacing_after_image)

    pdf.output(output_path)

