from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "College Essay Sample")
    c.drawString(100, 730, "This is a sample essay regarding my passion for computer science.")
    c.drawString(100, 710, "I have always been interested in AI and machine learning.")
    c.drawString(100, 690, "It started when I built my first robot in high school.")
    c.save()

if __name__ == "__main__":
    create_pdf("pdfs/sample_essay.pdf")
    print("Created pdfs/sample_essay.pdf")
