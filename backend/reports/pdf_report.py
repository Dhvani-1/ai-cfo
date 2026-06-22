import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Import analytics modules
from analytics.tax_estimator import estimate_tax, generate_tax_insights
from analytics.tax_summary import get_gst_summary
from analytics.health_score import calculate_health_score, get_financial_grade
from analytics.risk_analysis import analyze_risk
from analytics.recommendations import generate_recommendations
from analytics.forecast import forecast_summary, calculate_cash_runway
from analytics.cashflow import calculate_cashflow
from analytics.profit_loss import profit_loss
from analytics.category_analysis import category_summary
from analytics.fraud_detection import detect_large_transactions, detect_isolation_forest_anomalies, detect_rapid_transactions
from analytics.duplicate_detection import detect_duplicates

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        kwargs['pageCompression'] = 0
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        # We suppress the header/footer on page 1 (Executive Summary / Cover page)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            
            # Header
            self.drawString(54, 755, "AI CFO - FINANCIAL PERFORMANCE REPORT")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
            # Footer
            self.setFont("Helvetica", 8)
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 35, page_text)
            self.drawString(54, 35, f"Confidential | Generated on {datetime.date.today().isoformat()}")
            self.line(54, 45, 558, 45)
            self.restoreState()

def get_merged_alerts(transactions):
    if not transactions:
        return []
    large = detect_large_transactions(transactions)
    if_anom = detect_isolation_forest_anomalies(transactions)
    rapid = detect_rapid_transactions(transactions)
    _, duplicates = detect_duplicates(transactions)
    all_raw = large + if_anom + rapid + duplicates
    
    from collections import defaultdict
    tx_alerts = defaultdict(list)
    for alert in all_raw:
        tx_alerts[alert["transaction_id"]].append(alert)
        
    tx_map = {t.id: t for t in transactions}
    
    sev_priority = {
        "critical": 3,
        "high": 3,
        "warning": 2,
        "medium": 2,
        "low": 1,
        "info": 1
    }
    
    merged_list = []
    for tx_id, alerts in tx_alerts.items():
        t = tx_map.get(tx_id)
        if not t:
            continue
        sources = list(dict.fromkeys([a["source"] for a in alerts]))
        reasons = list(dict.fromkeys([a["reason"] for a in alerts]))
        highest_sev = "low"
        highest_priority = 0
        for a in alerts:
            p = sev_priority.get(a["severity"].lower(), 0)
            if p > highest_priority:
                highest_priority = p
                highest_sev = a["severity"]
        max_confidence = max(a["confidence"] for a in alerts)
        
        score = 0
        if "duplicate" in sources:
            score += 40
        if "large_transaction" in sources:
            score += 20
        if "rapid_transaction" in sources:
            score += 15
        if "isolation_forest" in sources:
            score += 30
        fraud_score = min(100, max(0, score))
        
        merged_list.append({
            "transaction_id": tx_id,
            "severity": highest_sev,
            "fraud_score": fraud_score,
            "sources": sources,
            "reasons": reasons
        })
    return merged_list

def format_recommendation(r):
    if isinstance(r, dict):
        return r.get("message", str(r))
    return str(r)

