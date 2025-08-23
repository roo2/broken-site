# BrokenSite - Frontend

A modern React frontend for the BrokenSite web application. Built with Vite, SCSS, and modern React patterns.

## Features

- 🎨 Modern, responsive UI design
- ⚡ Fast development with Vite
- 🎯 SCSS for styling with CSS variables
- 📱 Mobile-first responsive design
- 🔍 Real-time website diagnostics
- 🎨 Beautiful issue cards with severity indicators
- ⚡ Optimized for performance

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **SCSS** - Advanced CSS with variables and mixins
- **Lucide React** - Beautiful icons
- **ESLint** - Code quality and consistency

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend server running on port 8000

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Development

### Project Structure

```
frontend/
├── src/
│   ├── App.jsx          # Main application component
│   ├── App.scss         # Component styles
│   ├── main.jsx         # Application entry point
│   └── styles/
│       └── main.scss    # Global styles and variables
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies and scripts
```

### Styling

The project uses SCSS with CSS custom properties (variables) for theming:

- **Variables**: Defined in `src/styles/main.scss`
- **Component styles**: Co-located with components (e.g., `App.scss`)
- **Responsive design**: Mobile-first approach with breakpoints

### API Integration

The frontend communicates with the FastAPI backend through:

- **Proxy**: Configured in `vite.config.js` to forward `/api/*` to `localhost:8000`
- **Endpoints**: 
  - `POST /api/diagnose` - Submit website for diagnosis

### Key Components

- **DiagnosisForm**: URL input and submission
- **ResultsDisplay**: Shows diagnostic results and issues
- **IssueCard**: Individual issue display with severity indicators

## Customization

### Colors and Theming

Edit CSS variables in `src/styles/main.scss`:

```scss
:root {
  --primary-color: #3b82f6;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  // ... more variables
}
```

### Adding New Issue Types

1. Add new category to the `getCategoryIcon` function in `App.jsx`
2. Update the backend to return the new category
3. Add corresponding styles if needed

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style
2. Use SCSS for styling
3. Ensure responsive design works
4. Test with different screen sizes
5. Run linting before committing
