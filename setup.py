from setuptools import setup, find_packages

setup(
    name="doc2draw",
    version="0.1.0",
    description="Turn Word Documents, PDF Notes, and Video Courses into Stunning, Interactive Excalidraw Visual Maps",
    author="Doc2Draw Team",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "python-docx>=0.8.11",
        "pypdf>=3.0.0",
    ],
    extras_require={
        "ai": ["instructor>=1.0.0", "openai>=1.0.0"],
        "media": ["opencv-python>=4.8.0"],
        "dev": ["pytest>=7.0.0"],
    },
    entry_points={
        "console_scripts": [
            "doc2draw=doc2draw.cli:main",
        ],
    },
    python_requires=">=3.8",
)
