"""system + human message templates"""

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# System prompt — define the recruiter persona and evaluation criteria
SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template("""...""")  # Your turn

# Analysis prompt — accept the job description and the CV text as variables
ANALYSIS_PROMPT = HumanMessagePromptTemplate.from_template(
    """...{job_description}...{cv_text}..."""
)  # Your turn

# Combine both into a single ChatPromptTemplate
CHAT_PROMPT = ChatPromptTemplate.from_messages([SYSTEM_PROMPT, ANALYSIS_PROMPT])
