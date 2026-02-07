"""Certificate PDF generation service"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from io import BytesIO
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CertificateGenerator:
    """Service for generating course completion certificates"""
    
    def __init__(self):
        self.page_size = A4
        self.width, self.height = self.page_size
    
    def generate_certificate(
        self,
        student_name: str,
        course_title: str,
        instructor_name: str,
        completion_date: datetime,
        course_duration: Optional[str] = None,
        certificate_id: Optional[str] = None
    ) -> BytesIO:
        """
        Generate a PDF certificate
        
        Args:
            student_name: Name of the student
            course_title: Title of the completed course
            instructor_name: Name of the instructor
            completion_date: Date of course completion
            course_duration: Optional duration (e.g., "40 hours")
            certificate_id: Optional unique certificate ID
        
        Returns:
            BytesIO object containing the PDF
        """
        buffer = BytesIO()
        
        try:
            # Create PDF canvas
            c = canvas.Canvas(buffer, pagesize=self.page_size)
            
            # Draw border
            self._draw_border(c)
            
            # Draw header
            self._draw_header(c)
            
            # Draw certificate content
            self._draw_content(
                c, student_name, course_title, instructor_name,
                completion_date, course_duration
            )
            
            # Draw footer
            self._draw_footer(c, certificate_id)
            
            # Save PDF
            c.save()
            buffer.seek(0)
            
            logger.info(f"Certificate generated for {student_name} - {course_title}")
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating certificate: {e}")
            raise
    
    def _draw_border(self, c: canvas.Canvas):
        """Draw decorative border"""
        margin = 0.5 * inch
        
        # Outer border
        c.setStrokeColor(colors.HexColor('#2563eb'))
        c.setLineWidth(3)
        c.rect(margin, margin, self.width - 2*margin, self.height - 2*margin)
        
        # Inner border
        c.setStrokeColor(colors.HexColor('#dbeafe'))
        c.setLineWidth(1)
        inner_margin = margin + 0.1*inch
        c.rect(inner_margin, inner_margin, 
               self.width - 2*inner_margin, self.height - 2*inner_margin)
    
    def _draw_header(self, c: canvas.Canvas):
        """Draw certificate header"""
        y_position = self.height - 1.5*inch
        
        # Logo/Icon
        c.setFont("Helvetica-Bold", 48)
        c.setFillColor(colors.HexColor('#2563eb'))
        c.drawCentredString(self.width/2, y_position, "🎓")
        
        # Platform name
        y_position -= 0.5*inch
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor('#1f2937'))
        c.drawCentredString(self.width/2, y_position, "SkillStudio")
        
        # Certificate title
        y_position -= 0.7*inch
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(colors.HexColor('#2563eb'))
        c.drawCentredString(self.width/2, y_position, "Certificate of Completion")
    
    def _draw_content(
        self,
        c: canvas.Canvas,
        student_name: str,
        course_title: str,
        instructor_name: str,
        completion_date: datetime,
        course_duration: Optional[str]
    ):
        """Draw main certificate content"""
        y_position = self.height - 4.5*inch
        
        # "This certifies that"
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor('#6b7280'))
        c.drawCentredString(self.width/2, y_position, "This certifies that")
        
        # Student name
        y_position -= 0.6*inch
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.HexColor('#1f2937'))
        c.drawCentredString(self.width/2, y_position, student_name)
        
        # Underline for name
        c.setStrokeColor(colors.HexColor('#2563eb'))
        c.setLineWidth(2)
        name_width = c.stringWidth(student_name, "Helvetica-Bold", 32)
        c.line(
            self.width/2 - name_width/2 - 20, y_position - 5,
            self.width/2 + name_width/2 + 20, y_position - 5
        )
        
        # "has successfully completed"
        y_position -= 0.6*inch
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor('#6b7280'))
        c.drawCentredString(self.width/2, y_position, "has successfully completed")
        
        # Course title
        y_position -= 0.6*inch
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor('#1f2937'))
        
        # Handle long course titles (wrap if needed)
        max_width = self.width - 2*inch
        course_width = c.stringWidth(course_title, "Helvetica-Bold", 20)
        
        if course_width > max_width:
            # Split into two lines if too long
            words = course_title.split()
            line1 = ""
            line2 = ""
            for word in words:
                test_line = line1 + " " + word if line1 else word
                if c.stringWidth(test_line, "Helvetica-Bold", 20) < max_width:
                    line1 = test_line
                else:
                    line2 = " ".join([line2, word]).strip()
            
            c.drawCentredString(self.width/2, y_position, line1)
            y_position -= 0.4*inch
            c.drawCentredString(self.width/2, y_position, line2)
        else:
            c.drawCentredString(self.width/2, y_position, course_title)
        
        # Date and duration
        y_position -= 0.8*inch
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor('#6b7280'))
        
        date_str = completion_date.strftime("%B %d, %Y")
        info_text = f"Completed on {date_str}"
        if course_duration:
            info_text += f" • Duration: {course_duration}"
        
        c.drawCentredString(self.width/2, y_position, info_text)
        
        # Instructor signature area
        y_position -= 1.2*inch
        
        # Signature line
        sig_width = 2*inch
        c.setStrokeColor(colors.HexColor('#6b7280'))
        c.setLineWidth(1)
        c.line(
            self.width/2 - sig_width/2, y_position,
            self.width/2 + sig_width/2, y_position
        )
        
        # Instructor name
        y_position -= 0.3*inch
        c.setFont("Helvetica", 11)
        c.drawCentredString(self.width/2, y_position, instructor_name)
        
        y_position -= 0.25*inch
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.HexColor('#9ca3af'))
        c.drawCentredString(self.width/2, y_position, "Course Instructor")
    
    def _draw_footer(self, c: canvas.Canvas, certificate_id: Optional[str]):
        """Draw certificate footer"""
        y_position = 0.8*inch
        
        # Certificate ID
        if certificate_id:
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#9ca3af'))
            c.drawCentredString(
                self.width/2, y_position,
                f"Certificate ID: {certificate_id}"
            )
        
        # Verification URL
        y_position -= 0.2*inch
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor('#9ca3af'))
        c.drawCentredString(
            self.width/2, y_position,
            "Verify at: skillstudio.com/verify"
        )


# Global certificate generator instance
certificate_generator = CertificateGenerator()
