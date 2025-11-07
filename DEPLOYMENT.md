# Vercel Deployment Guide

This guide will walk you through deploying your resume website with AI chatbot to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Your OpenAI API key (get one from https://platform.openai.com/api-keys)
3. Git repository with your code (already done!)

## Step-by-Step Deployment

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Push your code to GitHub** (already done!)
   - Your code is in branch: `claude/create-website-showcase-011CUtbRqTKr19sgarXaQFU7`

2. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New" → "Project"

3. **Import your GitHub repository**
   - Select "Import Git Repository"
   - Find and select `d4deepakkv/mywebsite`
   - Click "Import"

4. **Configure the project**
   - **Framework Preset**: Select "Other" (or leave as detected)
   - **Root Directory**: Leave as is (.)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave as public or .

5. **Add Environment Variables**
   Click "Environment Variables" and add:
   ```
   Key: OPENAI_API_KEY
   Value: sk-your-actual-openai-api-key-here
   ```
   - Make sure to add it for Production, Preview, and Development

6. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (usually 1-2 minutes)
   - Your site will be live at: `https://your-project-name.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**
   ```bash
   cd /path/to/mywebsite
   vercel
   ```

4. **Follow the prompts**
   - Set up and deploy: Yes
   - Which scope: Your account
   - Link to existing project: No
   - Project name: mywebsite (or your preferred name)
   - Directory: ./
   - Override settings: No

5. **Add environment variable**
   ```bash
   vercel env add OPENAI_API_KEY
   ```
   Then paste your OpenAI API key when prompted.

6. **Deploy to production**
   ```bash
   vercel --prod
   ```

## Post-Deployment Steps

1. **Test your website**
   - Visit your Vercel URL
   - Test the chatbot by clicking the chat button
   - Ask a few questions like:
     - "What is Deepak's experience?"
     - "Tell me about his skills"
     - "Where did he study?"

2. **Configure custom domain (optional)**
   - In Vercel Dashboard → Your Project → Settings → Domains
   - Add your custom domain (e.g., deepakkv.com)
   - Follow DNS configuration instructions

3. **Monitor your deployment**
   - Check Vercel Dashboard → Your Project → Deployments
   - View logs: Click on a deployment → View Function Logs

## Troubleshooting

### Chatbot not responding
1. Check if OPENAI_API_KEY is set correctly in Vercel Environment Variables
2. View function logs in Vercel Dashboard
3. Make sure your OpenAI API key has credits

### API errors
1. Check Vercel Function Logs for detailed error messages
2. Verify the API endpoint is accessible at `/api/chat`
3. Test locally first with `python app.py`

### Build failures
1. Check that all files are committed to Git
2. Verify `vercel.json` is properly configured
3. Check Vercel build logs for specific errors

## Important Notes

1. **Serverless limitations**:
   - Vercel serverless functions have a 10-second timeout (hobby plan)
   - Conversation history is stored in-memory and resets between function invocations
   - For persistent conversation history, consider using a database (Redis, MongoDB, etc.)

2. **API Keys Security**:
   - Never commit `.env` file with actual keys
   - Always use Vercel Environment Variables
   - Rotate your API keys regularly

3. **Cost Management**:
   - Monitor OpenAI API usage at https://platform.openai.com/usage
   - Set usage limits in OpenAI dashboard to control costs
   - Vercel hobby plan is free with generous limits

## Updating Your Deployment

To update your website after making changes:

```bash
git add .
git commit -m "Your update message"
git push origin claude/create-website-showcase-011CUtbRqTKr19sgarXaQFU7
```

Vercel will automatically redeploy when you push to the connected branch.

## Getting Help

- Vercel Documentation: https://vercel.com/docs
- Vercel Support: https://vercel.com/support
- OpenAI Documentation: https://platform.openai.com/docs

## Your Deployment URLs

After deployment, you'll have:
- **Production URL**: `https://your-project.vercel.app`
- **Preview URLs**: Auto-generated for each commit
- **Custom Domain**: (optional) Your own domain

---

**Ready to deploy?** Follow the steps above and your website will be live in minutes!
