from Scrap.scrap_indeed.scrap_indeed import run_scraping as indeedscrap
from Scrap.scrap_linkdin.script_without_login import ScrapLinkdin




def sysInit():
    states = [
        "Alabama, United States",
        "Alaska, United States",
        "Arizona, United States",
        "Arkansas, United States",
        "California, United States",
        "Colorado, United States",
        "Indiana, United States",
        "Iowa, United States",
        "Kansas, United States",
        "Kentucky, United States",
        "Louisiana, United States",
        "Maine, United States",
        "Maryland, United States",
        "Massachusetts, United States",
        "Michigan, United States",
        "Minnesota, United States",
        "Mississippi, United States",
        "Connecticut, United States",
        "Delaware, United States",
        "Florida, United States",
        "Georgia, United States",
        "Hawaii, United States",
        "Idaho, United States",
        "Illinois, United States",
        "Missouri, United States",
        "Montana, United States",
        "Nebraska, United States",
        "Nevada, United States",
        "New Hampshire, United States",
        "New Jersey, United States",
        "New Mexico, United States",
        "New York, United States",
        "North Carolina, United States",
        "North Dakota, United States",
        "Ohio, United States",
        "Oklahoma, United States",
        "Oregon, United States",
        "Pennsylvania, United States",
        "Rhode Island, United States",
        "South Carolina, United States",
        "South Dakota, United States",
        "Tennessee, United States",
        "Texas, United States",
        "Utah, United States",
        "Vermont, United States",
        "Virginia, United States",
        "Washington, United States",
        "West Virginia, United States",
        "Wisconsin, United States",
        "Wyoming, United States"
    ]

    
    print("___________START CRON JOB _____________")
    keywords= [
        'Vertex Pharmaceuticals', 
        'Takeda', 
        'Gilead Sciences', 
        'Eli Lilly', 
        'Pfizer', 
        'Astrazeneca', 
        'Pharmaceuticals Jobs', 
        'Orbital Therapeutics',

        'Chief Executive Officer pharma',
        'Chief Operating Officer Pharma',
        'Chief Scientific Officer Pharma',
        'Chief Medical Officer Pharma',
        'Vice President Pharma',
        'Vice President Of Research And Development Pharma',
        'Vice President Of Clinical Development Pharma',
        'Vice President Of Medical Affairs Pharma',
        'Director of Research and Development Pharma',
        'Director of Clinical Operations Pharma',
        'Director of Medical Affairs Pharma',
        'Director Of Pharmacy',
        'Director Pharmacology',
        'Pharmacovigilance Manager',
        'Pharmacovigilance',
        'Medical Affairs Pharma',
        'Research Scientist Pharma',
        'Senior Scientist Pharma'
        'Principal Scientist Pharma',
        'Medical Science Liaison Pharma'
        ]
    for keyword in keywords:
        for state in states:
            indeedscrap(city_name = state, keyword= keyword)

    for keyword in keywords:
        for state in states:
            ScrapLinkdin(city_name=state, key_word=keyword)
    
    



if __name__ == "__main__":
    sysInit()


"""

###############################   Crontab  ###################################################################
Runing python script with a virtualenv :

* * * * * cd /home/admin112/Documents/backup/Hnh_office/Project_KUBER/Project/Project_Kuber/ && /home/admin112/Documents/backup/Hnh_office/Project_KUBER/Project/Project_Kuber/myenv/bin/python /home/admin112/Documents/backup/Hnh_office/Project_KUBER/Project/Project_Kuber/cron.py >> /home/admin112/Documents/backup/Hnh_office/Project_KUBER/Project/Project_Kuber/cron.log 2>&1


* * * * * cd /home/admin112/Hnh_office/Project_Kuber/ && /home/admin112/Hnh_office/Project_Kuber/env/bin/python /home/admin112/Hnh_office/Project_Kuber/cron.sh >> /home/admin112/Hnh_office/Project_Kuber/cron.log 2>&1


*/10 * * * * cd /hnh/Project_Kuber/ && /hnh/Project_Kuber/env/bin/python /hnh/Project_Kuber/cron.py >> /hnh/Project_Kuber/cron.log 2>&1

"""

# from webapi.models import Jobs

# keywords_title = ['pharma', 'Pharmaceuticals', 'Biotech', 'Biotechnology', 'Pharmacology', 'Microbiological']
# keywords_description= ['Pharmaceuticals', 'Biotechnology', 'Pharmacology']
# keyword_industries= ['Biotechnology', 'Pharmaceutical', 'Biotechnology Research']

# excluded_companies = [
#     'Vertex Pharmaceuticals', 
#     'Takeda', 
#     'Gilead Sciences', 
#     'Eli Lilly', 
#     'Pfizer', 
#     'Astrazeneca', 
#     'Pharmaceuticals', 
#     'Orbital Therapeutics'
# ]

# # Filter jobs that contain any of the keywords in their job title or description
# pharma_related_jobs_description = Jobs.objects.filter(
#     job_description__iregex=r'(' + '|'.join(keywords_description) + ')'
# )

# pharma_related_jobs_filter = Jobs.objects.filter(
#     job_title__iregex=r'(' + '|'.join(keywords_title) + ')',
# ) | Jobs.objects.filter(
#     industries__iregex=r'(' + '|'.join(keyword_industries) + ')'
# ) 

# pharma_related_jobs= pharma_related_jobs_description & pharma_related_jobs_filter

# # Filter jobs that belong to the excluded companies
# excluded_company_jobs = Jobs.objects.filter(
#     company_name__in=excluded_companies
# )

# # Combine the two querysets to get all the jobs that should not be deleted
# jobs_to_keep = pharma_related_jobs | excluded_company_jobs

# # Get the IDs of the jobs to keep
# jobs_to_keep_ids = jobs_to_keep.values_list('id', flat=True)

# # Delete all jobs that are not in the jobs_to_keep_ids
# Jobs.objects.exclude(id__in=jobs_to_keep_ids).delete()
