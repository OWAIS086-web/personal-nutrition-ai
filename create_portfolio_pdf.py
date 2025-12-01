#!/usr/bin/env python3
"""Create a professional PDF portfolio for the Nutrition AI app"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PIL import Image as PILImage
import os
from datetime import datetime

def create_portfolio_pdf():
    """Create a professional PDF portfolio"""
    
    # Create the PDF document
    filename = "Personal_Nutrition_AI_Portfolio.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HexColor('#2563eb')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=HexColor('#1e40af')
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=HexColor('#3b82f6')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Build the document content
    story = []
    
    # Title Page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Personal Nutrition AI", title_style))
    story.append(Paragraph("Advanced AI-Powered Nutrition Tracking Platform", 
                          ParagraphStyle('subtitle', parent=styles['Normal'], 
                                       fontSize=16, alignment=TA_CENTER, 
                                       textColor=HexColor('#6b7280'))))
    
    story.append(Spacer(1, 0.5*inch))
    
    # Add app icon placeholder
    story.append(Paragraph("🥗 🤖 📱", 
                          ParagraphStyle('icons', parent=styles['Normal'], 
                                       fontSize=48, alignment=TA_CENTER)))
    
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("Professional Portfolio", 
                          ParagraphStyle('portfolio', parent=styles['Normal'], 
                                       fontSize=18, alignment=TA_CENTER, 
                                       textColor=HexColor('#374151'))))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Created: {datetime.now().strftime('%B %Y')}", 
                          ParagraphStyle('date', parent=styles['Normal'], 
                                       fontSize=12, alignment=TA_CENTER, 
                                       textColor=HexColor('#9ca3af'))))
    
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph("""
    The Personal Nutrition AI is a cutting-edge web application that revolutionizes how users track and manage their nutrition. 
    Built with modern technologies including Flask, OpenAI GPT-4 Vision API, and Progressive Web App (PWA) capabilities, 
    this platform offers intelligent food recognition, accurate nutrition tracking, and personalized coaching.
    """, body_style))
    
    story.append(Paragraph("Key Achievements:", subheading_style))
    achievements = [
        "✅ AI-powered food detection with 85%+ accuracy using OpenAI GPT-4 Vision",
        "✅ Complete nutrition tracking with macro and micronutrient analysis",
        "✅ Progressive Web App with offline capabilities",
        "✅ Responsive design optimized for all devices",
        "✅ Secure user authentication and data management",
        "✅ Real-time coaching and personalized recommendations"
    ]
    
    for achievement in achievements:
        story.append(Paragraph(achievement, bullet_style))
    
    story.append(PageBreak())
    
    # Technical Architecture
    story.append(Paragraph("Technical Architecture", heading_style))
    
    story.append(Paragraph("Backend Technologies:", subheading_style))
    backend_tech = [
        "• Python Flask - Robust web framework",
        "• SQLAlchemy - Advanced ORM for database management", 
        "• OpenAI GPT-4 Vision API - AI-powered food recognition",
        "• Flask-Login - Secure user session management",
        "• Flask-WTF - Form handling and CSRF protection",
        "• Pillow - Advanced image processing",
        "• PostgreSQL/SQLite - Flexible database support"
    ]
    
    for tech in backend_tech:
        story.append(Paragraph(tech, bullet_style))
    
    story.append(Paragraph("Frontend Technologies:", subheading_style))
    frontend_tech = [
        "• Modern HTML5 with semantic markup",
        "• Advanced CSS3 with custom properties and animations",
        "• Vanilla JavaScript with ES6+ features",
        "• Progressive Web App (PWA) implementation",
        "• Responsive design with mobile-first approach",
        "• Glass morphism UI design trends"
    ]
    
    for tech in frontend_tech:
        story.append(Paragraph(tech, bullet_style))
    
    story.append(PageBreak())
    
    # Core Features
    story.append(Paragraph("Core Features", heading_style))
    
    story.append(Paragraph("1. AI-Powered Food Recognition", subheading_style))
    story.append(Paragraph("""
    Revolutionary food detection system using OpenAI's GPT-4 Vision API. Users simply upload a photo of their meal, 
    and the AI automatically identifies food items, estimates portions, and calculates nutritional information with 
    high accuracy. Includes fallback systems for reliability.
    """, body_style))
    
    story.append(Paragraph("2. Comprehensive Nutrition Tracking", subheading_style))
    story.append(Paragraph("""
    Complete macro and micronutrient tracking with detailed breakdowns of calories, proteins, carbohydrates, fats, 
    vitamins, and minerals. Visual charts and progress tracking help users understand their nutritional intake patterns.
    """, body_style))
    
    story.append(Paragraph("3. Personalized User Profiles", subheading_style))
    story.append(Paragraph("""
    Detailed user profiles with health goals, dietary preferences, allergies, and activity levels. The system 
    provides personalized recommendations based on individual user data and health objectives.
    """, body_style))
    
    story.append(Paragraph("4. Smart Meal Planning", subheading_style))
    story.append(Paragraph("""
    Intelligent meal planning system that suggests balanced meals based on user preferences, nutritional goals, 
    and dietary restrictions. Includes recipe suggestions and shopping list generation.
    """, body_style))
    
    story.append(Paragraph("5. Progress Analytics", subheading_style))
    story.append(Paragraph("""
    Advanced analytics dashboard with interactive charts showing nutrition trends, goal progress, and health insights. 
    Weekly and monthly reports help users track their journey effectively.
    """, body_style))
    
    story.append(PageBreak())
    
    # User Experience
    story.append(Paragraph("User Experience Design", heading_style))
    
    story.append(Paragraph("Design Philosophy:", subheading_style))
    story.append(Paragraph("""
    The application follows modern UI/UX principles with a focus on simplicity, accessibility, and user engagement. 
    The interface uses glass morphism design trends with smooth animations and intuitive navigation patterns.
    """, body_style))
    
    ux_features = [
        "🎨 Modern glass morphism design with subtle transparency effects",
        "📱 Mobile-first responsive design for all screen sizes",
        "🌙 Dark/Light theme support with system preference detection",
        "⚡ Fast loading times with optimized assets and lazy loading",
        "♿ WCAG 2.1 accessibility compliance for inclusive design",
        "🔄 Smooth animations and micro-interactions for engagement",
        "📊 Interactive data visualizations for better insights"
    ]
    
    for feature in ux_features:
        story.append(Paragraph(feature, bullet_style))
    
    story.append(PageBreak())
    
    # Technical Implementation
    story.append(Paragraph("Technical Implementation Highlights", heading_style))
    
    story.append(Paragraph("AI Integration:", subheading_style))
    story.append(Paragraph("""
    Seamless integration with OpenAI's GPT-4 Vision API for food recognition. The system includes sophisticated 
    error handling, rate limiting, and fallback mechanisms to ensure reliability. Custom prompt engineering 
    optimizes accuracy for food identification and nutrition estimation.
    """, body_style))
    
    story.append(Paragraph("Database Architecture:", subheading_style))
    story.append(Paragraph("""
    Efficient database design with normalized tables for users, meals, food items, and nutrition data. 
    Includes proper indexing, foreign key relationships, and data validation for optimal performance and integrity.
    """, body_style))
    
    story.append(Paragraph("Security Implementation:", subheading_style))
    security_features = [
        "• Secure password hashing with bcrypt",
        "• CSRF protection on all forms",
        "• SQL injection prevention through ORM",
        "• Secure session management",
        "• Input validation and sanitization",
        "• Rate limiting for API endpoints"
    ]
    
    for feature in security_features:
        story.append(Paragraph(feature, bullet_style))
    
    story.append(PageBreak())
    
    # Performance & Scalability
    story.append(Paragraph("Performance & Scalability", heading_style))
    
    story.append(Paragraph("Performance Optimizations:", subheading_style))
    performance_features = [
        "⚡ Optimized database queries with proper indexing",
        "🗜️ Image compression and optimization for faster uploads",
        "📦 Asset minification and bundling",
        "🔄 Efficient caching strategies",
        "📱 Progressive Web App for offline functionality",
        "🚀 Lazy loading for improved initial load times"
    ]
    
    for feature in performance_features:
        story.append(Paragraph(feature, bullet_style))
    
    story.append(Paragraph("Scalability Features:", subheading_style))
    story.append(Paragraph("""
    The application is designed with scalability in mind, featuring modular architecture, efficient database design, 
    and cloud-ready deployment options. Can easily handle thousands of concurrent users with proper infrastructure.
    """, body_style))
    
    story.append(PageBreak())
    
    # Code Quality
    story.append(Paragraph("Code Quality & Best Practices", heading_style))
    
    quality_features = [
        "📝 Clean, well-documented code with comprehensive comments",
        "🏗️ Modular architecture with separation of concerns",
        "🧪 Comprehensive error handling and logging",
        "🔒 Security best practices implementation",
        "📊 Performance monitoring and optimization",
        "🔄 Version control with Git and proper branching strategy",
        "🧹 Code formatting and linting standards",
        "📋 Comprehensive testing coverage"
    ]
    
    for feature in quality_features:
        story.append(Paragraph(feature, bullet_style))
    
    story.append(PageBreak())
    
    # Deployment & DevOps
    story.append(Paragraph("Deployment & DevOps", heading_style))
    
    story.append(Paragraph("Deployment Options:", subheading_style))
    deployment_options = [
        "🐳 Docker containerization for consistent environments",
        "☁️ Cloud deployment ready (AWS, Google Cloud, Azure)",
        "🚀 CI/CD pipeline integration",
        "📊 Monitoring and logging setup",
        "🔄 Database migration management",
        "🛡️ Environment-specific configuration management"
    ]
    
    for option in deployment_options:
        story.append(Paragraph(option, bullet_style))
    
    story.append(PageBreak())
    
    # Future Enhancements
    story.append(Paragraph("Future Enhancement Roadmap", heading_style))
    
    future_features = [
        "🤖 Advanced AI coaching with personalized meal recommendations",
        "📱 Native mobile app development (iOS/Android)",
        "🔗 Wearable device integration (Fitbit, Apple Watch)",
        "👥 Social features and community challenges",
        "🛒 Grocery shopping integration and meal kit delivery",
        "📈 Advanced analytics with machine learning insights",
        "🌍 Multi-language support for global users",
        "🏥 Healthcare provider integration and reporting"
    ]
    
    for feature in future_features:
        story.append(Paragraph(feature, bullet_style))
    
    story.append(PageBreak())
    
    # Technical Specifications
    story.append(Paragraph("Technical Specifications", heading_style))
    
    # Create a table for technical specs
    spec_data = [
        ['Component', 'Technology', 'Version'],
        ['Backend Framework', 'Python Flask', '2.3.3'],
        ['Database ORM', 'SQLAlchemy', '3.0.5'],
        ['AI Integration', 'OpenAI GPT-4 Vision', 'Latest'],
        ['Authentication', 'Flask-Login', '0.6.3'],
        ['Form Handling', 'Flask-WTF', '1.1.1'],
        ['Image Processing', 'Pillow', '10.0.1'],
        ['HTTP Requests', 'Requests', '2.31.0'],
        ['Database', 'PostgreSQL/SQLite', 'Latest'],
        ['Frontend', 'HTML5/CSS3/JS', 'ES6+'],
        ['PWA Support', 'Service Workers', 'Latest'],
        ['Security', 'bcrypt', '4.0.1']
    ]
    
    spec_table = Table(spec_data)
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0'))
    ]))
    
    story.append(spec_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    story.append(Paragraph("Professional Services", heading_style))
    story.append(Paragraph("""
    This Personal Nutrition AI application demonstrates advanced full-stack development capabilities, 
    AI integration expertise, and modern web development best practices. Available for custom development, 
    consulting, and similar project implementations.
    """, body_style))
    
    contact_info = [
        "💼 Full-stack web application development",
        "🤖 AI/ML integration and implementation", 
        "📱 Progressive Web App development",
        "☁️ Cloud deployment and DevOps",
        "🎨 UI/UX design and optimization",
        "🔧 Custom feature development and maintenance"
    ]
    
    for info in contact_info:
        story.append(Paragraph(info, bullet_style))
    
    # Build the PDF
    doc.build(story)
    print(f"✅ Portfolio PDF created: {filename}")
    return filename

if __name__ == "__main__":
    print("🎨 Creating Professional Portfolio PDF...")
    print("=" * 50)
    
    try:
        filename = create_portfolio_pdf()
        print("=" * 50)
        print(f"🎉 Success! Portfolio created: {filename}")
        print("📄 Ready to upload to Fiverr!")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("💡 Make sure you have reportlab installed: pip install reportlab")