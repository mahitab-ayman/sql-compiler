# GitHub Setup Guide

This guide will help you set up this project on GitHub.

## Initial Setup

1. **Create a new repository on GitHub**
   - Go to https://github.com/new
   - Name it: `sql-compiler` (or your preferred name)
   - Choose Public or Private
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)

2. **Initialize Git in your project directory**
   ```bash
   cd sql-compiler
   git init
   ```

3. **Add all files**
   ```bash
   git add .
   ```

4. **Create initial commit**
   ```bash
   git commit -m "Initial commit: SQL-like Compiler with all three phases"
   ```

5. **Add remote repository**
   ```bash
   git remote add origin https://github.com/mahitab-ayman/sql-compiler.git
   ```

6. **Push to GitHub**
   ```bash
   git branch -M main
   git push -u origin main
   ```

## Project Structure on GitHub

Your repository should contain:
```
sql-compiler/
├── .gitignore
├── README.md
├── GITHUB_SETUP.md
├── QUICKSTART.md
├── requirements.txt
├── lexer.py
├── parser.py
├── semantic_analyzer.py
├── visualizer.py
├── main.py
├── test_compiler.py
├── sample_input.sql
└── sample_input_errors.sql
```

## Updating the Repository

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

## Adding Project Description

On GitHub, you can add a project description:
- Go to your repository
- Click "Settings"
- Scroll to "Topics" and add: `compiler`, `sql`, `lexical-analyzer`, `parser`, `semantic-analyzer`, `python`

## License

If you want to add a license:
1. Go to https://choosealicense.com/
2. Choose an appropriate license (e.g., MIT for educational projects)
3. Create a `LICENSE` file in your repository

## Project Badges (Optional)

You can add badges to your README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

## Collaboration

If working in a team:
1. Add collaborators in repository Settings > Collaborators
2. Use branches for features:
   ```bash
   git checkout -b feature-name
   # Make changes
   git commit -m "Add feature"
   git push origin feature-name
   ```
3. Create Pull Requests for code review

## Notes

- The `.gitignore` file excludes generated files (PNG images, cache files, etc.)
- Keep your code clean and well-commented
- Update README.md as you add features
- Test your code before pushing

