from fpdf import FPDF
import os
import re

_BDR_CODES = re.compile(r'([0-9]{6})')


def generate_text_file(
    similarity_scores: list[float],
    all_metadata: list[dict],
    output_path: str,
):
    """
    Generates a text file that have PBRU number + similarity score 
        for all the matches, one per line.
    
    Parameters
    ----------
    similarity_scores : list[float]
        List of match scores corresponding to each image path
    all_metadata : list[dict]
        List of all metadata corresponding to each image path
    pdf_path : str
        Path of output pdf file

    Returns
    -------
    None. A text file is generated at the output_path.
    """
    with open(output_path, "w") as f:
        for score, metadata in zip(similarity_scores, all_metadata):
            f.write(f"{metadata['dwc_catalog_number_ssi']} {score}\n")


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
        all_metadata: list[dict],
        pdf_path: str,
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
    all_metadata : list[dict]
        List of all metadata corresponding to each image path
    pdf_path : str
        Path of output pdf file
    image_dir : str
        Directory of segmented labels 

    Returns 
    -------
    None. A PDF file is generated at the pdf_path.
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

    for path, score, metadata in zip(matched_img_paths, similarity_scores, all_metadata):
        if "/" not in path:
            path = os.path.join(image_dir, path)

        code = re.search(_BDR_CODES, path).group(0) # type: ignore
        
        # Check remaining space on page
        current_y = pdf.get_y()
        if current_y + image_height + spacing_after_image > pdf.h - pdf.b_margin:
            pdf.add_page()

        # Add metadata
        catalog_num = metadata["dwc_catalog_number_ssi"]
        plant_name = metadata["dwc_accepted_name_usage_ssi"]
        year = metadata["dwc_year_ssi"]
        collectors = metadata["dwc_recorded_by_ssi"]

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

    pdf.output(pdf_path)

