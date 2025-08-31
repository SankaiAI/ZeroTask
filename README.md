# ZeroTask

**A Privacy-First Daily Brief System for Gmail, Slack & GitHub**

ZeroTask is a local-first desktop/web application that aggregates your Gmail, Slack, and GitHub notifications into a single, action-ready daily brief. Built with privacy and security in mind, it runs entirely on your machine with shared service account architecture for company deployment.

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+ and pip
- **Git** for version control

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SankaiAI/ZeroTask.git
   cd ZeroTask
   ```

2. **Start the backend:**
   ```bash
   cd zerotask-backend
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   python -m app.main
   ```

3. **Start the frontend:**
   ```bash
   cd zerotask-frontend
   npm install
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3001 (or 3000 if available)
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Features

### Core Functionality
- **📧 Gmail Integration** - Read emails and create draft replies (OAuth 2.0)
- **💬 Slack Integration** - Individual user OAuth with profile display and API access
- **🔧 GitHub Integration** - Monitor assigned issues and PR reviews (Service Account)
- **🤖 AI-Powered Summarization** - Using local Ollama or BYOK LLM providers
- **🔗 Smart Deduplication** - Merge related items across platforms
- **⚡ Action-Ready Cards** - Open, reply, snooze, and follow-up actions

### Privacy & Security
- **🏠 Local-First Architecture** - All data stored locally
- **🔐 Encrypted Token Storage** - OAuth tokens and service credentials secured with AES-256
- **👤 Individual User Authentication** - Personal OAuth flows for Gmail and Slack
- **🏢 Company Deployment Ready** - IT-managed service accounts for GitHub
- **🔒 No Central Server** - Zero data sent to external services

### Recent Enhancements
- **👨‍💼 User Profile Display** - Show Slack user avatars, names, emails, and titles
- **🎯 Improved UX** - Removed intrusive alert popups, console logging for debugging
- **🔗 OAuth Callback Handling** - Seamless popup-based OAuth flows with automatic status updates
- **🛡️ Enhanced Security** - Proper token encryption and secure credential management

### Technical Stack
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **Backend:** FastAPI, SQLite, SQLAlchemy
- **LLM:** Ollama (local) or LiteLLM (BYOK)
- **Authentication:** Environment-based shared service accounts

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   SQLite        │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Port 3000)   │    │   (Port 8000)   │    │   (Local File)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │   External      │
         └──────────────┤   Services      │
                        │   • Gmail API   │
                        │   • Slack API   │
                        │   • GitHub API  │
                        └─────────────────┘
```

## 🛠️ IT Team Setup (Company Deployment)

For company internal deployment, IT teams configure shared service accounts:

### 1. GitHub Service Account
```bash
# Create service account: zerotask-bot@company.com
# Generate PAT with scopes: repo, read:user, notifications
export GITHUB_TOKEN=ghp_your_service_account_token
```

### 2. Slack OAuth Application
```bash
# Create Slack OAuth app for individual user authentication
# Configure OAuth scopes: channels:read, chat:write, users:read, users:read.email, channels:history, groups:read, im:read
export SLACK_CLIENT_ID=your_oauth_client_id
export SLACK_CLIENT_SECRET=your_oauth_client_secret
# Configure OAuth redirect URI: https://your-domain.com/oauth2/slack/callback
```

### 3. Gmail OAuth
```bash
# Configure Google Cloud OAuth 2.0 credentials
export GOOGLE_CLIENT_ID=your_oauth_client_id
export GOOGLE_CLIENT_SECRET=your_oauth_client_secret
# Configure OAuth redirect URI: http://localhost:8000/oauth2/callback
```

📋 **See [IT_SETUP.md](IT_SETUP.md) for detailed configuration instructions.**

## 🔧 Configuration

### Environment Variables

Copy and configure the environment file:

```bash
# Backend configuration
cd zerotask-backend
cp .env.example .env
# Edit .env with your service account credentials
```

### Key Configuration Options

- **LLM Provider**: Choose between Ollama (local) or BYOK providers
- **Polling Intervals**: Configure how often to check each service
- **Daily Brief Time**: Set when to generate daily summaries
- **Security Settings**: Configure encryption and authentication

## 📖 Documentation

- **[PRD.md](PRD.md)** - Complete Product Requirements Document
- **[IT_SETUP.md](IT_SETUP.md)** - IT team setup guide for service accounts
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[CLAUDE.md](CLAUDE.md)** - Development governance and contribution rules

## 🔌 API Endpoints

### Authentication
- `GET /api/v1/auth/validate` - Check all service configurations
- `GET /api/v1/auth/status/{provider}` - Get provider connection status
- `GET /api/v1/auth/github/test` - Test GitHub connection
- `GET /api/v1/auth/slack/oauth/status` - Get Slack OAuth status and user profile
- `GET /api/v1/auth/slack/oauth/start` - Start Slack OAuth flow
- `GET /api/v1/auth/gmail/status` - Check Gmail OAuth configuration
- `GET /api/v1/auth/gmail/oauth/start` - Start Gmail OAuth flow

### Health & Monitoring
- `GET /api/v1/health` - API health check
- `GET /` - Root endpoint with API information

## 🧪 Development

### Code Structure

```
ZeroTask/
├── zerotask-frontend/          # Next.js frontend
│   ├── src/components/         # React components
│   ├── src/app/               # App router pages
│   ├── src/lib/               # Utilities and helpers
│   └── public/                # Static files and OAuth callbacks
├── zerotask-backend/          # FastAPI backend
│   ├── app/api/               # API endpoints
│   ├── app/models/            # SQLAlchemy models
│   ├── app/services/          # Business logic (including OAuth services)
│   └── app/utils/             # Utilities and encryption
└── docs/                      # Documentation
```

### Development Commands

```bash
# Frontend development
cd zerotask-frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint

