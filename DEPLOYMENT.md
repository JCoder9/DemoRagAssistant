# Deployment Guide

This guide covers deploying the RAG Assistant to various platforms.

## Prerequisites

- OpenAI API key
- Git repository access
- Platform account (Render, AWS, or Docker)

---

## Option 1: Deploy to Render (Recommended for Demo)

Render offers free hosting for demos and is the easiest deployment option.

### Backend Deployment

1. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```
   Name: rag-assistant-backend
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Add Environment Variables**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   EMBEDDING_MODEL=text-embedding-3-small
   CHAT_MODEL=gpt-3.5-turbo
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note the service URL (e.g., `https://rag-assistant-backend.onrender.com`)

### Frontend Deployment

1. **Create New Static Site**
   - Click "New +" → "Static Site"
   - Connect your GitHub repository

2. **Configure Site**
   ```
   Name: rag-assistant-frontend
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```

3. **Add Environment Variables**
   ```
   VITE_API_URL=https://rag-assistant-backend.onrender.com
   ```

4. **Deploy**
   - Click "Create Static Site"
   - Your app will be live at `https://rag-assistant-frontend.onrender.com`

### Notes: Free Tier Cold Starts
- **Backend sleeps after 15 minutes** of inactivity
- **First request takes 30-60 seconds** to wake up the server
- The app includes notifications to inform users about wake-up delays
- **User experience during cold start:**
  - Upload: Shows "Upload is taking longer than usual. Free-tier server may be waking up..." after 10 seconds
  - Query: Shows "First request may take 30-60 seconds as the free-tier server wakes up..."
  - Errors: Displays helpful timeout messages clarifying it's the free-tier with retry instructions
- **Upgrade to paid tier** ($7/month) for always-on, instant responses

### Recommended: Use Firebase/Netlify for Frontend
For better performance, deploy frontend to Firebase, Netlify, or Vercel (all have generous free tiers with global CDN and no sleep). Keep backend on Render for Python runtime.

---

## Option 2: Deploy with Docker

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed

### Local Development

1. **Create .env file in project root**
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

4. **Stop services**
   ```bash
   docker-compose down
   ```

### Backend Only (Docker)

```bash
cd backend
docker build -t rag-assistant-backend .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  rag-assistant-backend
```

### Frontend Only (Docker)

```bash
cd frontend
docker build -t rag-assistant-frontend .
docker run -p 5173:5173 rag-assistant-frontend
```

---

## Option 3: Deploy to AWS

### Backend (AWS Elastic Beanstalk)

1. **Install AWS CLI and EB CLI**
   ```bash
   pip install awscli awsebcli
   aws configure
   ```

2. **Initialize Elastic Beanstalk**
   ```bash
   cd backend
   eb init -p python-3.11 rag-assistant
   ```

3. **Create Environment**
   ```bash
   eb create rag-assistant-env
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv OPENAI_API_KEY=your_key_here
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

6. **Open Application**
   ```bash
   eb open
   ```

### Frontend (AWS S3 + CloudFront)

1. **Build Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://rag-assistant-frontend
   aws s3 website s3://rag-assistant-frontend --index-document index.html
   ```

3. **Upload Build**
   ```bash
   aws s3 sync dist/ s3://rag-assistant-frontend --acl public-read
   ```

4. **Configure CloudFront** (Optional, for HTTPS)
   - Create CloudFront distribution pointing to S3 bucket
   - Enable HTTPS with AWS Certificate Manager

### Notes
- AWS Free Tier covers first 12 months
- After free tier: ~$10-20/month for small apps
- Use AWS Cost Explorer to monitor spending

---

## Option 4: Deploy to VPS (DigitalOcean, Linode, etc.)

### Setup

1. **Create Droplet/VPS**
   - Ubuntu 22.04 LTS
   - Minimum: 1GB RAM, 1 CPU

2. **SSH into Server**
   ```bash
   ssh root@your_server_ip
   ```

3. **Install Dependencies**
   ```bash
   apt update
   apt install -y python3.11 python3-pip nodejs npm nginx
   ```

4. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/RagAssistant.git
   cd RagAssistant
   ```

5. **Setup Backend**
   ```bash
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create .env file
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

6. **Setup Frontend**
   ```bash
   cd ../frontend
   npm install
   npm run build
   ```

7. **Configure Nginx**
   ```nginx
   # /etc/nginx/sites-available/rag-assistant
   server {
       listen 80;
       server_name your_domain.com;

       # Frontend
       location / {
           root /root/RagAssistant/frontend/dist;
           try_files $uri $uri/ /index.html;
       }

       # Backend API
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

8. **Enable Site**
   ```bash
   ln -s /etc/nginx/sites-available/rag-assistant /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

9. **Setup Process Manager (PM2)**
   ```bash
   npm install -g pm2
   cd /root/RagAssistant/backend
   pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name rag-backend
   pm2 startup
   pm2 save
   ```

10. **Enable HTTPS** (Optional)
    ```bash
    apt install certbot python3-certbot-nginx
    certbot --nginx -d your_domain.com
    ```

---

## Production Considerations

### Performance
- **Vector Database**: Replace FAISS with Pinecone, Weaviate, or Qdrant for production
- **Caching**: Add Redis for session management and rate limiting
- **CDN**: Use CloudFlare or AWS CloudFront for static assets
- **Load Balancer**: Use AWS ALB or Nginx for multiple backend instances

### Security
- **HTTPS**: Always use SSL/TLS in production
- **CORS**: Configure proper CORS origins (don't use `*`)
- **Rate Limiting**: Implement per-user rate limiting with Redis
- **API Keys**: Rotate OpenAI API keys regularly
- **Secrets**: Use AWS Secrets Manager or HashiCorp Vault

### Monitoring
- **Logging**: Use CloudWatch, DataDog, or Sentry
- **Uptime**: Use UptimeRobot or Pingdom
- **Analytics**: Add Mixpanel or Google Analytics
- **Error Tracking**: Integrate Sentry for error monitoring

### Scalability
- **Horizontal Scaling**: Use container orchestration (Kubernetes, ECS)
- **Database**: PostgreSQL for user management and document metadata
- **Queue**: Add Celery + Redis for async document processing
- **Storage**: Use S3 for uploaded documents

### Cost Optimization
- **OpenAI**: Use GPT-3.5-turbo instead of GPT-4 (10x cheaper)
- **Embeddings**: Cache embeddings to avoid regenerating
- **Compute**: Use auto-scaling groups to scale down during low traffic
- **Storage**: Set S3 lifecycle policies for old documents

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker logs rag-assistant-backend

# Verify environment variables
echo $OPENAI_API_KEY

# Test uvicorn directly
cd backend
uvicorn app.main:app --reload
```

### Frontend can't connect to backend
- Check VITE_API_URL in .env
- Verify CORS settings in backend/app/main.py
- Check browser console for errors

### OpenAI API errors
- Verify API key is valid
- Check API quota and billing
- Ensure correct model names in settings

### FAISS index errors
- Delete storage/*.faiss and storage/*.pkl
- Restart backend to rebuild index
- Check file permissions on storage directory

---

## Support

For issues or questions:
- Check GitHub Issues
- Review FastAPI docs: https://fastapi.tiangolo.com
- OpenAI API docs: https://platform.openai.com/docs
