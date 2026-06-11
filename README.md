# 🚀 Supergit (슈퍼깃)

An easy-to-use, beautiful GUI application for Git and GitHub CLI operations.

## ✨ Features

- 📊 **Git Status Management** - View and manage staged/unstaged changes
- 🌿 **Branch Operations** - Create, checkout, and view branches with ease
- 📝 **Commit History** - Browse commit history with detailed information
- 🔀 **Pull Request Creation** - Easy PR creation using GitHub CLI (if installed)
- 🌐 **Multi-language Support** - Korean (한국어) and English
- 🎨 **Beautiful Dark Theme** - Easy on the eyes, built for developers

## 📋 Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Git
- GitHub CLI (optional, for PR features) - [Install gh](https://cli.github.com/)

## 🚀 Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd supergit
```

2. Install dependencies:
```bash
npm install
```

## 🏃‍♂️ Running the Application

### Development Mode

```bash
npm start
```

This will start both the React development server and Electron app.

### Build for Production

```bash
npm run build:electron
```

This creates distributable packages for your platform in the `dist` folder.

## 🎯 Usage

1. **Select Repository**: Click "Select Repository" to choose a Git repository
2. **Status Tab**: View and stage/unstage files, commit changes
3. **Branches Tab**: Create new branches, checkout existing branches
4. **Commits Tab**: Browse commit history and details
5. **Pull Requests Tab**: Create and view PRs (requires GitHub CLI)
6. **Settings Tab**: Change language and view app information

## 🛠️ Technology Stack

- **Electron** - Cross-platform desktop application framework
- **React** - UI library
- **simple-git** - Git operations in Node.js
- **GitHub CLI** - GitHub PR operations
- **i18next** - Internationalization

## 🌏 Supported Languages

- 🇰🇷 Korean (한국어)
- 🇺🇸 English

## 📝 License

MIT

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👨‍💻 Author

Supergit Team