# Backend development
cd zerotask-backend
python -m app.main   # Start development server
pip install -r requirements.txt  # Install dependencies
```

### Testing

```bash
# Frontend testing
cd zerotask-frontend
npm test

# Backend testing
cd zerotask-backend
pytest
```

## 🚀 Deployment

### Production Deployment

1. **Configure environment variables** for production
2. **Build frontend application:**
   ```bash
   cd zerotask-frontend
   npm run build
   ```
3. **Start backend server:**
   ```bash
   cd zerotask-backend
   python -m app.main
   ```

### Docker Deployment (Future)

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Follow the governance rules** in [CLAUDE.md](CLAUDE.md)
4. **Ensure PRD compliance** for any scope changes
5. **Commit your changes:** `git commit -m 'Add amazing feature'`
6. **Push to the branch:** `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- **Follow the PRD** - All changes must comply with the Product Requirements Document
- **Update CHANGELOG.md** - Document all changes following Keep a Changelog format
- **Test thoroughly** - Ensure all features work across platforms
- **Security first** - Never commit secrets or compromise privacy-first architecture

## 📊 Milestones

### Milestone 1 ✅ (Completed)
- [x] Slack + GitHub integration
- [x] Shared service account architecture
- [x] Basic daily brief generation
- [x] IT setup documentation

### Milestone 2 ✅ (Completed)
- [x] Gmail OAuth integration
- [x] Slack individual user OAuth with profile display
- [x] Enhanced frontend with user profile avatars
- [x] Improved error handling and user experience

### Milestone 3 (Next)
- [ ] LLM summarization with Ollama
- [ ] Priority scoring algorithm
- [ ] Follow-up task management
- [ ] Advanced deduplication

### Milestone 4 (Future)
- [ ] Export to Markdown
- [ ] Background job scheduling
- [ ] Enhanced preferences UI
- [ ] Mobile responsiveness

## 🛡️ Security & Privacy

- **Local-first architecture** - No data leaves your machine
- **Encrypted credentials** - All tokens encrypted at rest
- **Minimal API scopes** - Only necessary permissions requested
- **No telemetry** - Optional opt-in only
- **Audit logging** - All actions logged locally

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/SankaiAI/ZeroTask/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SankaiAI/ZeroTask/discussions)
- **Documentation**: Check the `docs/` directory
- **IT Support**: Contact your organization's IT team for service account setup

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Claude Code** - AI-powered development assistant
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework for production
- **Ollama** - Local LLM deployment
- **Tailwind CSS** - Utility-first CSS framework

---

**Built with privacy in mind. Your data stays on your machine.**

*Generated with [Claude Code](https://claude.ai/code) - AI-powered development assistant*