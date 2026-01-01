# GitHub Setup Guide

## ✅ Step 1: Local Repository Ready
Your local git repository has been initialized and your first commit has been created with 26 files.

## 📝 Step 2: Create GitHub Repository

1. **Go to GitHub**: Visit [https://github.com/new](https://github.com/new)

2. **Repository Settings**:
   - **Repository name**: `LearnSmart-AI` (or your preferred name)
   - **Description**: "Student Productivity & Burnout Prediction System with AI Chatbot"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)

3. **Click "Create repository"**

## 🚀 Step 3: Push to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

### Option A: If you haven't set up a remote yet

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Option B: If you want to use SSH (if you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 🔑 Step 4: Authentication

If prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)

### How to create a Personal Access Token:

1. Go to: [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "LearnSmart AI")
4. Select scopes: Check `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)
7. Use this token as your password when pushing

## 📋 Quick Commands Summary

```bash
# Check current status
git status

# Add changes (if you make any later)
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# View remote URL
git remote -v
```

## ⚠️ Important Notes

- ✅ Your `.env` file is already in `.gitignore` (API keys won't be uploaded)
- ✅ Your `venv/` folder is excluded
- ✅ User uploads folder is excluded
- ✅ Temporary scripts are excluded
- ✅ Your architecture diagram SVG is included

## 🎯 Next Steps After Upload

1. Add a repository description on GitHub
2. Consider adding topics/tags: `flask`, `machine-learning`, `burnout-prediction`, `student-productivity`, `ai-chatbot`
3. Update the README with badges if desired
4. Consider adding a LICENSE file

## 🆘 Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Error: "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Want to change branch name from master to main?
```bash
git branch -M main
```

