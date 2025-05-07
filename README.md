# Function Cloud (FC)

A Python library for easily deploying functions to Modal.com's cloud infrastructure.

## Security Notice

This library requires API keys and credentials to function properly. **NEVER** commit these directly to your code. Instead, use environment variables or a secure configuration file.

## Installation

```bash
pip install git+https://github.com/Saadmomin2903/WC.git
```

## Configuration

### Using Environment Variables (Recommended)

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual credentials:
   ```
   # Modal credentials
   MODAL_TOKEN_ID=your_modal_token_id
   MODAL_TOKEN_SECRET=your_modal_token_secret

   # Groq API key
   GROQ_API_KEY=your_groq_api_key

   # Google OAuth credentials (only needed for web interface)
   FC_GOOGLE_CLIENT_ID=your_google_client_id
   FC_GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

3. Load the environment variables in your code:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load environment variables from .env file

   from function_cloud import FC
   FC.configure()  # Will automatically use environment variables
   ```

### Using a Configuration File

1. Create a configuration file at `~/.function_cloud/config.json`:
   ```json
   {
     "modal_token_id": "your_modal_token_id",
     "modal_token_secret": "your_modal_token_secret",
     "groq_api_key": "your_groq_api_key"
   }
   ```

2. Set secure permissions:
   ```bash
   chmod 600 ~/.function_cloud/config.json
   ```

3. Use the configuration in your code:
   ```python
   from function_cloud import FC
   FC.configure()  # Will automatically load from config file
   ```

## Vercel Deployment

When deploying to Vercel, add your credentials as environment variables in the Vercel dashboard:

1. Go to your project settings
2. Navigate to the "Environment Variables" tab
3. Add the following environment variables:
   - `MODAL_TOKEN_ID`: Your Modal token ID
   - `MODAL_TOKEN_SECRET`: Your Modal token secret
   - `GROQ_API_KEY`: Your Groq API key
   - `FC_GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `FC_GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `FC_SECRET_KEY`: A random secret key for Flask sessions
   - `SUPABASE_URL`: Your Supabase URL (if using Supabase)
   - `SUPABASE_KEY`: Your Supabase key (if using Supabase)

## GitHub Actions Deployment

This repository includes a GitHub Actions workflow that automatically deploys to Vercel when you push to the main branch.

To set it up:

1. Go to your GitHub repository settings
2. Navigate to "Secrets and variables" > "Actions"
3. Add the following secrets:
   - `VERCEL_TOKEN`: Your Vercel API token
   - `MODAL_TOKEN_ID`: Your Modal token ID
   - `MODAL_TOKEN_SECRET`: Your Modal token secret
   - `GROQ_API_KEY`: Your Groq API key
   - `FC_GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `FC_GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `FC_SECRET_KEY`: A random secret key for Flask sessions
   - `SUPABASE_URL`: Your Supabase URL (if using Supabase)
   - `SUPABASE_KEY`: Your Supabase key (if using Supabase)

## Production Guide

For detailed information on deploying Function Cloud to production, see the [Production Guide](function_cloud_production_guide.md).
