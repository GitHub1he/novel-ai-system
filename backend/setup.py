from setuptools import setup, find_packages

setup(
    name="novel-ai-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "python-multipart>=0.0.12",
        "sqlalchemy>=2.0.36",
        "psycopg2-binary>=2.9.10",
        "alembic>=1.14.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        "openai>=1.50.0",
        "httpx>=0.28.0",
        "zhipuai>=2.1.0",
        "pydantic>=2.10.0",
        "pydantic-settings>=2.6.0",
        "python-dateutil>=2.9.0",
        "email-validator>=2.1.0",
        "slowapi>=0.1.9",
        "apscheduler>=3.10.4",
    ],
)