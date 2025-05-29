# Themes

Renardo supports multiple editor themes to match your visual preferences and reduce eye strain in different lighting conditions.

## Available Themes

The editor includes several built-in themes:

- **Dracula** - Dark theme with vibrant colors (default)
- **Monokai** - Dark theme with warm, colorful syntax highlighting
- **Material** - Modern, material design-inspired dark theme
- **Nord** - Cool, blue-tinted dark theme
- **Solarized Dark** - Dark theme with carefully chosen colors
- **Solarized Light** - Light theme with the Solarized color palette
- **Darcula** - Dark theme inspired by JetBrains IDEs
- **Eclipse** - Light theme inspired by the Eclipse IDE

## Changing Themes

To change the editor theme:

1. Locate the theme selector in the bottom status bar
2. Click to open the theme dropdown menu
3. Select your preferred theme
4. The theme will apply immediately

## Theme Components

Each theme affects multiple aspects of the editor:

- **Editor Background** - The main background color of the code area
- **Syntax Highlighting** - Colors for different code elements
- **UI Elements** - Controls, buttons, and panels
- **Console Colors** - The console background and text colors

## Console Color Adaptation

The console automatically adapts to match your selected theme:

- Console background and text colors coordinate with the editor theme
- Console header and footer elements match the theme's accent colors
- Message types (info, warning, error) maintain their semantic colors across themes

## Creating Custom Themes

While Renardo doesn't currently support custom theme creation through the UI, advanced users can:

1. Create custom CSS files in the public/themes directory
2. Follow the naming and structure of existing theme files
3. Restart the application to load custom themes

## Theme Persistence

Your theme selection is automatically saved to your browser's local storage and will persist between sessions.

## Recommended Themes for Different Scenarios

- **Long coding sessions**: Nord or Solarized Dark (reduced eye strain)
- **Live performances**: Dracula or Material (high contrast, vibrant colors)
- **Brightly lit environments**: Eclipse or Solarized Light
- **Team collaboration**: Dracula (default) for consistency