def generate_pdf_report(user, transactions, invoices):
    os.makedirs("exports", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{user.id}_financial_report_{timestamp}.pdf"
    file_path = os.path.join("exports", filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#475569")
    )
    meta_val = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )
    empty_style = ParagraphStyle(
        'EmptyText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#94A3B8")
    )

    story = []

    # --- Fetch Analytics Data ---
    tax_est = estimate_tax(transactions)
    tax_ins = generate_tax_insights(transactions)
    gst_sum = get_gst_summary(invoices)
    
    health_data = calculate_health_score(transactions)
    health_score = health_data["health_score"]
    grade_info = get_financial_grade(health_score)
    risk_info = analyze_risk(transactions)
    recs = generate_recommendations(transactions)
    
    runway_info = calculate_cash_runway(transactions)
    forecast_data = forecast_summary(transactions)
    
    cashflow_data = calculate_cashflow(transactions)
    pnl_data = profit_loss(transactions)
    cat_data = category_summary(transactions)
    
    fraud_alerts = get_merged_alerts(transactions)
    total_alerts = len(fraud_alerts)
    avg_fraud_score = round(sum(a["fraud_score"] for a in fraud_alerts) / total_alerts, 2) if total_alerts > 0 else 0.0

    # --- PAGE 1: TITLE & EXECUTIVE SUMMARY ---
    story.append(Paragraph("AI CFO Financial Report", title_style))
    story.append(Spacer(1, 10))

    # Metadata Card
    meta_table_data = [
        [Paragraph("User Name:", meta_label), Paragraph(user.name or "N/A", meta_val),
         Paragraph("Report Type:", meta_label), Paragraph("Executive Full Report", meta_val)],
        [Paragraph("User Email:", meta_label), Paragraph(user.email, meta_val),
         Paragraph("Generated At:", meta_label), Paragraph(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), meta_val)],
        [Paragraph("Total Transactions:", meta_label), Paragraph(str(len(transactions)), meta_val),
         Paragraph("Total Invoices:", meta_label), Paragraph(str(len(invoices)), meta_val)]
    ]
    meta_table = Table(meta_table_data, colWidths=[120, 132, 110, 142])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    # Executive Summary KPI block
    story.append(Paragraph("Executive Summary", section_style))
    
    kpi_table_data = [
        [Paragraph("Key Performance Indicator", meta_label), Paragraph("Value", meta_label)],
        [Paragraph("Total Income", normal_style), Paragraph(f"${round(tax_est['income'], 2):,.2f}", normal_style)],
        [Paragraph("Total Expenses", normal_style), Paragraph(f"${round(tax_est['expenses'], 2):,.2f}", normal_style)],
        [Paragraph("Net Cashflow", normal_style), Paragraph(f"${round(cashflow_data.get('net_cashflow', 0.0), 2):,.2f}", normal_style)],
        [Paragraph("Financial Health Score", normal_style), Paragraph(f"{health_score} / 100", normal_style)],
        [Paragraph("Financial Health Grade", normal_style), Paragraph(f"{grade_info['grade']} ({grade_info['description']})", normal_style)],
        [Paragraph("Fraud Alerts Flagged", normal_style), Paragraph(str(total_alerts), normal_style)],
        [Paragraph("Estimated Taxable Income", normal_style), Paragraph(f"${round(tax_est['taxable_income'], 2):,.2f}", normal_style)]
    ]
    kpi_table = Table(kpi_table_data, colWidths=[250, 254])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    # Quick fix for KPI header text color
    for i in range(2):
        kpi_table_data[0][i].style.textColor = colors.white
        kpi_table_data[0][i].style.fontName = 'Helvetica-Bold'
        
    story.append(kpi_table)
    story.append(PageBreak())

    # --- PAGE 2+: DETAILED SECTIONS ---

    # 1. Financial Summary
    story.append(Paragraph("1. Financial Summary", section_style))
    if not transactions:
        story.append(Paragraph("No transactions found.", empty_style))
    else:
        summary_desc = (
            f"During the analyzed period, you generated a total income of <b>${round(tax_est['income'], 2):,.2f}</b> "
            f"against total expenses of <b>${round(tax_est['expenses'], 2):,.2f}</b>, resulting in a net cashflow "
            f"of <b>${round(cashflow_data.get('net_cashflow', 0.0), 2):,.2f}</b>. Your cash burn rate is "
            f"<b>${round(cashflow_data.get('burn_rate', 0.0), 2):,.2f}</b> per month."
        )
        story.append(Paragraph(summary_desc, normal_style))
    story.append(Spacer(1, 10))

    # 2. Category Analysis
    story.append(Paragraph("2. Category Analysis", section_style))
    if not transactions or not cat_data:
        story.append(Paragraph("No spending data available by category.", empty_style))
    else:
        cat_table_data = [[Paragraph("Category", meta_label), Paragraph("Amount Spent", meta_label), Paragraph("% of Total Expenses", meta_label)]]
        total_exp = tax_est['expenses']
        for cat, amt in sorted(cat_data.items(), key=lambda x: x[1], reverse=True):
            pct = round((amt / total_exp) * 100.0, 2) if total_exp > 0 else 0.0
            cat_table_data.append([
                Paragraph(cat, normal_style),
                Paragraph(f"${round(amt, 2):,.2f}", normal_style),
                Paragraph(f"{pct}%", normal_style)
            ])
        cat_table = Table(cat_table_data, colWidths=[180, 160, 164])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(cat_table)
    story.append(Spacer(1, 10))

    # 3. Forecast Summary
    story.append(Paragraph("3. Forecast Summary", section_style))
    if not transactions:
        story.append(Paragraph("No historical records to build forecasts.", empty_style))
    else:
        forecast_desc = (
            f"Based on your transaction trends, your current cash runway is estimated at "
            f"<b>{runway_info.get('runway_months', 0.0)} months</b> (Status: <b>{runway_info.get('status', 'N/A')}</b>). "
            f"The predicted average monthly income is <b>${round(forecast_data.get('predicted_monthly_income', 0.0), 2):,.2f}</b> "
            f"and average monthly expenses is <b>${round(forecast_data.get('predicted_monthly_expenses', 0.0), 2):,.2f}</b>."
        )
        story.append(Paragraph(forecast_desc, normal_style))
    story.append(Spacer(1, 10))

    # 4. Health Score & Recommendations
    story.append(Paragraph("4. Health Score & Recommendations", section_style))
    health_desc = (
        f"Your financial health score is <b>{health_score} / 100</b>, giving you a grade of "
        f"<b>{grade_info['grade']} ({grade_info['description']})</b>. Your analyzed risk level "
        f"is <b>{risk_info.get('risk_level', 'N/A').upper()}</b>.<br/>"
        f"<b>Key Ratios:</b> Savings Ratio: <b>{health_data['components']['raw']['savings_ratio']}%</b> | "
        f"Expense Ratio: <b>{health_data['components']['raw']['expense_ratio']}%</b>."
    )
    story.append(Paragraph(health_desc, normal_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Top Financial Recommendations:</b>", meta_label))
    if not recs:
        story.append(Paragraph("No recommendations generated.", empty_style))
    else:
        for r in recs[:4]: # Top 4 recommendations
            msg = format_recommendation(r)
            story.append(Paragraph(f"• {msg}", normal_style))
    story.append(Spacer(1, 10))

    # 5. Fraud Summary
    story.append(Paragraph("5. Fraud Summary", section_style))
    fraud_desc = (
        f"A total of <b>{total_alerts} suspicious alerts</b> were flagged by our rule-based "
        f"and machine learning detection algorithms. The average transaction risk score is "
        f"<b>{avg_fraud_score} / 100</b>."
    )
    story.append(Paragraph(fraud_desc, normal_style))
    if total_alerts > 0:
        story.append(Spacer(1, 6))
        fraud_table_data = [[Paragraph("Tx ID", meta_label), Paragraph("Severity", meta_label), Paragraph("Fraud Score", meta_label), Paragraph("Flagged Reasons", meta_label)]]
        for alert in fraud_alerts[:5]: # Top 5 alerts
            reasons_str = "; ".join(alert["reasons"])
            fraud_table_data.append([
                Paragraph(str(alert["transaction_id"]), normal_style),
                Paragraph(alert["severity"].upper(), normal_style),
                Paragraph(str(alert["fraud_score"]), normal_style),
                Paragraph(reasons_str, normal_style)
            ])
        fraud_table = Table(fraud_table_data, colWidths=[50, 80, 80, 294])
        fraud_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(fraud_table)
    story.append(Spacer(1, 10))

    # 6. Tax Summary & Insights
    story.append(Paragraph("6. Tax Summary", section_style))
    tax_desc = (
        f"Your estimated taxable income is <b>${round(tax_est['taxable_income'], 2):,.2f}</b> "
        f"on an expense ratio of <b>{tax_est['expense_ratio']}%</b>. Total GST paid is "
        f"<b>${round(gst_sum['total_gst_paid'], 2):,.2f}</b> across <b>{gst_sum['invoice_count']} invoices</b> "
        f"(Explicit: <b>{gst_sum['explicit_gst_invoices']}</b>, Estimated: <b>{gst_sum['estimated_gst_invoices']}</b>)."
    )
    story.append(Paragraph(tax_desc, normal_style))
    
    if not invoices:
        story.append(Paragraph("No invoices found.", empty_style))
    
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Tax Insights:</b>", meta_label))
    if not tax_ins.get("insights"):
        story.append(Paragraph("No tax insights available.", empty_style))
    else:
        for insight in tax_ins["insights"]:
            story.append(Paragraph(f"• {insight}", normal_style))
            
    story.append(Spacer(1, 15))
    story.append(Paragraph("Disclaimer: Tax calculations and estimates are indicative only and do not constitute professional or legal tax advice. Please consult a qualified tax professional for formal compliance.", disclaimer_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    return file_path
