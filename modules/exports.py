from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate
from io import BytesIO
from flask import Flask, make_response

def generate_pdf(links):
    # Create a new PDF document    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)

    flowables = []
    styles = getSampleStyleSheet()

    for link in links:

                
        flowables.append(Paragraph(get_first_line(link), styles["Normal"]))
        if link.comment:
            flowables.append(Paragraph(f'<i>{link.comment}</i>',styles["Italic"]))
        elif link.summary:
            flowables.append(Paragraph(f'<i>{link.summary}</i>',styles["Italic"]))

        tagline = ''
        for tag in link.tags :
            tagline += f' {tag.name}'
        flowables.append(Paragraph(f'<div>Tags: {tagline}</div>'))        

        flowables.append(Spacer(width=0, height=20))

    doc.build(flowables)
    
    response = make_response(pdf_buffer.getvalue())

    # Set the appropriate headers for the response
    response.headers["Content-Disposition"] = "attachment; filename=links.pdf"
    response.headers["Content-Type"] = "application/pdf"

    return response

def get_first_line(link):
    author = f'by {link.author}' if link.author else ''
    hyperlink = f'<a href="{link.get_address()}">{link.title}</a>'
    date =  f', published {link.document_modified_at}' if link.document_modified_at else ''        
    first_line = f'{hyperlink} {author} {date}' 
    print(f'exported link: {first_line}')
    return first_line