def generate_project_html(title, description, technologies, link):
    """Generates the HTML for a project entry"""
    return f"""
    <div class="item">
        <h3 class="title"><a href="{link}" target="_blank">{title}</a></h3>
        <p class="summary">{description}<br/><b>Technology Stack - </b> {technologies}</p>
    </div>
    """

def generate_work_experience_html(title, company, team_name, company_url, year_range, description):
    """Generates the HTML for a work experience entry"""
    return f"""
    <div class="item">
        <h3 class="title">{title} - <span class="place"><a href="{company_url}" target="_blank">{company}</a></span> <span class="year">({year_range})</span></h3>
        <p><b>Team:</b> {team_name}<br/>{description}</p>
    </div>
    """
