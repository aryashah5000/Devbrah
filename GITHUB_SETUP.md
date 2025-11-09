# GitHub Repository Setup Instructions

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **+** icon in the top right corner
3. Select **New repository**
4. Fill in the repository details:
   - **Repository name**: `devbrah` (or your preferred name)
   - **Description**: "Personalized AI Career Growth Newsletter - Microsoft for Startups Track"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **Create repository**

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/devbrah.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/devbrah.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify

1. Go to your GitHub repository page
2. You should see all your files there
3. The README.md will be displayed on the main page

## Additional Notes

- The `.gitignore` file is already configured to exclude:
  - Environment variables (`.env` files)
  - Database files (`.db`, `.sqlite`)
  - Node modules
  - Python cache files
  - Build artifacts

- **Important**: Never commit `.env` files with API keys or secrets!

## Optional: Add GitHub Actions for CI/CD

You can add GitHub Actions workflows later for:
- Automated testing
- Code quality checks
- Deployment automation

