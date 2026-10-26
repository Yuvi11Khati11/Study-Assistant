"""Generate a searchable text version of the Data Visualization Lab Syllabus."""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def create_searchable_syllabus(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        "HeaderBox",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.black,
    )
    title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.black,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.black,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        leftIndent=15,
        textColor=colors.black,
        spaceAfter=2,
    )

    story = []

    # ================= PAGE 1 =================
    header_table = Table(
        [["Code: BADCCE7202", "Data Handling and Visualization Lab", "1 Credits [LTP: 0-0-2]"]],
        colWidths=[130, 260, 140],
    )
    header_table.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E2F0D9")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Course Outcome:</b> Students will be able:", body_style))
    story.append(Paragraph("• Apply fundamental data analytics techniques, using spreadsheet and database tools, to prepare, interpret on datasets.", bullet_style))
    story.append(Paragraph("• Identify the principles of visual perception.", bullet_style))
    story.append(Paragraph("• Apply core skills for visual analysis.", bullet_style))
    story.append(Paragraph("• Apply visualization techniques for various data analysis tasks.", bullet_style))
    story.append(Paragraph("• Implement data visualization methods to solve real world problems.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>A. LIST OF EXPERIMENTS:</b>", title_style))
    story.append(Paragraph("<b>1. Perform the Visualization of Spread sheet Models according to given requirement.</b>", body_style))
    story.append(Paragraph("1. For the given data set that contains immigration details to Canada from 1980 to 2013:", bullet_style))
    story.append(Paragraph("  • Create an area plot for top 6 immigrant countries from 1990 to 2013", bullet_style))
    story.append(Paragraph("  • Create and year-wise immigrant bar chart from India to Canada during the period of 1980 to 2013.", bullet_style))
    story.append(Paragraph("  • Create a box plot for Indian, Phillip in and China immigrants.", bullet_style))
    story.append(Paragraph("  • Show the total no. of immigrants from India and France countries using Area Chart and Pie chart.", bullet_style))
    story.append(Paragraph("  • Create a scatter Histogram for the immigrants from Fiji and Singapore in the year 2013.", bullet_style))
    story.append(Paragraph("Link for DataSet: https://www.un.org/en/development/desa/population/migration/data/empirical2/migrationflows.asp", bullet_style))
    story.append(Paragraph("2. Visualize the given Placement Data Full Class dataset that contains details about Campus Recruitment using the below techniques for appropriate dimensions and differentiate between the two techniques:", bullet_style))
    story.append(Paragraph("  • Histogram and Bar Chart [For histogram let no. of bins=10]", bullet_style))
    story.append(Paragraph("  • Facet Plot and Pair Plot", bullet_style))
    story.append(Paragraph("  • Area Chart and Pie Chart [For yes or no data]", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2. RDBMS Connectivity using Python</b>", body_style))
    story.append(Paragraph("Find out output of the joint operation applied to the company database. Apply inner join type to the following queries; apart from this apply other joins type to the first question.", bullet_style))
    story.append(Paragraph("• List the name of all employees who works for the research department.", bullet_style))
    story.append(Paragraph("• For every project located at 'Stafford' list the project number, the controlling Department number and Department manages last name.", bullet_style))
    story.append(Paragraph("• Find the name of all employees who works on the projects controlled by Dno=4.", bullet_style))
    story.append(Paragraph("• Make the list of project numbers for projects that involve an employee whose last name is 'Jennifer' as a worker or as a manager of the dept that controls the project.", bullet_style))
    story.append(Paragraph("• List the name of the employees who have no dependents.", bullet_style))
    story.append(Paragraph("• List the name of manager that have at least one dependent.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>3. Visualization of Semi-Structured Data</b>", body_style))
    story.append(Paragraph("1. Create a dictionary for the below data and convert the data into JSON using dump() method from JSON package:", bullet_style))

    p1_table_data = [
        ["S.NO", "Name", "Department", "GPA", "Future Preference"],
        ["1", "Amy", "CSE", "8.7", "Placements"],
        ["2", "Rebekah", "ECE", "9.2", "Higher Education"],
        ["3", "David", "CSE", "5.6", "Higher Education"],
        ["4", "Sophia", "CSE", "6.8", "Placements"],
        ["5", "Lucas", "ECE", "7.5", "Placements"],
        ["6", "Andrew", "CSE", "8.9", "Higher Education"],
        ["7", "Evan", "CSE", "7.9", "Placements"],
        ["8", "Rose", "CSE", "8.7", "Higher Education"],
    ]
    t1 = Table(p1_table_data, colWidths=[40, 100, 90, 60, 130])
    t1.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t1)

    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Paragraph("<b>3. Visualization of Semi-Structured Data (Continued)</b>", body_style))
    p2_table_data = [
        ["S.NO", "Name", "Department", "GPA", "Future Preference"],
        ["9", "Luis", "ECE", "7.2", "Higher Education"],
        ["10", "Blake", "ECE", "6.8", "Higher Education"],
        ["11", "Finn", "CSE", "7.2", "Placements"],
        ["12", "Alan", "ECE", "8.7", "Placements"],
        ["13", "Olivia", "ECE", "6.8", "Higher Education"],
        ["14", "Isabella", "CSE", "8.7", "Placements"],
        ["15", "Scarlett", "ECE", "6.8", "Higher Education"],
    ]
    t2 = Table(p2_table_data, colWidths=[40, 100, 90, 60, 130])
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t2)
    story.append(Spacer(1, 4))

    story.append(Paragraph("i. Plot a graph showing the difference in Future Preferences of the students.", bullet_style))
    story.append(Paragraph("ii. Visualize the student's statistics based on the feature 'Department'.", bullet_style))
    story.append(Paragraph("iii. Plot a pie chart for the feature GPA.", bullet_style))
    story.append(Paragraph("2. For the below given data set which contains world population in json format:", bullet_style))
    story.append(Paragraph("Link: https://query.data.world/s/uvvfp4usm2q4mlapbqtoi2stgunwda", bullet_style))
    story.append(Paragraph("iv. Read the data using pandas in column orient.", bullet_style))
    story.append(Paragraph("v. Using appropriate plotting technique visualize the given data on the basis of population feature.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4. Introduction to Tableau and Aggregation Methods in Any Data Visualization tool of your choice.</b>", body_style))
    story.append(Paragraph("Connect the given Bus Safety dataset to Tableau and perform the below tasks on separate sheets:", bullet_style))
    story.append(Paragraph("i. Go to meta-data of the data set and change the column name form 'Date Of Incident' to 'Date' and 'Bus Garage' to 'Garage'.", bullet_style))
    story.append(Paragraph("ii. Visualize the no. of Incidents by different Operators and explore various possible charts.", bullet_style))
    story.append(Paragraph("iii. Show a pie chart depicting the age categories as Adult, Child, Elderly and Unknown and no. of incidents in each category.", bullet_style))
    story.append(Paragraph("iv. Show the statistics of Route No.'s in purple color Bar Chart.", bullet_style))
    story.append(Paragraph("v. Create a chart for 'Borough' feature depicting the total count of each and then sort it in ascending order.", bullet_style))
    story.append(Paragraph("vi. Depict the no. of incidents under the eight Incident Event Types for each of the Boroughs in the form of horizontal bar chart.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>5. Visual Encodings and Basic Dash boards in Any Data Visualization tool of your choice</b>", body_style))
    story.append(Paragraph("For the given dataset FIFA.csv that contains data about various football players, perform tasks on separate sheets:", bullet_style))
    story.append(Paragraph("i. After connecting the data use the data interpreter and clean the data.", bullet_style))
    story.append(Paragraph("ii. Create a horizontal bar chart to depict the International Reputation of various nations on an avg.", bullet_style))
    story.append(Paragraph("iii. Check if there is any relation between wage and position(left/right). If yes, describe the relation.", bullet_style))
    story.append(Paragraph("iv. Plot a bar chart against Avg. Heading Accuracy and Body Type. Find out which body type has highest and least accuracy.", bullet_style))
    story.append(Paragraph("v. Create a yellow colored Tree Chart to depict the total penalties of each nation and thus determine the highest and lowest.", bullet_style))
    story.append(Paragraph("vi. Using the above sheets create a dashboard and write an analysis report of what insights can be drawn from this.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>6. Interactive Plots in Python</b>", body_style))
    story.append(Paragraph("Using the in-built 'Car Crashes' dataset from seaborn library perform the below tasks:", bullet_style))
    story.append(Paragraph("i. Create a sub-dataset df that contains 'total', 'speeding', 'alcohol' columns only.", bullet_style))
    story.append(Paragraph("ii. Visualize an interactive bar plot for df.", bullet_style))
    story.append(Paragraph("iii. Using bar iplot, display the mean of all columns in the original dataset.", bullet_style))
    story.append(Paragraph("iv. Visualize a scatter matrix plot for the dataset (set of all scatter plots for numeric columns).", bullet_style))
    story.append(Paragraph("v. Depict an interactive box plot for df.", bullet_style))
    story.append(Paragraph("vi. Show a histogram plot for df interactively.", bullet_style))
    story.append(Paragraph("vii. Visualize 3D iplot for the data and give your insights so as to why and when should 3D visualization be used.", bullet_style))

    story.append(PageBreak())

    # ================= PAGE 3 =================
    story.append(Paragraph("<b>7. Hierarchical and Topographical Data Visualizations in Any Data Visualization tool of your choice.</b>", body_style))
    story.append(Paragraph("Using the in-built data set from link: https://www.bls.gov/cpi/tables/relative-importance/home.htm#Archived%20Relative%20Importance%20Data", bullet_style))
    story.append(Paragraph("i. Develop a sunburst pie chart to visualize all items.", bullet_style))
    story.append(Paragraph("ii. Create a tree map graph to display data in rectangular box.", bullet_style))
    story.append(Paragraph("iii. Display the data in hierarchical format using sankey diagram.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>8. Calendar Heat maps Data Visualizations in Python</b>", body_style))
    story.append(Paragraph("i. Write a Pandas program to create a heat map for comparison of top 10 years in which UFO was sighted vs each Month.", bullet_style))
    story.append(Paragraph("ii. Load the dataset from 'flight_dealy.csv' and create a heat map to show relationship between various fields.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>9. Time Series Data Visualization in Python</b>", body_style))
    story.append(Paragraph("Collect dataset from: https://github.com/Neelu-Tiwari/dataset/blob/main/stock_data.csv", bullet_style))
    story.append(Paragraph("i. Plot the changes that occurred in data over time.", bullet_style))
    story.append(Paragraph("ii. Create a bar plot of month data for 2016 and 2017.", bullet_style))
    story.append(Paragraph("iii. Practice exercises from learnche.org and r-exercises.com.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>10. Retail Department Store Chain Visualization Task</b>", body_style))
    story.append(Paragraph("Imagine working at one location of a retail department store chain. Compare your location sales by product category against average sales across all locations.", bullet_style))
    story.append(Paragraph("Dataset link: https://docs.google.com/spreadsheets/d/1VDG-ZpkkRaAituejvzlJ1Ky24LMpQfTN/edit#gid=416232713", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>11. MIT Aesthetics and Computation Research Group</b>", body_style))
    story.append(Paragraph("Select a member of the MIT aesthetics and computation research group (http://acg.media.mit.edu/). Briefly discuss their work and review how the technique helps information visualization (amount of information vs aesthetics).", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>12. Census Dimension Ordering</b>", body_style))
    story.append(Paragraph("Given a census dataset, describe three or more ways you might order the dimensions prior to visualization. Use US County Census dataset from openindicators.org.", bullet_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>B. RECOMMENDED STUDY MATERIAL</b>", title_style))
    story.append(Paragraph("<b>Recommended Text Books:</b>", body_style))
    story.append(Paragraph("1. <i>Effective Data Storytelling: How to Drive Change with Data, Narrative, and Visuals</i> by Brent Dykes (Edition: 2018).", bullet_style))
    story.append(Paragraph("2. <i>Effective Data Visualization: The Right Chart for the Right Data</i> by Stephanie D. H. Evergreen (Edition: 2021, Publication: Evergreen Data & Evaluation, LLC).", bullet_style))
    story.append(Paragraph("3. <i>The Visual Display of Quantitative Information</i> by Edward R. Tufte (Edition: 2018, Publication: Amazon).", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Reference Books:</b>", body_style))
    story.append(Paragraph("1. <i>Information Dashboard Design: Displaying Data for At-a-glance Monitoring</i> by Stephen Few, O'Reilly.", bullet_style))
    story.append(Paragraph("2. <i>The Accidental Analyst: Show Your Data Who's Boss</i> by Eileen and Stephen McDaniel, O'Reilly.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Online Resources:</b>", body_style))
    story.append(Paragraph("1. https://towardsdatascience.com/visualize-hierarchical-data-using-plotly-and-datapane-7e5abe2686e1", bullet_style))
    story.append(Paragraph("2. https://www.idvbook.com/index.html%3Fp=44.html", bullet_style))

    doc.build(story)
    return output_path


if __name__ == "__main__":
    target1 = Path("data") / "sample" / "DataVisulizationLabSyllabus_searchable.pdf"
    create_searchable_syllabus(target1)
    print("Created searchable syllabus at:", target1)

    target2 = Path("C:/Users/yuvij/Downloads/DataVisulizationLabSyllabus_searchable.pdf")
    create_searchable_syllabus(target2)
    print("Created copy in Downloads at:", target2)
